{{
  config(
    materialized='table',
    description='Revenue forecasting model with multiple prediction methods and confidence intervals'
  )
}}

WITH historical_revenue AS (
  SELECT
    DATE_TRUNC('month', CloseDate) as month,
    DATE_TRUNC('quarter', CloseDate) as quarter,
    DATE_TRUNC('year', CloseDate) as year,
    
    -- Revenue metrics
    SUM(CASE WHEN IsWon = true THEN Amount ELSE 0 END) as won_revenue,
    SUM(CASE WHEN IsClosed = true AND IsWon = false THEN Amount ELSE 0 END) as lost_revenue,
    SUM(Amount) as total_pipeline_value,
    
    -- Opportunity metrics
    COUNT(*) as total_opportunities,
    COUNT(CASE WHEN IsWon = true THEN 1 END) as won_opportunities,
    COUNT(CASE WHEN IsClosed = true AND IsWon = false THEN 1 END) as lost_opportunities,
    
    -- Performance metrics
    AVG(Amount) as avg_deal_size,
    SUM(CASE WHEN IsWon = true THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) as win_rate,
    AVG(DATEDIFF('day', CreatedDate, CloseDate)) as avg_days_to_close
    
  FROM {{ ref('stg_sf__opportunity') }}
  WHERE Amount > 0 AND IsClosed = true
  GROUP BY 1, 2, 3
),

monthly_trends AS (
  SELECT
    month,
    won_revenue,
    total_pipeline_value,
    total_opportunities,
    won_opportunities,
    avg_deal_size,
    win_rate,
    avg_days_to_close,
    
    -- Rolling averages (3-month)
    AVG(won_revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as rolling_3m_revenue,
    AVG(win_rate) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as rolling_3m_win_rate,
    AVG(avg_deal_size) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as rolling_3m_deal_size,
    
    -- Growth rates
    LAG(won_revenue) OVER (ORDER BY month) as prev_month_revenue,
    won_revenue - LAG(won_revenue) OVER (ORDER BY month) as revenue_growth,
    (won_revenue - LAG(won_revenue) OVER (ORDER BY month)) / NULLIF(LAG(won_revenue) OVER (ORDER BY month), 0) as revenue_growth_rate,
    
    -- Seasonality indicators
    EXTRACT(MONTH FROM month) as month_of_year,
    EXTRACT(QUARTER FROM month) as quarter_of_year
    
  FROM historical_revenue
),

seasonal_patterns AS (
  SELECT
    month_of_year,
    quarter_of_year,
    AVG(won_revenue) as avg_monthly_revenue,
    AVG(win_rate) as avg_monthly_win_rate,
    AVG(avg_deal_size) as avg_monthly_deal_size,
    STDDEV(won_revenue) as revenue_volatility,
    COUNT(*) as months_count
    
  FROM monthly_trends
  GROUP BY 1, 2
),

current_pipeline AS (
  SELECT
    DATE_TRUNC('month', CloseDate) as forecast_month,
    SUM(Amount) as open_pipeline_value,
    COUNT(*) as open_opportunities,
    AVG(Amount) as avg_open_deal_size,
    
    -- Pipeline by stage
    SUM(CASE WHEN StageName = 'Prospecting' THEN Amount ELSE 0 END) as prospecting_value,
    SUM(CASE WHEN StageName = 'Qualification' THEN Amount ELSE 0 END) as qualification_value,
    SUM(CASE WHEN StageName = 'Proposal/Price Quote' THEN Amount ELSE 0 END) as proposal_value,
    SUM(CASE WHEN StageName = 'Negotiation/Review' THEN Amount ELSE 0 END) as negotiation_value,
    
    -- Probability-weighted pipeline
    SUM(CASE 
      WHEN StageName = 'Prospecting' THEN Amount * 0.1
      WHEN StageName = 'Qualification' THEN Amount * 0.25
      WHEN StageName = 'Proposal/Price Quote' THEN Amount * 0.5
      WHEN StageName = 'Negotiation/Review' THEN Amount * 0.75
      ELSE Amount * 0.1
    END) as probability_weighted_pipeline
    
  FROM {{ ref('stg_sf__opportunity') }}
  WHERE Amount > 0 AND IsClosed = false
  GROUP BY 1
),

forecast_models AS (
  SELECT
    m.month,
    m.won_revenue,
    m.rolling_3m_revenue,
    m.rolling_3m_win_rate,
    m.rolling_3m_deal_size,
    m.revenue_growth_rate,
    
    -- Model 1: Simple trend projection
    m.won_revenue * (1 + COALESCE(m.revenue_growth_rate, 0)) as trend_forecast,
    
    -- Model 2: Rolling average projection
    m.rolling_3m_revenue as rolling_avg_forecast,
    
    -- Model 3: Seasonal adjustment
    s.avg_monthly_revenue as seasonal_forecast,
    
    -- Model 4: Pipeline-based forecast
    COALESCE(p.probability_weighted_pipeline, 0) as pipeline_forecast,
    
    -- Model 5: Combined forecast (weighted average)
    (
      COALESCE(m.won_revenue * (1 + COALESCE(m.revenue_growth_rate, 0)), 0) * 0.3 +
      COALESCE(m.rolling_3m_revenue, 0) * 0.3 +
      COALESCE(s.avg_monthly_revenue, 0) * 0.2 +
      COALESCE(p.probability_weighted_pipeline, 0) * 0.2
    ) as combined_forecast,
    
    -- Confidence intervals
    s.revenue_volatility,
    s.revenue_volatility * 1.96 as confidence_interval_95,
    s.revenue_volatility * 2.58 as confidence_interval_99
    
  FROM monthly_trends m
  LEFT JOIN seasonal_patterns s ON m.month_of_year = s.month_of_year
  LEFT JOIN current_pipeline p ON m.month = p.forecast_month
),

forecast_accuracy AS (
  SELECT
    month,
    won_revenue as actual_revenue,
    trend_forecast,
    rolling_avg_forecast,
    seasonal_forecast,
    pipeline_forecast,
    combined_forecast,
    
    -- Forecast accuracy metrics
    ABS(won_revenue - trend_forecast) / NULLIF(won_revenue, 0) as trend_mape,
    ABS(won_revenue - rolling_avg_forecast) / NULLIF(won_revenue, 0) as rolling_mape,
    ABS(won_revenue - seasonal_forecast) / NULLIF(won_revenue, 0) as seasonal_mape,
    ABS(won_revenue - pipeline_forecast) / NULLIF(won_revenue, 0) as pipeline_mape,
    ABS(won_revenue - combined_forecast) / NULLIF(won_revenue, 0) as combined_mape,
    
    -- Best performing model
    CASE 
      WHEN ABS(won_revenue - trend_forecast) <= ABS(won_revenue - rolling_avg_forecast) 
       AND ABS(won_revenue - trend_forecast) <= ABS(won_revenue - seasonal_forecast)
       AND ABS(won_revenue - trend_forecast) <= ABS(won_revenue - pipeline_forecast)
       AND ABS(won_revenue - trend_forecast) <= ABS(won_revenue - combined_forecast)
      THEN 'trend'
      WHEN ABS(won_revenue - rolling_avg_forecast) <= ABS(won_revenue - seasonal_forecast)
       AND ABS(won_revenue - rolling_avg_forecast) <= ABS(won_revenue - pipeline_forecast)
       AND ABS(won_revenue - rolling_avg_forecast) <= ABS(won_revenue - combined_forecast)
      THEN 'rolling_avg'
      WHEN ABS(won_revenue - seasonal_forecast) <= ABS(won_revenue - pipeline_forecast)
       AND ABS(won_revenue - seasonal_forecast) <= ABS(won_revenue - combined_forecast)
      THEN 'seasonal'
      WHEN ABS(won_revenue - pipeline_forecast) <= ABS(won_revenue - combined_forecast)
      THEN 'pipeline'
      ELSE 'combined'
    END as best_model
    
  FROM forecast_models
  WHERE won_revenue > 0
)

SELECT
  -- Time dimensions
  month,
  DATE_FORMAT(month, 'YYYY-MM') as month_label,
  EXTRACT(YEAR FROM month) as year,
  EXTRACT(MONTH FROM month) as month_number,
  EXTRACT(QUARTER FROM month) as quarter,
  
  -- Actual metrics
  actual_revenue,
  
  -- Forecast models
  trend_forecast,
  rolling_avg_forecast,
  seasonal_forecast,
  pipeline_forecast,
  combined_forecast,
  
  -- Confidence intervals
  combined_forecast - confidence_interval_95 as forecast_lower_95,
  combined_forecast + confidence_interval_95 as forecast_upper_95,
  combined_forecast - confidence_interval_99 as forecast_lower_99,
  combined_forecast + confidence_interval_99 as forecast_upper_99,
  
  -- Accuracy metrics
  trend_mape,
  rolling_mape,
  seasonal_mape,
  pipeline_mape,
  combined_mape,
  
  -- Model selection
  best_model,
  
  -- Forecast quality indicators
  CASE 
    WHEN combined_mape <= 0.1 THEN 'Excellent'
    WHEN combined_mape <= 0.2 THEN 'Good'
    WHEN combined_mape <= 0.3 THEN 'Fair'
    ELSE 'Poor'
  END as forecast_quality,
  
  -- Risk assessment
  CASE 
    WHEN confidence_interval_95 / NULLIF(combined_forecast, 0) > 0.5 THEN 'High Risk'
    WHEN confidence_interval_95 / NULLIF(combined_forecast, 0) > 0.3 THEN 'Medium Risk'
    ELSE 'Low Risk'
  END as forecast_risk,
  
  -- Timestamps
  CURRENT_TIMESTAMP as created_at,
  CURRENT_TIMESTAMP as updated_at

FROM forecast_accuracy
ORDER BY month DESC

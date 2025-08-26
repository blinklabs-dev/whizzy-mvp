{{
  config(
    materialized='table',
    description='Executive dashboard with key performance indicators and strategic insights'
  )
}}

WITH current_period AS (
  SELECT
    DATE_TRUNC('quarter', CURRENT_DATE) as current_quarter,
    DATE_TRUNC('month', CURRENT_DATE) as current_month,
    DATE_TRUNC('year', CURRENT_DATE) as current_year
),

pipeline_summary AS (
  SELECT
    -- Current pipeline
    SUM(CASE WHEN IsClosed = false THEN Amount ELSE 0 END) as current_pipeline_value,
    COUNT(CASE WHEN IsClosed = false THEN 1 END) as current_pipeline_count,
    
    -- Won this quarter
    SUM(CASE WHEN IsWon = true AND DATE_TRUNC('quarter', CloseDate) = (SELECT current_quarter FROM current_period) THEN Amount ELSE 0 END) as qtd_won_revenue,
    COUNT(CASE WHEN IsWon = true AND DATE_TRUNC('quarter', CloseDate) = (SELECT current_quarter FROM current_period) THEN 1 END) as qtd_won_count,
    
    -- Won this month
    SUM(CASE WHEN IsWon = true AND DATE_TRUNC('month', CloseDate) = (SELECT current_month FROM current_period) THEN Amount ELSE 0 END) as mtd_won_revenue,
    COUNT(CASE WHEN IsWon = true AND DATE_TRUNC('month', CloseDate) = (SELECT current_month FROM current_period) THEN 1 END) as mtd_won_count,
    
    -- Won this year
    SUM(CASE WHEN IsWon = true AND DATE_TRUNC('year', CloseDate) = (SELECT current_year FROM current_period) THEN Amount ELSE 0 END) as ytd_won_revenue,
    COUNT(CASE WHEN IsWon = true AND DATE_TRUNC('year', CloseDate) = (SELECT current_year FROM current_period) THEN 1 END) as ytd_won_count,
    
    -- Lost this quarter
    SUM(CASE WHEN IsClosed = true AND IsWon = false AND DATE_TRUNC('quarter', CloseDate) = (SELECT current_quarter FROM current_period) THEN Amount ELSE 0 END) as qtd_lost_revenue,
    COUNT(CASE WHEN IsClosed = true AND IsWon = false AND DATE_TRUNC('quarter', CloseDate) = (SELECT current_quarter FROM current_period) THEN 1 END) as qtd_lost_count,
    
    -- Overall win rate
    SUM(CASE WHEN IsWon = true THEN 1 ELSE 0 END) / NULLIF(SUM(CASE WHEN IsClosed = true THEN 1 ELSE 0 END), 0) as overall_win_rate,
    
    -- Average deal size
    AVG(Amount) as avg_deal_size,
    
    -- Average days to close
    AVG(DATEDIFF('day', CreatedDate, CloseDate)) as avg_days_to_close
    
  FROM {{ ref('stg_sf__opportunity') }}
  WHERE Amount > 0
),

stage_breakdown AS (
  SELECT
    StageName,
    COUNT(*) as opportunity_count,
    SUM(Amount) as total_value,
    AVG(Amount) as avg_value,
    
    -- Stage conversion rates
    SUM(CASE WHEN IsWon = true THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) as win_rate,
    SUM(CASE WHEN IsClosed = true THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) as close_rate,
    
    -- Time in stage
    AVG(DATEDIFF('day', CreatedDate, CloseDate)) as avg_days_in_stage
    
  FROM {{ ref('stg_sf__opportunity') }}
  WHERE Amount > 0
  GROUP BY 1
),

owner_performance AS (
  SELECT
    u.Name as owner_name,
    COUNT(DISTINCT o.Id) as total_opportunities,
    SUM(o.Amount) as total_pipeline_value,
    SUM(CASE WHEN o.IsWon = true THEN o.Amount ELSE 0 END) as won_revenue,
    SUM(CASE WHEN o.IsWon = true THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) as win_rate,
    AVG(o.Amount) as avg_deal_size,
    AVG(DATEDIFF('day', o.CreatedDate, o.CloseDate)) as avg_days_to_close
    
  FROM {{ ref('stg_sf__opportunity') }} o
  LEFT JOIN {{ ref('stg_sf__user') }} u ON o.OwnerId = u.Id
  WHERE o.Amount > 0
  GROUP BY 1
),

quarterly_comparison AS (
  SELECT
    DATE_TRUNC('quarter', CloseDate) as quarter,
    SUM(CASE WHEN IsWon = true THEN Amount ELSE 0 END) as won_revenue,
    COUNT(CASE WHEN IsWon = true THEN 1 END) as won_count,
    SUM(CASE WHEN IsClosed = true AND IsWon = false THEN Amount ELSE 0 END) as lost_revenue,
    COUNT(CASE WHEN IsClosed = true AND IsWon = false THEN 1 END) as lost_count,
    SUM(Amount) as total_pipeline_value,
    COUNT(*) as total_opportunities,
    AVG(Amount) as avg_deal_size,
    SUM(CASE WHEN IsWon = true THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) as win_rate
    
  FROM {{ ref('stg_sf__opportunity') }}
  WHERE Amount > 0 AND IsClosed = true
  GROUP BY 1
),

risk_analysis AS (
  SELECT
    -- Overdue opportunities
    COUNT(CASE WHEN CloseDate < CURRENT_DATE AND IsClosed = false THEN 1 END) as overdue_count,
    SUM(CASE WHEN CloseDate < CURRENT_DATE AND IsClosed = false THEN Amount ELSE 0 END) as overdue_value,
    
    -- High-value opportunities at risk
    COUNT(CASE WHEN Amount > 100000 AND IsClosed = false THEN 1 END) as high_value_count,
    SUM(CASE WHEN Amount > 100000 AND IsClosed = false THEN Amount ELSE 0 END) as high_value_amount,
    
    -- Opportunities closing this month
    COUNT(CASE WHEN DATE_TRUNC('month', CloseDate) = DATE_TRUNC('month', CURRENT_DATE) AND IsClosed = false THEN 1 END) as closing_this_month_count,
    SUM(CASE WHEN DATE_TRUNC('month', CloseDate) = DATE_TRUNC('month', CURRENT_DATE) AND IsClosed = false THEN Amount ELSE 0 END) as closing_this_month_value
    
  FROM {{ ref('stg_sf__opportunity') }}
  WHERE Amount > 0
),

forecast_insights AS (
  SELECT
    -- Pipeline coverage ratio
    current_pipeline_value / NULLIF(qtd_won_revenue * 4, 0) as pipeline_coverage_ratio,
    
    -- Win rate trend (last 3 quarters)
    (SELECT AVG(win_rate) FROM quarterly_comparison ORDER BY quarter DESC LIMIT 3) as recent_win_rate_trend,
    
    -- Deal size trend
    (SELECT AVG(avg_deal_size) FROM quarterly_comparison ORDER BY quarter DESC LIMIT 3) as recent_deal_size_trend,
    
    -- Velocity trend
    (SELECT AVG(avg_days_to_close) FROM pipeline_summary) as current_velocity
    
  FROM pipeline_summary
),

kpi_summary AS (
  SELECT
    -- Revenue KPIs
    qtd_won_revenue,
    mtd_won_revenue,
    ytd_won_revenue,
    current_pipeline_value,
    
    -- Performance KPIs
    overall_win_rate,
    avg_deal_size,
    avg_days_to_close,
    
    -- Pipeline KPIs
    current_pipeline_count,
    qtd_won_count,
    mtd_won_count,
    ytd_won_count,
    
    -- Risk KPIs
    overdue_value,
    high_value_amount,
    closing_this_month_value,
    
    -- Forecast KPIs
    pipeline_coverage_ratio,
    recent_win_rate_trend,
    recent_deal_size_trend,
    current_velocity,
    
    -- Calculated KPIs
    CASE 
      WHEN pipeline_coverage_ratio >= 3 THEN 'Excellent'
      WHEN pipeline_coverage_ratio >= 2 THEN 'Good'
      WHEN pipeline_coverage_ratio >= 1.5 THEN 'Fair'
      ELSE 'Poor'
    END as pipeline_health,
    
    CASE 
      WHEN overall_win_rate >= 0.3 THEN 'Excellent'
      WHEN overall_win_rate >= 0.2 THEN 'Good'
      WHEN overall_win_rate >= 0.15 THEN 'Fair'
      ELSE 'Poor'
    END as win_rate_health,
    
    CASE 
      WHEN avg_days_to_close <= 30 THEN 'Excellent'
      WHEN avg_days_to_close <= 60 THEN 'Good'
      WHEN avg_days_to_close <= 90 THEN 'Fair'
      ELSE 'Poor'
    END as velocity_health
    
  FROM pipeline_summary
  CROSS JOIN risk_analysis
  CROSS JOIN forecast_insights
)

SELECT
  -- Executive Summary
  'executive_dashboard' as dashboard_type,
  CURRENT_DATE as report_date,
  
  -- Revenue Summary
  qtd_won_revenue,
  mtd_won_revenue,
  ytd_won_revenue,
  current_pipeline_value,
  
  -- Performance Metrics
  overall_win_rate,
  avg_deal_size,
  avg_days_to_close,
  
  -- Pipeline Metrics
  current_pipeline_count,
  qtd_won_count,
  mtd_won_count,
  ytd_won_count,
  
  -- Risk Metrics
  overdue_value,
  high_value_amount,
  closing_this_month_value,
  
  -- Forecast Metrics
  pipeline_coverage_ratio,
  recent_win_rate_trend,
  recent_deal_size_trend,
  current_velocity,
  
  -- Health Indicators
  pipeline_health,
  win_rate_health,
  velocity_health,
  
  -- Overall Health Score
  CASE 
    WHEN pipeline_health = 'Excellent' AND win_rate_health = 'Excellent' AND velocity_health = 'Excellent' THEN 100
    WHEN pipeline_health = 'Good' AND win_rate_health = 'Good' AND velocity_health = 'Good' THEN 80
    WHEN pipeline_health = 'Fair' AND win_rate_health = 'Fair' AND velocity_health = 'Fair' THEN 60
    ELSE 40
  END as overall_health_score,
  
  -- Key Insights
  CASE 
    WHEN pipeline_coverage_ratio < 1.5 THEN 'Pipeline coverage is below target. Focus on lead generation.'
    WHEN overall_win_rate < 0.15 THEN 'Win rate is declining. Review sales process and qualification criteria.'
    WHEN avg_days_to_close > 90 THEN 'Deal velocity is slow. Identify and address bottlenecks.'
    WHEN overdue_value > current_pipeline_value * 0.2 THEN 'High overdue pipeline. Prioritize deal closure.'
    ELSE 'Pipeline is healthy. Maintain current performance.'
  END as key_insight,
  
  -- Recommendations
  CASE 
    WHEN pipeline_coverage_ratio < 1.5 THEN 'Increase prospecting activities and lead generation efforts.'
    WHEN overall_win_rate < 0.15 THEN 'Review and improve sales qualification process.'
    WHEN avg_days_to_close > 90 THEN 'Implement deal acceleration programs and remove process bottlenecks.'
    WHEN overdue_value > current_pipeline_value * 0.2 THEN 'Focus on closing overdue deals and improving forecasting accuracy.'
    ELSE 'Continue current strategies and monitor performance trends.'
  END as recommendation,
  
  -- Timestamps
  CURRENT_TIMESTAMP as created_at,
  CURRENT_TIMESTAMP as updated_at

FROM kpi_summary

{{
  config(
    materialized='table',
    description='Comprehensive pipeline health analysis with key metrics and trends'
  )
}}

WITH pipeline_metrics AS (
  SELECT
    -- Date dimensions
    DATE_TRUNC('month', CloseDate) as month,
    DATE_TRUNC('quarter', CloseDate) as quarter,
    DATE_TRUNC('year', CloseDate) as year,
    
    -- Pipeline metrics
    StageName,
    COUNT(*) as opportunity_count,
    SUM(Amount) as total_amount,
    AVG(Amount) as avg_amount,
    
    -- Win/Loss metrics
    SUM(CASE WHEN IsWon = true THEN 1 ELSE 0 END) as won_count,
    SUM(CASE WHEN IsWon = true THEN Amount ELSE 0 END) as won_amount,
    SUM(CASE WHEN IsClosed = true AND IsWon = false THEN 1 ELSE 0 END) as lost_count,
    SUM(CASE WHEN IsClosed = true AND IsWon = false THEN Amount ELSE 0 END) as lost_amount,
    
    -- Open pipeline
    SUM(CASE WHEN IsClosed = false THEN 1 ELSE 0 END) as open_count,
    SUM(CASE WHEN IsClosed = false THEN Amount ELSE 0 END) as open_amount,
    
    -- Velocity metrics
    AVG(DATEDIFF('day', CreatedDate, CloseDate)) as avg_days_to_close,
    
    -- Risk metrics
    SUM(CASE WHEN CloseDate < CURRENT_DATE AND IsClosed = false THEN 1 ELSE 0 END) as overdue_count,
    SUM(CASE WHEN CloseDate < CURRENT_DATE AND IsClosed = false THEN Amount ELSE 0 END) as overdue_amount
    
  FROM {{ ref('stg_sf__opportunity') }}
  WHERE Amount > 0  -- Filter out zero-amount opportunities
  GROUP BY 1, 2, 3, 4
),

stage_velocity AS (
  SELECT
    StageName,
    AVG(DATEDIFF('day', CreatedDate, CloseDate)) as avg_days_in_stage,
    COUNT(*) as opportunities_passed_through,
    SUM(Amount) as total_value_passed_through
  FROM {{ ref('stg_sf__opportunity') }}
  WHERE IsClosed = true
  GROUP BY 1
),

quarterly_trends AS (
  SELECT
    quarter,
    SUM(opportunity_count) as total_opportunities,
    SUM(total_amount) as total_pipeline_value,
    SUM(won_amount) as total_won_value,
    SUM(open_amount) as current_open_pipeline,
    AVG(avg_amount) as avg_opportunity_size,
    SUM(won_count) / NULLIF(SUM(won_count + lost_count), 0) as win_rate,
    SUM(overdue_amount) as overdue_pipeline_value
  FROM pipeline_metrics
  GROUP BY 1
),

pipeline_health_score AS (
  SELECT
    quarter,
    total_opportunities,
    total_pipeline_value,
    total_won_value,
    current_open_pipeline,
    avg_opportunity_size,
    win_rate,
    overdue_pipeline_value,
    
    -- Health score calculation (0-100)
    CASE 
      WHEN win_rate >= 0.3 THEN 25
      WHEN win_rate >= 0.2 THEN 20
      WHEN win_rate >= 0.1 THEN 15
      ELSE 10
    END +
    CASE 
      WHEN overdue_pipeline_value / NULLIF(current_open_pipeline, 0) <= 0.1 THEN 25
      WHEN overdue_pipeline_value / NULLIF(current_open_pipeline, 0) <= 0.2 THEN 20
      WHEN overdue_pipeline_value / NULLIF(current_open_pipeline, 0) <= 0.3 THEN 15
      ELSE 10
    END +
    CASE 
      WHEN avg_opportunity_size >= 100000 THEN 25
      WHEN avg_opportunity_size >= 50000 THEN 20
      WHEN avg_opportunity_size >= 25000 THEN 15
      ELSE 10
    END +
    CASE 
      WHEN total_opportunities >= 100 THEN 25
      WHEN total_opportunities >= 50 THEN 20
      WHEN total_opportunities >= 25 THEN 15
      ELSE 10
    END as pipeline_health_score
    
  FROM quarterly_trends
)

SELECT
  -- Quarter info
  quarter,
  DATE_FORMAT(quarter, 'YYYY-Q%Q') as quarter_label,
  
  -- Pipeline metrics
  total_opportunities,
  total_pipeline_value,
  total_won_value,
  current_open_pipeline,
  avg_opportunity_size,
  
  -- Performance metrics
  win_rate,
  overdue_pipeline_value,
  pipeline_health_score,
  
  -- Health indicators
  CASE 
    WHEN pipeline_health_score >= 80 THEN 'Excellent'
    WHEN pipeline_health_score >= 60 THEN 'Good'
    WHEN pipeline_health_score >= 40 THEN 'Fair'
    ELSE 'Poor'
  END as health_status,
  
  -- Risk indicators
  CASE 
    WHEN overdue_pipeline_value / NULLIF(current_open_pipeline, 0) > 0.3 THEN 'High Risk'
    WHEN overdue_pipeline_value / NULLIF(current_open_pipeline, 0) > 0.2 THEN 'Medium Risk'
    ELSE 'Low Risk'
  END as risk_level,
  
  -- Trend indicators
  LAG(total_pipeline_value) OVER (ORDER BY quarter) as prev_quarter_pipeline,
  LAG(win_rate) OVER (ORDER BY quarter) as prev_quarter_win_rate,
  
  -- Calculated fields
  total_pipeline_value - LAG(total_pipeline_value) OVER (ORDER BY quarter) as pipeline_growth,
  win_rate - LAG(win_rate) OVER (ORDER BY quarter) as win_rate_change,
  
  -- Timestamps
  CURRENT_TIMESTAMP as created_at,
  CURRENT_TIMESTAMP as updated_at

FROM pipeline_health_score
ORDER BY quarter DESC

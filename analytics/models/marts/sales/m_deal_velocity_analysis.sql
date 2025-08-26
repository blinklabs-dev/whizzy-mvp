{{
  config(
    materialized='table',
    description='Deal velocity analysis - tracking how quickly opportunities move through pipeline stages'
  )
}}

WITH opportunity_stages AS (
  SELECT
    Id as opportunity_id,
    Name as opportunity_name,
    StageName,
    Amount,
    CreatedDate,
    CloseDate,
    IsClosed,
    IsWon,
    OwnerId,
    AccountId,
    
    -- Stage progression tracking
    ROW_NUMBER() OVER (PARTITION BY Id ORDER BY CreatedDate) as stage_sequence,
    
    -- Time in each stage
    DATEDIFF('day', CreatedDate, CloseDate) as days_in_stage,
    
    -- Stage categories
    CASE 
      WHEN StageName IN ('Prospecting', 'Qualification') THEN 'Early Stage'
      WHEN StageName IN ('Proposal/Price Quote', 'Negotiation/Review') THEN 'Mid Stage'
      WHEN StageName IN ('Closed Won', 'Closed Lost') THEN 'Final Stage'
      ELSE 'Other'
    END as stage_category
    
  FROM {{ ref('stg_sf__opportunity') }}
  WHERE Amount > 0
),

stage_velocity_metrics AS (
  SELECT
    StageName,
    stage_category,
    COUNT(*) as opportunities_count,
    SUM(Amount) as total_value,
    AVG(Amount) as avg_deal_size,
    AVG(days_in_stage) as avg_days_in_stage,
    MEDIAN(days_in_stage) as median_days_in_stage,
    STDDEV(days_in_stage) as stddev_days_in_stage,
    
    -- Velocity metrics
    SUM(Amount) / NULLIF(AVG(days_in_stage), 0) as value_per_day,
    COUNT(*) / NULLIF(AVG(days_in_stage), 0) as deals_per_day,
    
    -- Win rate by stage
    SUM(CASE WHEN IsWon = true THEN 1 ELSE 0 END) as won_count,
    SUM(CASE WHEN IsWon = true THEN Amount ELSE 0 END) as won_amount,
    SUM(CASE WHEN IsClosed = true AND IsWon = false THEN 1 ELSE 0 END) as lost_count,
    SUM(CASE WHEN IsClosed = true AND IsWon = false THEN Amount ELSE 0 END) as lost_amount,
    
    -- Conversion rates
    SUM(CASE WHEN IsWon = true THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) as win_rate,
    SUM(CASE WHEN IsClosed = true THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) as close_rate
    
  FROM opportunity_stages
  GROUP BY 1, 2
),

owner_velocity AS (
  SELECT
    o.OwnerId,
    u.Name as owner_name,
    COUNT(DISTINCT o.Id) as total_opportunities,
    SUM(o.Amount) as total_pipeline_value,
    AVG(o.Amount) as avg_deal_size,
    AVG(DATEDIFF('day', o.CreatedDate, o.CloseDate)) as avg_days_to_close,
    
    -- Owner performance metrics
    SUM(CASE WHEN o.IsWon = true THEN 1 ELSE 0 END) as won_opportunities,
    SUM(CASE WHEN o.IsWon = true THEN o.Amount ELSE 0 END) as won_amount,
    SUM(CASE WHEN o.IsWon = true THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) as win_rate,
    
    -- Velocity by owner
    SUM(o.Amount) / NULLIF(AVG(DATEDIFF('day', o.CreatedDate, o.CloseDate)), 0) as value_velocity,
    COUNT(*) / NULLIF(AVG(DATEDIFF('day', o.CreatedDate, o.CloseDate)), 0) as deal_velocity
    
  FROM {{ ref('stg_sf__opportunity') }} o
  LEFT JOIN {{ ref('stg_sf__user') }} u ON o.OwnerId = u.Id
  WHERE o.Amount > 0 AND o.IsClosed = true
  GROUP BY 1, 2
),

quarterly_velocity_trends AS (
  SELECT
    DATE_TRUNC('quarter', CloseDate) as quarter,
    StageName,
    COUNT(*) as opportunities_count,
    SUM(Amount) as total_value,
    AVG(DATEDIFF('day', CreatedDate, CloseDate)) as avg_days_in_stage,
    
    -- Quarter-over-quarter changes
    LAG(COUNT(*)) OVER (PARTITION BY StageName ORDER BY DATE_TRUNC('quarter', CloseDate)) as prev_quarter_count,
    LAG(SUM(Amount)) OVER (PARTITION BY StageName ORDER BY DATE_TRUNC('quarter', CloseDate)) as prev_quarter_value,
    LAG(AVG(DATEDIFF('day', CreatedDate, CloseDate))) OVER (PARTITION BY StageName ORDER BY DATE_TRUNC('quarter', CloseDate)) as prev_quarter_days,
    
    -- Velocity changes
    COUNT(*) - LAG(COUNT(*)) OVER (PARTITION BY StageName ORDER BY DATE_TRUNC('quarter', CloseDate)) as count_change,
    SUM(Amount) - LAG(SUM(Amount)) OVER (PARTITION BY StageName ORDER BY DATE_TRUNC('quarter', CloseDate)) as value_change,
    AVG(DATEDIFF('day', CreatedDate, CloseDate)) - LAG(AVG(DATEDIFF('day', CreatedDate, CloseDate))) OVER (PARTITION BY StageName ORDER BY DATE_TRUNC('quarter', CloseDate)) as days_change
    
  FROM {{ ref('stg_sf__opportunity') }}
  WHERE Amount > 0 AND IsClosed = true
  GROUP BY 1, 2
),

bottleneck_analysis AS (
  SELECT
    StageName,
    avg_days_in_stage,
    opportunities_count,
    total_value,
    
    -- Bottleneck identification
    CASE 
      WHEN avg_days_in_stage > 30 THEN 'High Bottleneck'
      WHEN avg_days_in_stage > 15 THEN 'Medium Bottleneck'
      WHEN avg_days_in_stage > 7 THEN 'Low Bottleneck'
      ELSE 'No Bottleneck'
    END as bottleneck_level,
    
    -- Impact assessment
    total_value * (avg_days_in_stage / 30) as monthly_value_impact,
    opportunities_count * (avg_days_in_stage / 30) as monthly_deal_impact
    
  FROM stage_velocity_metrics
  WHERE avg_days_in_stage > 0
)

SELECT
  -- Stage velocity summary
  'stage_velocity' as metric_type,
  StageName as dimension,
  opportunities_count,
  total_value,
  avg_deal_size,
  avg_days_in_stage,
  median_days_in_stage,
  stddev_days_in_stage,
  value_per_day,
  deals_per_day,
  win_rate,
  close_rate,
  bottleneck_level,
  monthly_value_impact,
  monthly_deal_impact,
  CURRENT_TIMESTAMP as created_at

FROM stage_velocity_metrics
LEFT JOIN bottleneck_analysis USING (StageName)

UNION ALL

SELECT
  -- Owner velocity summary
  'owner_velocity' as metric_type,
  owner_name as dimension,
  total_opportunities as opportunities_count,
  total_pipeline_value as total_value,
  avg_deal_size,
  avg_days_to_close as avg_days_in_stage,
  NULL as median_days_in_stage,
  NULL as stddev_days_in_stage,
  value_velocity as value_per_day,
  deal_velocity as deals_per_day,
  win_rate,
  NULL as close_rate,
  NULL as bottleneck_level,
  NULL as monthly_value_impact,
  NULL as monthly_deal_impact,
  CURRENT_TIMESTAMP as created_at

FROM owner_velocity

UNION ALL

SELECT
  -- Quarterly trends
  'quarterly_trends' as metric_type,
  StageName as dimension,
  opportunities_count,
  total_value,
  NULL as avg_deal_size,
  avg_days_in_stage,
  NULL as median_days_in_stage,
  NULL as stddev_days_in_stage,
  NULL as value_per_day,
  NULL as deals_per_day,
  NULL as win_rate,
  NULL as close_rate,
  NULL as bottleneck_level,
  NULL as monthly_value_impact,
  NULL as monthly_deal_impact,
  CURRENT_TIMESTAMP as created_at

FROM quarterly_velocity_trends

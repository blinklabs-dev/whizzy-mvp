{{
  config(
    materialized='table'
  )
}}

with opportunities as (
  select * from {{ ref('fct_opportunity') }}
),

-- Calculate historical win rates and velocity
historical_metrics as (
  select
    owner_id,
    created_month,
    count(*) as total_opportunities,
    sum(case when outcome = 'Won' then 1 else 0 end) as won_opportunities,
    sum(case when outcome = 'Won' then opportunity_amount else 0 end) as won_amount,
    avg(case when outcome = 'Won' then days_to_close else null end) as avg_days_to_close,
    -- P50 calculation (median days to close for won deals)
    percentile_cont(0.5) within group (order by days_to_close) as p50_days_to_close,
    -- P90 calculation (90th percentile days to close for won deals)
    percentile_cont(0.9) within group (order by days_to_close) as p90_days_to_close,
    -- P10 calculation (10th percentile days to close for won deals)
    percentile_cont(0.1) within group (order by days_to_close) as p10_days_to_close
  from opportunities
  where outcome in ('Won', 'Lost')
    and created_date >= dateadd('month', -12, current_date())  -- Last 12 months
  group by owner_id, created_month
),

-- Calculate current pipeline for forecasting
current_pipeline as (
  select
    owner_id,
    count(*) as open_opportunities,
    sum(opportunity_amount) as pipeline_amount,
    avg(total_days_in_pipeline) as avg_days_in_pipeline,
    -- Group by close month for forecasting
    close_month,
    close_quarter,
    close_year
  from opportunities
  where outcome = 'Open'
    and close_date is not null
  group by owner_id, close_month, close_quarter, close_year
),

-- Calculate forecast based on historical performance
forecast_calculation as (
  select
    cp.owner_id,
    cp.close_month,
    cp.close_quarter,
    cp.close_year,
    cp.open_opportunities,
    cp.pipeline_amount,
    
    -- Historical win rate (last 6 months)
    avg(hm.won_opportunities::float / nullif(hm.total_opportunities, 0)) as historical_win_rate,
    
    -- Historical velocity (deals per month)
    avg(hm.total_opportunities) as avg_deals_per_month,
    
    -- Historical average deal size
    avg(case when hm.won_opportunities > 0 then hm.won_amount / hm.won_opportunities else 0 end) as avg_deal_size,
    
    -- P50 forecast (based on historical P50)
    avg(hm.p50_days_to_close) as p50_days_to_close,
    
    -- P90 forecast (based on historical P90)
    avg(hm.p90_days_to_close) as p90_days_to_close,
    
    -- P10 forecast (based on historical P10)
    avg(hm.p10_days_to_close) as p10_days_to_close,
    
    -- Forecast calculations
    cp.open_opportunities * avg(hm.won_opportunities::float / nullif(hm.total_opportunities, 0)) as forecasted_wins,
    cp.pipeline_amount * avg(hm.won_opportunities::float / nullif(hm.total_opportunities, 0)) as forecasted_amount
    
  from current_pipeline cp
  left join historical_metrics hm on cp.owner_id = hm.owner_id
  where hm.created_month >= dateadd('month', -6, current_date())  -- Last 6 months for recent trends
  group by 
    cp.owner_id, cp.close_month, cp.close_quarter, cp.close_year,
    cp.open_opportunities, cp.pipeline_amount
)

select
  owner_id,
  close_month,
  close_quarter,
  close_year,
  open_opportunities,
  pipeline_amount,
  historical_win_rate,
  avg_deals_per_month,
  avg_deal_size,
  p10_days_to_close,
  p50_days_to_close,
  p90_days_to_close,
  forecasted_wins,
  forecasted_amount,
  
  -- Quota coverage (assuming 100k monthly quota per owner for demo)
  100000 as monthly_quota,
  forecasted_amount / 100000 as quota_coverage_ratio,
  
  -- Confidence intervals
  case 
    when historical_win_rate >= 0.3 then 'High'
    when historical_win_rate >= 0.2 then 'Medium'
    else 'Low'
  end as forecast_confidence,
  
  current_timestamp() as calculated_at

from forecast_calculation

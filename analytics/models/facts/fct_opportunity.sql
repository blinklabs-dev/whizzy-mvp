{{
  config(
    materialized='table'
  )
}}

with opportunities as (
  select * from {{ ref('stg_sf__opportunity') }}
),

opportunity_history as (
  select * from {{ ref('stg_sf__opportunity_history') }}
),

-- Calculate days in each stage for forecasting
stage_durations as (
  select
    opportunity_id,
    stage_name,
    stage_created_date,
    stage_close_date,
    datediff('day', stage_created_date, coalesce(stage_close_date, current_date())) as days_in_stage
  from opportunity_history
),

-- Aggregate stage durations per opportunity
opportunity_stage_metrics as (
  select
    opportunity_id,
    avg(days_in_stage) as avg_days_per_stage,
    sum(days_in_stage) as total_days_in_pipeline,
    count(distinct stage_name) as stages_touched
  from stage_durations
  group by opportunity_id
)

select
  -- Primary keys
  o.opportunity_id,
  o.account_id,
  o.owner_id,
  
  -- Opportunity details
  o.opportunity_name,
  o.opportunity_amount,
  o.stage_name,
  o.opportunity_type,
  
  -- Dates
  o.created_date,
  o.close_date,
  o.last_modified_date,
  
  -- Forecasting metrics
  osm.avg_days_per_stage,
  osm.total_days_in_pipeline,
  osm.stages_touched,
  
  -- Derived fields for forecasting
  case 
    when o.stage_name in ('Closed Won', 'Closed Lost') then 'Closed'
    else 'Open'
  end as opportunity_status,
  
  case 
    when o.stage_name = 'Closed Won' then 'Won'
    when o.stage_name = 'Closed Lost' then 'Lost'
    else 'Open'
  end as outcome,
  
  -- Time-based fields for forecasting
  date_trunc('month', o.created_date) as created_month,
  date_trunc('quarter', o.created_date) as created_quarter,
  date_trunc('year', o.created_date) as created_year,
  
  -- Close date fields (for forecasting)
  date_trunc('month', o.close_date) as close_month,
  date_trunc('quarter', o.close_date) as close_quarter,
  date_trunc('year', o.close_date) as close_year,
  
  -- Days to close (for P50/P90 calculations)
  case 
    when o.close_date is not null then datediff('day', o.created_date, o.close_date)
    else null
  end as days_to_close,
  
  -- Metadata
  o.loaded_at

from opportunities o
left join opportunity_stage_metrics osm on o.opportunity_id = osm.opportunity_id

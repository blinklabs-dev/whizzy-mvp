-- Slippage impact analysis by quarter, segment, and region
-- Used by CDO for comprehensive analysis and CFO for financial planning
{{
  config(
    materialized='table',
    description='Slippage impact analysis by quarter, segment, and region'
  )
}}

with fct_opp as (
  select * from {{ ref('fct_opportunity') }}
),
dim_account as (
  select * from {{ ref('dim_account') }}
),
dim_owner as (
  select * from {{ ref('dim_owner') }}
)

select
  date_trunc('quarter', fct_opp.close_date) as close_quarter,
  coalesce(dim_account.segment, 'Unknown') as segment,
  coalesce(dim_account.region, 'Unknown') as region,
  dim_owner.team_name,
  -- Slippage metrics
  count(case when fct_opp.is_slipped then 1 end) as slipped_opps,
  sum(case when fct_opp.is_slipped then fct_opp.amount else 0 end) as slipped_amount,
  avg(case when fct_opp.is_slipped then fct_opp.slip_days else null end) as avg_slip_days,
  -- Total pipeline for context
  count(*) as total_opps,
  sum(fct_opp.amount) as total_pipeline_amount,
  -- Slippage rates
  nullif(count(case when fct_opp.is_slipped then 1 end), 0) / nullif(count(*), 0) as slippage_rate,
  nullif(sum(case when fct_opp.is_slipped then fct_opp.amount else 0 end), 0) / nullif(sum(fct_opp.amount), 0) as slippage_amount_rate,
  -- QoQ comparison
  lag(count(case when fct_opp.is_slipped then 1 end)) over (
    partition by dim_account.segment, dim_account.region, dim_owner.team_name
    order by date_trunc('quarter', fct_opp.close_date)
  ) as prev_q_slipped_opps,
  lag(sum(case when fct_opp.is_slipped then fct_opp.amount else 0 end)) over (
    partition by dim_account.segment, dim_account.region, dim_owner.team_name
    order by date_trunc('quarter', fct_opp.close_date)
  ) as prev_q_slipped_amount,
  -- QoQ changes
  (count(case when fct_opp.is_slipped then 1 end) - lag(count(case when fct_opp.is_slipped then 1 end)) over (
    partition by dim_account.segment, dim_account.region, dim_owner.team_name
    order by date_trunc('quarter', fct_opp.close_date)
  )) as qoq_slipped_opps_change,
  (sum(case when fct_opp.is_slipped then fct_opp.amount else 0 end) - lag(sum(case when fct_opp.is_slipped then fct_opp.amount else 0 end)) over (
    partition by dim_account.segment, dim_account.region, dim_owner.team_name
    order by date_trunc('quarter', fct_opp.close_date)
  )) as qoq_slipped_amount_change,
  -- QoQ percentage changes
  case 
    when lag(count(case when fct_opp.is_slipped then 1 end)) over (
      partition by dim_account.segment, dim_account.region, dim_owner.team_name
      order by date_trunc('quarter', fct_opp.close_date)
    ) > 0 
    then ((count(case when fct_opp.is_slipped then 1 end) - lag(count(case when fct_opp.is_slipped then 1 end)) over (
      partition by dim_account.segment, dim_account.region, dim_owner.team_name
      order by date_trunc('quarter', fct_opp.close_date)
    )) / lag(count(case when fct_opp.is_slipped then 1 end)) over (
      partition by dim_account.segment, dim_account.region, dim_owner.team_name
      order by date_trunc('quarter', fct_opp.close_date)
    )) * 100)
    else null
  end as qoq_slipped_opps_percent_change,
  case 
    when lag(sum(case when fct_opp.is_slipped then fct_opp.amount else 0 end)) over (
      partition by dim_account.segment, dim_account.region, dim_owner.team_name
      order by date_trunc('quarter', fct_opp.close_date)
    ) > 0 
    then ((sum(case when fct_opp.is_slipped then fct_opp.amount else 0 end) - lag(sum(case when fct_opp.is_slipped then fct_opp.amount else 0 end)) over (
      partition by dim_account.segment, dim_account.region, dim_owner.team_name
      order by date_trunc('quarter', fct_opp.close_date)
    )) / lag(sum(case when fct_opp.is_slipped then fct_opp.amount else 0 end)) over (
      partition by dim_account.segment, dim_account.region, dim_owner.team_name
      order by date_trunc('quarter', fct_opp.close_date)
    )) * 100)
    else null
  end as qoq_slipped_amount_percent_change

from fct_opp
left join dim_account on fct_opp.account_id = dim_account.account_id
left join dim_owner on fct_opp.owner_id = dim_owner.owner_id

where fct_opp.close_date >= dateadd('month', -18, current_date())
  and fct_opp.stage_name not in ('Closed Won', 'Closed Lost')  -- Focus on open deals

group by 1, 2, 3, 4
order by 1 desc, 2, 3, 4

-- Stage velocity analysis by quarter, segment, region, and stage
-- Used by Sales Manager, AE, and CFO personas
{{
  config(
    materialized='table',
    description='Stage velocity analysis by quarter, segment, region, and stage'
  )
}}

with fct_opp as (
  select * from {{ ref('fct_opportunity') }}
),
fct_history as (
  select * from {{ ref('fct_stage_transitions') }}
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
  fct_history.stage_name,
  dim_owner.team_name,
  count(distinct fct_opp.opportunity_id) as opp_count,
  avg(fct_history.days_in_stage) as avg_days_in_stage,
  sum(fct_opp.amount) as total_amount,
  -- QoQ comparison
  lag(avg(fct_history.days_in_stage)) over (
    partition by dim_account.segment, dim_account.region, fct_history.stage_name, dim_owner.team_name
    order by date_trunc('quarter', fct_opp.close_date)
  ) as prev_q_avg_days,
  -- Calculate QoQ change
  (avg(fct_history.days_in_stage) - lag(avg(fct_history.days_in_stage)) over (
    partition by dim_account.segment, dim_account.region, fct_history.stage_name, dim_owner.team_name
    order by date_trunc('quarter', fct_opp.close_date)
  )) as qoq_days_change,
  -- QoQ percentage change
  case 
    when lag(avg(fct_history.days_in_stage)) over (
      partition by dim_account.segment, dim_account.region, fct_history.stage_name, dim_owner.team_name
      order by date_trunc('quarter', fct_opp.close_date)
    ) > 0 
    then ((avg(fct_history.days_in_stage) - lag(avg(fct_history.days_in_stage)) over (
      partition by dim_account.segment, dim_account.region, fct_history.stage_name, dim_owner.team_name
      order by date_trunc('quarter', fct_opp.close_date)
    )) / lag(avg(fct_history.days_in_stage)) over (
      partition by dim_account.segment, dim_account.region, fct_history.stage_name, dim_owner.team_name
      order by date_trunc('quarter', fct_opp.close_date)
    )) * 100)
    else null
  end as qoq_percent_change

from fct_opp
left join fct_history on fct_opp.opportunity_id = fct_history.opportunity_id
left join dim_account on fct_opp.account_id = dim_account.account_id
left join dim_owner on fct_opp.owner_id = dim_owner.owner_id

where fct_opp.close_date >= dateadd('month', -18, current_date())
  and fct_history.stage_name is not null

group by 1, 2, 3, 4, 5
order by 1 desc, 2, 3, 4, 5

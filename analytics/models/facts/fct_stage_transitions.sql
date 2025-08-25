{{
  config(
    materialized='table',
    description='Fact table for opportunity stage transitions and velocity'
  )
}}

with opportunity_history as (
    select * from {{ source('raw', 'raw_opportunity_history') }}
),

stage_transitions as (
    select
        opportunityid as opportunity_id,
        stagename as stage_name,
        amount,
        closedate as close_date,
        createddate as stage_created_date,
        
        -- Calculate days in this stage
        datediff('day', 
            createddate, 
            coalesce(
                lead(createddate) over (
                    partition by opportunityid 
                    order by createddate
                ), 
                current_date()
            )
        ) as days_in_stage,
        
        -- Stage sequence number
        row_number() over (
            partition by opportunityid 
            order by createddate
        ) as stage_sequence,
        
        -- Previous stage
        lag(stagename) over (
            partition by opportunityid 
            order by createddate
        ) as previous_stage,
        
        -- Next stage
        lead(stagename) over (
            partition by opportunityid 
            order by createddate
        ) as next_stage
        
    from opportunity_history
    where opportunityid is not null
      and stagename is not null
),

stage_velocity as (
    select
        opportunity_id,
        stage_name,
        amount,
        close_date,
        stage_created_date,
        days_in_stage,
        stage_sequence,
        previous_stage,
        next_stage,
        
        -- Stage velocity metrics
        case 
            when days_in_stage <= 7 then 'Fast'
            when days_in_stage <= 30 then 'Normal'
            when days_in_stage <= 90 then 'Slow'
            else 'Stuck'
        end as velocity_category,
        
        -- Stage transition type
        case 
            when previous_stage is null then 'Initial'
            when next_stage is null then 'Current'
            else 'Transition'
        end as transition_type
        
    from stage_transitions
)

select * from stage_velocity

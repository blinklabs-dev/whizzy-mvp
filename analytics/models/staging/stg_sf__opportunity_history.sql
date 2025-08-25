{{
  config(
    materialized='view'
  )
}}

with source as (
  select * from {{ source('raw', 'raw_opportunity_history') }}
),

renamed as (
  select
    -- Primary keys
    id as history_id,
    opportunityid as opportunity_id,
    
    -- Stage information
    stagename as stage_name,
    amount as stage_amount,
    
    -- Dates (critical for forecasting)
    createddate as stage_created_date,
    closedate as stage_close_date,
    
    -- Metadata
    _loaded_at as loaded_at
    
  from source
)

select * from renamed

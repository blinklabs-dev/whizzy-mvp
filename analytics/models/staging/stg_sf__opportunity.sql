{{
  config(
    materialized='view'
  )
}}

with source as (
  select * from {{ source('raw', 'raw_opportunity') }}
),

renamed as (
  select
    -- Primary keys
    id as opportunity_id,
    accountid as account_id,
    ownerid as owner_id,
    
    -- Opportunity details
    name as opportunity_name,
    amount as opportunity_amount,
    stagename as stage_name,
    type as opportunity_type,
    
    -- Dates (critical for forecasting)
    createddate as created_date,
    closedate as close_date,
    lastmodifieddate as last_modified_date,
    
    -- Metadata
    _loaded_at as loaded_at
    
  from source
)

select * from renamed

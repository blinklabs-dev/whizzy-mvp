{{
  config(
    materialized='table'
  )
}}

-- For now, create a simple owner dimension from opportunity data
-- In production, this would come from User object

with opportunity_owners as (
  select distinct
    owner_id,
    owner_id as owner_name,  -- Placeholder, would be actual name in production
    'Active' as owner_status,
    current_timestamp() as created_at
  from {{ ref('stg_sf__opportunity') }}
  where owner_id is not null
)

select * from opportunity_owners

{{
  config(
    materialized='table'
  )
}}

with account_source as (
    select * from {{ source('raw', 'raw_account') }}
),

account_cleaned as (
    select
        id as account_id,
        name as account_name,
        industry,
        type,
        billingcountry as country,
        billingstate as state,
        billingcity as city,
        annualrevenue,
        numberofemployees,
        createddate,
        lastmodifieddate,
        
        -- Segment logic based on revenue and employee count
        case 
            when annualrevenue >= 10000000 then 'Enterprise'
            when annualrevenue >= 1000000 then 'Mid-Market'
            when annualrevenue >= 100000 then 'SMB'
            else 'SMB'
        end as segment,
        
        -- Region logic based on country/state
        case 
            when billingcountry = 'United States' then 'North America'
            when billingcountry in ('Canada', 'Mexico') then 'North America'
            when billingcountry in ('United Kingdom', 'Germany', 'France', 'Italy', 'Spain') then 'Europe'
            when billingcountry in ('Australia', 'New Zealand') then 'APAC'
            else 'Other'
        end as region
        
    from account_source
    where id is not null
)

select * from account_cleaned

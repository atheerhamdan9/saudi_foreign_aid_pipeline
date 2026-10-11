with source as (

    select *
    from {{ source('source_a', 'cleaned_source_a_records') }}

),

staged as (

    select
        record,
        project_title,
        project_status,
        project_sector,
        project_location,
        total_cost_usd,
        project_donor,
        beneficiary_country,
        snapshot_month
    from source

)

select *
from staged

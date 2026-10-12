with source as (

    select *
    from {{ source('saudi_aid_projects', 'raw_source_a_records') }}

),

cleaned as (

    select
        record,
        trim(project_title) as project_title,
        trim(project_status) as project_status,
        trim(project_sector) as project_sector,
        trim(project_location) as project_location,

        {% if target.type == 'bigquery' %}
            safe_cast(
                replace(
                    replace(trim(cast(total_cost_usd as string)), ',', ''),
                    '$',
                    ''
                ) as numeric
            ) as total_cost_usd,
        {% else %}
            try_cast(
                replace(
                    replace(trim(cast(total_cost_usd as varchar)), ',', ''),
                    '$',
                    ''
                ) as decimal(38, 6)
            ) as total_cost_usd,
        {% endif %}

        trim(project_donor) as project_donor,
        trim(beneficiary_country) as beneficiary_country,
        snapshot_month

    from source

),

deduplicated as (

    select *
    from cleaned
    qualify row_number() over (
        partition by
            snapshot_month,
            project_title,
            project_status,
            project_sector,
            project_location,
            total_cost_usd,
            project_donor,
            beneficiary_country
        order by record
    ) = 1

)

select *
from deduplicated
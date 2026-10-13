{%- set snapshot_months = var('snapshot_months', []) -%}

{{
    config(
        materialized='incremental',
        incremental_strategy='append' if target.type == 'duckdb' else 'merge',
        pre_hook=["{{ delete_snapshot_metrics() }}"] if target.type == 'duckdb' else [],
        unique_key=['snapshot_month', 'dimension_type', 'dimension_value']
    )
}}
with staged as (

    select *
    from {{ ref('stg_source_a__records') }}

    {% if is_incremental() and snapshot_months | length > 0 %}
        where snapshot_month in (
            {% for month in snapshot_months %}
                '{{ month }}'{{ "," if not loop.last }}
            {% endfor %}
        )
    {% endif %}

),

dimensions as (

    select
        snapshot_month,
        'beneficiary_country' as dimension_type,
        beneficiary_country as dimension_value,
        total_cost_usd
    from staged

    union all

    select
        snapshot_month,
        'project_sector' as dimension_type,
        project_sector as dimension_value,
        total_cost_usd
    from staged

    union all

    select
        snapshot_month,
        'project_donor' as dimension_type,
        project_donor as dimension_value,
        total_cost_usd
    from staged

    union all

    select
        snapshot_month,
        'project_status' as dimension_type,
        project_status as dimension_value,
        total_cost_usd
    from staged

)

select
    snapshot_month,
    dimension_type,
    dimension_value,
    count(*) as record_count,
    sum(total_cost_usd) as total_cost_usd
from dimensions
group by
    snapshot_month,
    dimension_type,
    dimension_value


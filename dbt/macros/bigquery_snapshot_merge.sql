{% macro bigquery__get_merge_sql(
    target, source, unique_key, dest_columns, incremental_predicates=none
) %}
{% if target.identifier != 'fct_records_by_snapshot' %}
    {{ return(
        dbt.default__get_merge_sql(
            target,
            source,
            unique_key,
            dest_columns,
            incremental_predicates
        )
    ) }}
{% endif %}
    {% set snapshot_months = var('snapshot_months', []) %}
    {% if snapshot_months | length == 0 %}
    {{ exceptions.raise_compiler_error(
        "BigQuery incremental MERGE requires snapshot_months."
    ) }}
    {% endif %}
    {% set columns = dest_columns | map(attribute='name') | list %}
    {% set quoted_columns = get_quoted_csv(columns) %}

    merge into {{ target }} as DBT_INTERNAL_DEST
    using {{ source }} as DBT_INTERNAL_SOURCE
    on
        DBT_INTERNAL_DEST.snapshot_month = DBT_INTERNAL_SOURCE.snapshot_month
        and DBT_INTERNAL_DEST.dimension_type = DBT_INTERNAL_SOURCE.dimension_type
        and DBT_INTERNAL_DEST.dimension_value = DBT_INTERNAL_SOURCE.dimension_value

    when matched then update set
        record_count = DBT_INTERNAL_SOURCE.record_count,
        total_cost_usd = DBT_INTERNAL_SOURCE.total_cost_usd

    when not matched then insert
        ({{ quoted_columns }})
    values
        (
            DBT_INTERNAL_SOURCE.snapshot_month,
            DBT_INTERNAL_SOURCE.dimension_type,
            DBT_INTERNAL_SOURCE.dimension_value,
            DBT_INTERNAL_SOURCE.record_count,
            DBT_INTERNAL_SOURCE.total_cost_usd
        )

    {% if snapshot_months | length > 0 %}
    when not matched by source
        and DBT_INTERNAL_DEST.snapshot_month in (
            {% for month in snapshot_months %}
                '{{ month }}'{{ "," if not loop.last }}
            {% endfor %}
        )
    then delete
    {% endif %}

{% endmacro %}
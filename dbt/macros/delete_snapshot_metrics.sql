{% macro delete_snapshot_metrics() %}
    {% if is_incremental() and target.type == 'duckdb' %}
        {% set snapshot_months = var('snapshot_months', []) %}

        {% if snapshot_months | length == 0 %}
            {{ exceptions.raise_compiler_error(
                "DuckDB incremental run requires snapshot_months. Specify the months to refresh."
            ) }}
        {% endif %}

        DELETE FROM {{ this }}
        WHERE snapshot_month IN (
            {% for month in snapshot_months %}
                '{{ month }}'{{ "," if not loop.last }}
            {% endfor %}
        )
    {% else %}
        SELECT 1
    {% endif %}
{% endmacro %}
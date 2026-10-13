{% macro delete_snapshot_metrics() %}

    {% if is_incremental() and target.type in ['duckdb', 'bigquery'] %}
        {% set snapshot_months = var('snapshot_months', []) %}

        DELETE FROM {{ this }}
        WHERE snapshot_month IN (

            {% if snapshot_months | length > 0 %}

                {% for month in snapshot_months %}
                    '{{ month }}'{{ "," if not loop.last }}
                {% endfor %}

            {% else %}

                SELECT DISTINCT snapshot_month
                FROM {{ ref('stg_source_a__records') }}

            {% endif %}

        )

    {% else %}

        SELECT 1

    {% endif %}

{% endmacro %}
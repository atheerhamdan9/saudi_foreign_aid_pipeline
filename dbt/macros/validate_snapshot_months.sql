{% macro validate_snapshot_months() %}
    {% if execute and is_incremental() %}
        {% set snapshot_months = var('snapshot_months', []) %}

        {% if snapshot_months | length == 0 %}
            {{ exceptions.raise_compiler_error(
                "Incremental run requires snapshot_months."
            ) }}
        {% endif %}

        {% set query %}
            SELECT DISTINCT snapshot_month
            FROM {{ ref('stg_source_a__records') }}
            WHERE snapshot_month IN (
                {% for month in snapshot_months %}
                    '{{ month }}'{{ "," if not loop.last }}
                {% endfor %}
            )
        {% endset %}

        {% set results = run_query(query) %}
        {% set available_months = results.columns[0].values() | list %}

        {% for month in snapshot_months %}
            {% if month not in available_months %}
                {{ exceptions.raise_compiler_error(
                    "Missing snapshot_month in staging: " ~ month
                    ~ ". Incremental update aborted."
                ) }}
            {% endif %}
        {% endfor %}
    {% endif %}
{% endmacro %}
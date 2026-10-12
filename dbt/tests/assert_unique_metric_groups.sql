SELECT
    snapshot_month,
    dimension_type,
    dimension_value,
    COUNT(*) AS occurrences
FROM {{ ref('fct_records_by_snapshot') }}
GROUP BY
    snapshot_month,
    dimension_type,
    dimension_value
HAVING COUNT(*) > 1

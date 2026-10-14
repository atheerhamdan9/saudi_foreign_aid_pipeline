# GCP Environment

## Resources

- Project: `saudi-foreign-aid-data`
- Region: `europe-west1`
- Raw GCS bucket: `saudi-foreign-aid-raw-data`
- Raw BigQuery dataset: `saudi_aid_raw`
- dbt BigQuery dataset: `saudi_aid_dbt_dev`

## Authentication

Local authentication:

- dbt uses Google OAuth.
- Python Google Cloud libraries use Application Default Credentials (ADC).

Configure ADC locally with:

```bash
gcloud auth application-default login
```

Runtime service account:

`saudi-aid-pipeline-sa@saudi-foreign-aid-data.iam.gserviceaccount.com`

No service account keys or credentials should be committed to the repository.

## Runtime Permissions

The runtime service account has:

- `roles/bigquery.jobUser` on the project
- `roles/storage.objectCreator` on the raw GCS bucket
- `roles/storage.objectViewer` on the raw GCS bucket
- `roles/bigquery.dataEditor` on `saudi_aid_raw`
- `roles/bigquery.dataEditor` on `saudi_aid_dbt_dev`

## Existing Cloud Resources

These resources are shared by the project and should not be recreated:

- GCS bucket: `saudi-foreign-aid-raw-data`
- BigQuery dataset: `saudi_aid_raw`
- BigQuery dataset: `saudi_aid_dbt_dev`

## Runtime Security Notes

- Cloud runtimes should use the configured service account through Application Default Credentials (ADC).
- Do not create or commit service account JSON keys.
- Secrets such as SMTP credentials must be provided through environment variables or a managed secret store.
- The `.env` file is local-only and must remain excluded from Git.
- Cloud permissions should remain scoped to only the resources required by the pipeline.

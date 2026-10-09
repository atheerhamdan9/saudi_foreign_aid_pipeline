# Saudi Foreign Aid Pipeline — Data Architecture

```mermaid
flowchart TD
    A["<b>Open Data Platform</b>"]

    B["<b>Data Ingestion</b><br/><small>Read CSV Files</small>"]

    C["<b>Google Cloud Storage (GCS)</b><br/><small>Preserve Original Raw CSV Files</small>"]

    D["<b>BigQuery (Raw Layer)</b><br/><small>Load Source Records</small>"]

    E["<b>BigQuery (Staging Layer)</b><br/><small>Standardize, Clean & Validate Data</small>"]

    F["<b>BigQuery (Analytics Layer)</b><br/><small>Analytical Tables & Aggregated Views</small>"]

    G["<b>Streamlit Dashboard</b>"]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
```

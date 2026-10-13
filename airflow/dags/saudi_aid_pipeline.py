from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path

import pendulum
from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


log = logging.getLogger(__name__)

DEFAULT_RUN_DATE = os.getenv("DEFAULT_RUN_DATE", "2026-10-11")
SOURCE_ROOT = Path("/opt/project/data/raw/source_a")
SNAPSHOT_PATTERN = re.compile(r"(?<!\d)(\d{2})M(\d{2})(?!\d)")


def notify_failure(context):
    """Log the failure and send an email alert."""
    task_instance = context["task_instance"]
    exception = context.get("exception")

    dag_id = task_instance.dag_id
    task_id = task_instance.task_id
    run_id = context.get("run_id")

    log.error(
        "PIPELINE FAILURE | dag=%s | task=%s | run_id=%s | exception=%s",
        dag_id,
        task_id,
        run_id,
        exception,
    )

    try:
        smtp_host = os.environ["SMTP_HOST"]
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ["SMTP_USER"]
        smtp_password = os.environ["SMTP_PASSWORD"]
        email_from = os.environ["ALERT_EMAIL_FROM"]
        email_to = os.environ["ALERT_EMAIL_TO"]

        message = EmailMessage()
        message["Subject"] = f"[FAILED] Saudi Aid Pipeline - {task_id}"
        message["From"] = email_from
        message["To"] = email_to

        message.set_content(
            f"""Saudi Foreign Aid pipeline task failed.

DAG: {dag_id}
Task: {task_id}
Run ID: {run_id}
Exception: {exception}

Check the Airflow logs for full details.
"""
        )

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)

        log.info("Failure alert email sent successfully.")

    except Exception:
        log.exception("Failed to send failure alert email.")


def prepare_run(**context):
    """Validate the ingestion date and discover snapshot months."""
    dag_run = context.get("dag_run")

    run_date = DEFAULT_RUN_DATE
    if dag_run and dag_run.conf:
        run_date = dag_run.conf.get("run_date", DEFAULT_RUN_DATE)

    try:
        datetime.strptime(run_date, "%Y-%m-%d")
    except ValueError as exc:
        raise AirflowFailException(
            "run_date must use YYYY-MM-DD format."
        ) from exc

    ingest_dir = SOURCE_ROOT / f"ingest_date={run_date}"

    if not ingest_dir.is_dir():
        raise AirflowFailException(
            f"Input directory not found: {ingest_dir}"
        )

    files = sorted(ingest_dir.glob("*.csv"))

    if not files:
        raise AirflowFailException(
            f"No CSV files found in: {ingest_dir}"
        )

    snapshot_months = []

    for path in files:
        match = SNAPSHOT_PATTERN.search(path.stem)

        if match is None:
            raise AirflowFailException(
                f"Cannot determine snapshot month from: {path.name}"
            )

        year = 2000 + int(match.group(1))
        month = int(match.group(2))

        if not 1 <= month <= 12:
            raise AirflowFailException(
                f"Invalid snapshot month in: {path.name}"
            )

        snapshot_month = f"{year:04d}-{month:02d}"

        if snapshot_month in snapshot_months:
            raise AirflowFailException(
                f"Duplicate snapshot month: {snapshot_month}"
            )

        snapshot_months.append(snapshot_month)

    dbt_vars = json.dumps(
        {"snapshot_months": snapshot_months}
    )

    ti = context["ti"]
    ti.xcom_push(key="run_date", value=run_date)
    ti.xcom_push(key="snapshot_months", value=snapshot_months)
    ti.xcom_push(key="dbt_vars", value=dbt_vars)

    log.info(
        "Prepared run_date=%s snapshot_months=%s",
        run_date,
        snapshot_months,
    )


default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=5),
    "on_failure_callback": notify_failure,
}


with DAG(
    dag_id="saudi_foreign_aid_pipeline",
    description="Orchestrate Saudi Foreign Aid snapshot processing.",
    start_date=pendulum.datetime(2026, 10, 1, tz="UTC"),
    schedule=os.getenv("PIPELINE_SCHEDULE", "@daily"),
    catchup=False,
    default_args=default_args,
    tags=["capstone", "saudi-aid"],
) as dag:

    prepare = PythonOperator(
        task_id="prepare_run",
        python_callable=prepare_run,
    )

    ingest_snapshot = BashOperator(
        task_id="ingest_snapshot",
        cwd="/opt/project",
        bash_command="""
        set -e
        aid-pipeline run \
          --date "{{ ti.xcom_pull(task_ids='prepare_run', key='run_date') }}"
        """,
    )

    dbt_incremental = BashOperator(
        task_id="dbt_incremental",
        cwd="/opt/project",
        bash_command="""
        set -e
        dbt build \
          --project-dir dbt \
          --profiles-dir dbt \
          --target dev \
          --vars '{{ ti.xcom_pull(task_ids="prepare_run", key="dbt_vars") }}'
        """,
    )

    prepare >> ingest_snapshot >> dbt_incremental

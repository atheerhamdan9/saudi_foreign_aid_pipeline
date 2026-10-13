from airflow.models import DagBag
from airflow.utils.dag_cycle_tester import check_cycle

DAG_ID = "saudi_foreign_aid_pipeline"
EXPECTED_TASKS = {
    "prepare_run",
    "ingest_snapshot",
    "dbt_incremental",
}


def load_dag():
    dag_bag = DagBag(
        dag_folder="/opt/airflow/dags",
        include_examples=False,
    )

    assert not dag_bag.import_errors, dag_bag.import_errors

    dag = dag_bag.dags.get(DAG_ID)
    assert dag is not None

    return dag


def test_dag_imports_without_errors():
    load_dag()


def test_expected_tasks_exist():
    dag = load_dag()
    assert set(dag.task_ids) == EXPECTED_TASKS


def test_task_dependencies():
    dag = load_dag()

    prepare = dag.get_task("prepare_run")
    ingest = dag.get_task("ingest_snapshot")
    dbt = dag.get_task("dbt_incremental")

    assert prepare.downstream_task_ids == {"ingest_snapshot"}
    assert ingest.upstream_task_ids == {"prepare_run"}
    assert ingest.downstream_task_ids == {"dbt_incremental"}
    assert dbt.upstream_task_ids == {"ingest_snapshot"}


def test_retry_configuration():
    dag = load_dag()

    for task in dag.tasks:
        assert task.retries == 2
        assert task.retry_exponential_backoff is True
        assert task.on_failure_callback is not None


def test_dag_has_no_cycles():
    dag = load_dag()
    check_cycle(dag)

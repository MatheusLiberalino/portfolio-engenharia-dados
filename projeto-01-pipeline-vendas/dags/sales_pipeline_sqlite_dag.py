from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_DIR = "/opt/airflow/project"


default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="sales_pipeline_sqlite_demo",
    description="Demo local do pipeline de vendas usando SQLite.",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["portfolio", "demo", "sqlite", "sales"],
) as dag:
    run_sqlite_pipeline = BashOperator(
        task_id="run_sqlite_pipeline",
        bash_command=f"cd {PROJECT_DIR} && python src/run_pipeline_sqlite.py",
    )

    run_sqlite_quality_checks = BashOperator(
        task_id="run_sqlite_quality_checks",
        bash_command=f"cd {PROJECT_DIR} && python src/quality_checks_sqlite.py",
    )

    run_sqlite_pipeline >> run_sqlite_quality_checks

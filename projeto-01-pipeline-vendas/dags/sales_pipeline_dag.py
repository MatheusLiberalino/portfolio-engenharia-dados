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
    dag_id="sales_pipeline_elt",
    description="Pipeline ELT de vendas com Python, PostgreSQL, dbt e testes de qualidade.",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["portfolio", "elt", "dbt", "sales"],
) as dag:
    generate_raw_data = BashOperator(
        task_id="generate_raw_data",
        bash_command=f"cd {PROJECT_DIR} && python src/generate_data.py",
    )

    load_staging = BashOperator(
        task_id="load_staging",
        bash_command=f"cd {PROJECT_DIR} && python src/load_staging.py",
    )

    dbt_debug = BashOperator(
        task_id="dbt_debug",
        bash_command=f"cd {PROJECT_DIR} && dbt debug --profiles-dir .",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {PROJECT_DIR} && dbt run --profiles-dir .",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {PROJECT_DIR} && dbt test --profiles-dir .",
    )

    run_quality_checks = BashOperator(
        task_id="run_quality_checks",
        bash_command=f"cd {PROJECT_DIR} && python src/quality_checks.py",
    )

    generate_docs = BashOperator(
        task_id="generate_dbt_docs",
        bash_command=f"cd {PROJECT_DIR} && dbt docs generate --profiles-dir .",
    )

    (
        generate_raw_data
        >> load_staging
        >> dbt_debug
        >> dbt_run
        >> dbt_test
        >> run_quality_checks
        >> generate_docs
    )

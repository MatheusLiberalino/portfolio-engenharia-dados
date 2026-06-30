from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
SQL_DIR = PROJECT_DIR / "sql"


TABLE_FILES = {
    "staging.customers": "customers.csv",
    "staging.products": "products.csv",
    "staging.orders": "orders.csv",
    "staging.order_items": "order_items.csv",
}


def get_connection() -> connection:
    load_dotenv(PROJECT_DIR / ".env")
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "sales_dw"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )


def execute_sql_file(conn: connection, file_name: str) -> None:
    sql = (SQL_DIR / file_name).read_text(encoding="utf-8")
    with conn.cursor() as cursor:
        cursor.execute(sql)
    conn.commit()


def load_csv_to_table(conn: connection, table_name: str, file_name: str) -> None:
    csv_path = RAW_DIR / file_name
    dataframe = pd.read_csv(csv_path)
    columns = list(dataframe.columns)
    placeholders = ", ".join(["%s"] * len(columns))
    column_list = ", ".join(columns)

    insert_sql = f"insert into {table_name} ({column_list}) values ({placeholders})"

    with conn.cursor() as cursor:
        cursor.executemany(insert_sql, dataframe.to_records(index=False).tolist())
    conn.commit()


def main() -> None:
    with get_connection() as conn:
        execute_sql_file(conn, "01_create_schemas.sql")
        execute_sql_file(conn, "02_create_staging_tables.sql")

        for table_name, file_name in TABLE_FILES.items():
            load_csv_to_table(conn, table_name, file_name)
            print(f"Carga concluida: {table_name}")


if __name__ == "__main__":
    main()

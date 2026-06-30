from __future__ import annotations

import csv
import sqlite3
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
SQLITE_DIR = PROJECT_DIR / "sqlite"
DATABASE_PATH = PROJECT_DIR / "data" / "sales_dw.sqlite"

TABLE_FILES = {
    "customers": "customers.csv",
    "products": "products.csv",
    "orders": "orders.csv",
    "order_items": "order_items.csv",
}


def run_python_script(script_name: str) -> None:
    script_path = PROJECT_DIR / "src" / script_name
    subprocess.run([sys.executable, str(script_path)], check=True)


def execute_sql_file(conn: sqlite3.Connection, file_name: str) -> None:
    sql = (SQLITE_DIR / file_name).read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


def load_csv_to_table(conn: sqlite3.Connection, table_name: str, file_name: str) -> None:
    csv_path = RAW_DIR / file_name

    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    if not rows:
        return

    columns = reader.fieldnames or []
    placeholders = ", ".join(["?"] * len(columns))
    column_list = ", ".join(columns)
    insert_sql = f"insert into {table_name} ({column_list}) values ({placeholders})"
    values = [tuple(row[column] for column in columns) for row in rows]

    conn.executemany(insert_sql, values)
    conn.commit()


def main() -> None:
    print("1/4 Gerando dados brutos...")
    run_python_script("generate_data.py")

    print("2/4 Criando banco SQLite local...")
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("pragma foreign_keys = on")
        execute_sql_file(conn, "schemas.sql")

        print("3/4 Carregando staging local...")
        for table_name, file_name in TABLE_FILES.items():
            load_csv_to_table(conn, table_name, file_name)
            print(f"Carga concluida: {table_name}")

        print("4/4 Transformando Data Warehouse local...")
        execute_sql_file(conn, "transform_dw.sql")

    print(f"Pipeline SQLite finalizado: {DATABASE_PATH}")


if __name__ == "__main__":
    main()

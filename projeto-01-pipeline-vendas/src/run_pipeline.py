from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from load_staging import execute_sql_file, get_connection


PROJECT_DIR = Path(__file__).resolve().parents[1]


def run_python_script(script_name: str) -> None:
    script_path = PROJECT_DIR / "src" / script_name
    subprocess.run([sys.executable, str(script_path)], check=True)


def main() -> None:
    print("1/4 Gerando dados brutos...")
    run_python_script("generate_data.py")

    print("2/4 Carregando staging...")
    run_python_script("load_staging.py")

    print("3/4 Transformando Data Warehouse...")
    with get_connection() as conn:
        execute_sql_file(conn, "03_create_dw_tables.sql")
        execute_sql_file(conn, "04_transform_dw.sql")

    print("4/4 Pipeline finalizado com sucesso.")


if __name__ == "__main__":
    main()

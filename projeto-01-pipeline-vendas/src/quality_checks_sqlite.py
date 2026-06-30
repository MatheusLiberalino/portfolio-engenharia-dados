from __future__ import annotations

import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_DIR / "data" / "sales_dw.sqlite"

CHECKS = [
    (
        "fact_sales possui registros",
        "select count(*) >= 1 from fact_sales",
    ),
    (
        "order_item_id unico na fato",
        "select count(*) = count(distinct order_item_id) from fact_sales",
    ),
    (
        "sem chaves nulas na fato",
        """
        select count(*) = 0
        from fact_sales
        where customer_key is null
           or product_key is null
           or order_date_key is null
        """,
    ),
    (
        "gross_amount consistente",
        """
        select count(*) = 0
        from fact_sales
        where round(gross_amount, 2) <> round(quantity * unit_price, 2)
        """,
    ),
    (
        "quantidades positivas",
        "select count(*) = 0 from fact_sales where quantity <= 0",
    ),
]


def main() -> None:
    failed_checks = []

    with sqlite3.connect(DATABASE_PATH) as conn:
        for check_name, query in CHECKS:
            passed = bool(conn.execute(query).fetchone()[0])
            status = "OK" if passed else "FAIL"
            print(f"{status} - {check_name}")

            if not passed:
                failed_checks.append(check_name)

    if failed_checks:
        raise SystemExit(f"Falhas de qualidade: {', '.join(failed_checks)}")


if __name__ == "__main__":
    main()

from __future__ import annotations

from load_staging import get_connection


CHECKS = [
    (
        "fact_sales possui registros",
        "select count(*) >= 1 from dw.fact_sales",
    ),
    (
        "order_item_id unico na fato",
        """
        select count(*) = count(distinct order_item_id)
        from dw.fact_sales
        """,
    ),
    (
        "sem chaves nulas na fato",
        """
        select count(*) = 0
        from dw.fact_sales
        where customer_key is null
           or product_key is null
           or order_date_key is null
        """,
    ),
    (
        "gross_amount consistente",
        """
        select count(*) = 0
        from dw.fact_sales
        where gross_amount <> quantity * unit_price
        """,
    ),
    (
        "quantidades positivas",
        """
        select count(*) = 0
        from dw.fact_sales
        where quantity <= 0
        """,
    ),
]


def main() -> None:
    failed_checks = []

    with get_connection() as conn:
        with conn.cursor() as cursor:
            for check_name, query in CHECKS:
                cursor.execute(query)
                passed = cursor.fetchone()[0]
                status = "OK" if passed else "FAIL"
                print(f"{status} - {check_name}")

                if not passed:
                    failed_checks.append(check_name)

    if failed_checks:
        raise SystemExit(f"Falhas de qualidade: {', '.join(failed_checks)}")


if __name__ == "__main__":
    main()

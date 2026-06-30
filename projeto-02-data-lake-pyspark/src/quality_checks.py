from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
SILVER_DIR = PROJECT_DIR / "data" / "silver"
GOLD_DIR = PROJECT_DIR / "data" / "gold"


def read_parquet_dataset(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path, engine="fastparquet")


def assert_condition(condition: bool, message: str) -> None:
    status = "OK" if condition else "FAIL"
    print(f"{status} - {message}")
    if not condition:
        raise AssertionError(message)


def main() -> None:
    customers = read_parquet_dataset(SILVER_DIR / "customers")
    products = read_parquet_dataset(SILVER_DIR / "products")
    orders = read_parquet_dataset(SILVER_DIR / "orders")
    order_items = read_parquet_dataset(SILVER_DIR / "order_items")
    daily_sales = read_parquet_dataset(GOLD_DIR / "daily_sales")
    product_sales = read_parquet_dataset(GOLD_DIR / "product_sales")
    state_sales = read_parquet_dataset(GOLD_DIR / "state_sales")

    assert_condition(len(customers) > 0, "silver customers possui registros")
    assert_condition(len(products) > 0, "silver products possui registros")
    assert_condition(len(orders) > 0, "silver orders possui registros")
    assert_condition(len(order_items) > 0, "silver order_items possui registros")
    assert_condition(len(daily_sales) > 0, "gold daily_sales possui registros")
    assert_condition(len(product_sales) > 0, "gold product_sales possui registros")
    assert_condition(len(state_sales) > 0, "gold state_sales possui registros")

    invalid_quantities = order_items[order_items["quantity"] <= 0]
    assert_condition(len(invalid_quantities) == 0, "quantidades sao positivas")

    orphan_orders = orders[~orders["customer_id"].isin(customers["customer_id"])]
    assert_condition(len(orphan_orders) == 0, "todos os pedidos possuem cliente valido")

    orphan_items = order_items[~order_items["product_id"].isin(products["product_id"])]
    assert_condition(len(orphan_items) == 0, "todos os itens possuem produto valido")

    negative_revenue = product_sales[product_sales["revenue"] <= 0]
    assert_condition(len(negative_revenue) == 0, "receita gold e positiva")


if __name__ == "__main__":
    main()

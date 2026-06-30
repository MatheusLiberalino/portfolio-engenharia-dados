from __future__ import annotations

from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


PROJECT_DIR = Path(__file__).resolve().parents[1]
SILVER_DIR = PROJECT_DIR / "data" / "silver"
GOLD_DIR = PROJECT_DIR / "data" / "gold"


def get_spark() -> SparkSession:
    return (
        SparkSession.builder.appName("data-lake-quality-checks")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )


def assert_condition(condition: bool, message: str) -> None:
    status = "OK" if condition else "FAIL"
    print(f"{status} - {message}")
    if not condition:
        raise AssertionError(message)


def main() -> None:
    spark = get_spark()

    try:
        customers = spark.read.parquet(str(SILVER_DIR / "customers"))
        products = spark.read.parquet(str(SILVER_DIR / "products"))
        orders = spark.read.parquet(str(SILVER_DIR / "orders"))
        order_items = spark.read.parquet(str(SILVER_DIR / "order_items"))
        daily_sales = spark.read.parquet(str(GOLD_DIR / "daily_sales"))
        product_sales = spark.read.parquet(str(GOLD_DIR / "product_sales"))
        state_sales = spark.read.parquet(str(GOLD_DIR / "state_sales"))

        assert_condition(customers.count() > 0, "silver customers possui registros")
        assert_condition(products.count() > 0, "silver products possui registros")
        assert_condition(orders.count() > 0, "silver orders possui registros")
        assert_condition(order_items.count() > 0, "silver order_items possui registros")
        assert_condition(daily_sales.count() > 0, "gold daily_sales possui registros")
        assert_condition(product_sales.count() > 0, "gold product_sales possui registros")
        assert_condition(state_sales.count() > 0, "gold state_sales possui registros")

        invalid_quantities = order_items.filter(F.col("quantity") <= 0).count()
        assert_condition(invalid_quantities == 0, "quantidades sao positivas")

        orphan_orders = orders.join(customers, "customer_id", "left_anti").count()
        assert_condition(orphan_orders == 0, "todos os pedidos possuem cliente valido")

        orphan_items = order_items.join(products, "product_id", "left_anti").count()
        assert_condition(orphan_items == 0, "todos os itens possuem produto valido")

        negative_revenue = product_sales.filter(F.col("revenue") <= 0).count()
        assert_condition(negative_revenue == 0, "receita gold e positiva")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

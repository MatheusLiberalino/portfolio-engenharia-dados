from __future__ import annotations

from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
BRONZE_DIR = PROJECT_DIR / "data" / "bronze"
SILVER_DIR = PROJECT_DIR / "data" / "silver"
GOLD_DIR = PROJECT_DIR / "data" / "gold"


def get_spark() -> SparkSession:
    return (
        SparkSession.builder.appName("data-lake-pyspark-portfolio")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )


def write_parquet(dataframe, path: Path) -> None:
    dataframe.write.mode("overwrite").parquet(str(path))


def build_bronze(spark: SparkSession) -> dict[str, object]:
    datasets = {
        "customers": spark.read.json(str(RAW_DIR / "customers.json")),
        "products": spark.read.json(str(RAW_DIR / "products.json")),
        "orders": spark.read.json(str(RAW_DIR / "orders.json")),
        "order_items": spark.read.json(str(RAW_DIR / "order_items.json")),
    }

    for name, dataframe in datasets.items():
        write_parquet(dataframe, BRONZE_DIR / name)

    return datasets


def build_silver(spark: SparkSession) -> dict[str, object]:
    customers = (
        spark.read.parquet(str(BRONZE_DIR / "customers"))
        .dropDuplicates(["customer_id"])
        .withColumn("created_at", F.to_date("created_at"))
        .withColumn("email", F.lower("email"))
    )

    products = (
        spark.read.parquet(str(BRONZE_DIR / "products"))
        .dropDuplicates(["product_id"])
        .withColumn("unit_price", F.col("unit_price").cast("decimal(12,2)"))
    )

    orders = (
        spark.read.parquet(str(BRONZE_DIR / "orders"))
        .dropDuplicates(["order_id"])
        .withColumn("order_date", F.to_date("order_date"))
        .withColumn("ingestion_date", F.to_date("ingestion_date"))
    )

    order_items = (
        spark.read.parquet(str(BRONZE_DIR / "order_items"))
        .dropDuplicates(["order_item_id"])
        .withColumn("quantity", F.col("quantity").cast("integer"))
        .withColumn("unit_price", F.col("unit_price").cast("decimal(12,2)"))
        .withColumn("ingestion_date", F.to_date("ingestion_date"))
    )

    datasets = {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
    }

    for name, dataframe in datasets.items():
        write_parquet(dataframe, SILVER_DIR / name)

    return datasets


def build_gold(silver: dict[str, object]) -> None:
    customers = silver["customers"]
    products = silver["products"]
    orders = silver["orders"]
    order_items = silver["order_items"]

    sales = (
        order_items.join(orders, "order_id", "inner")
        .join(customers, "customer_id", "inner")
        .join(products, "product_id", "inner")
        .withColumn("gross_amount", F.col("quantity") * order_items["unit_price"])
    )

    daily_sales = (
        sales.groupBy("order_date")
        .agg(
            F.countDistinct("order_id").alias("orders"),
            F.sum("quantity").alias("units_sold"),
            F.round(F.sum("gross_amount"), 2).alias("revenue"),
        )
        .orderBy("order_date")
    )

    product_sales = (
        sales.groupBy("product_id", "product_name", "category")
        .agg(
            F.sum("quantity").alias("units_sold"),
            F.round(F.sum("gross_amount"), 2).alias("revenue"),
        )
        .orderBy(F.desc("revenue"))
    )

    state_sales = (
        sales.groupBy("state")
        .agg(
            F.countDistinct("order_id").alias("orders"),
            F.round(F.sum("gross_amount"), 2).alias("revenue"),
        )
        .orderBy(F.desc("revenue"))
    )

    write_parquet(daily_sales, GOLD_DIR / "daily_sales")
    write_parquet(product_sales, GOLD_DIR / "product_sales")
    write_parquet(state_sales, GOLD_DIR / "state_sales")


def main() -> None:
    spark = get_spark()
    try:
        build_bronze(spark)
        silver = build_silver(spark)
        build_gold(silver)
        print(f"Lakehouse built at: {PROJECT_DIR / 'data'}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

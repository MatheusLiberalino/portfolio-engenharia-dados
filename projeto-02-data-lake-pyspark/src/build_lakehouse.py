from __future__ import annotations

import shutil
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
from py4j.protocol import Py4JJavaError
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
        .master("local[2]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )


def write_parquet(dataframe, path: Path) -> None:
    try:
        dataframe.write.mode("overwrite").parquet(str(path))
    except Py4JJavaError as error:
        error_message = str(error)
        if "HADOOP_HOME" not in error_message and "winutils.exe" not in error_message:
            raise

        # Local Windows fallback for small portfolio datasets when winutils.exe is not installed.
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
        normalize_for_fastparquet(dataframe.toPandas()).to_parquet(
            path / "part-00000.parquet",
            engine="fastparquet",
            index=False,
        )


def normalize_for_fastparquet(dataframe: pd.DataFrame) -> pd.DataFrame:
    normalized = dataframe.copy()

    for column in normalized.columns:
        if normalized[column].dtype != "object":
            continue

        sample = normalized[column].dropna()
        if sample.empty:
            normalized[column] = normalized[column].astype(str)
            continue

        first_value = sample.iloc[0]
        if isinstance(first_value, Decimal):
            normalized[column] = normalized[column].astype(float)
        elif isinstance(first_value, (date, datetime)):
            normalized[column] = pd.to_datetime(normalized[column])
        else:
            normalized[column] = normalized[column].astype(str)

    return normalized


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


def build_silver(bronze: dict[str, object]) -> dict[str, object]:
    customers = (
        bronze["customers"]
        .dropDuplicates(["customer_id"])
        .withColumn("created_at", F.to_date("created_at"))
        .withColumn("email", F.lower("email"))
    )

    products = (
        bronze["products"]
        .dropDuplicates(["product_id"])
        .withColumn("unit_price", F.col("unit_price").cast("decimal(12,2)"))
    )

    orders = (
        bronze["orders"]
        .dropDuplicates(["order_id"])
        .withColumn("order_date", F.to_date("order_date"))
        .withColumn("ingestion_date", F.to_date("ingestion_date"))
    )

    order_items = (
        bronze["order_items"]
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
        bronze = build_bronze(spark)
        silver = build_silver(bronze)
        build_gold(silver)
        print(f"Lakehouse built at: {PROJECT_DIR / 'data'}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

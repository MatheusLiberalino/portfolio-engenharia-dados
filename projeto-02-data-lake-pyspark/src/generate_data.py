from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path


RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


CITIES = [
    ("Sao Paulo", "SP"),
    ("Rio de Janeiro", "RJ"),
    ("Belo Horizonte", "MG"),
    ("Curitiba", "PR"),
    ("Recife", "PE"),
    ("Porto Alegre", "RS"),
    ("Salvador", "BA"),
    ("Fortaleza", "CE"),
]

PRODUCTS = [
    ("Notebook Pro 14", "Eletronicos", 4899.90),
    ("Monitor 27", "Eletronicos", 1299.90),
    ("Teclado Mecanico", "Acessorios", 349.90),
    ("Mouse Wireless", "Acessorios", 159.90),
    ("Cadeira Ergonomica", "Moveis", 999.90),
    ("Mesa Ajustavel", "Moveis", 1499.90),
    ("Headset USB", "Acessorios", 229.90),
    ("Webcam Full HD", "Eletronicos", 279.90),
]


def write_json_lines(file_name: str, rows: list[dict]) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with (RAW_DIR / file_name).open("w", encoding="utf-8") as output:
        for row in rows:
            output.write(json.dumps(row, ensure_ascii=True) + "\n")


def build_customers(total: int = 120) -> list[dict]:
    customers = []

    for customer_id in range(1, total + 1):
        city, state = random.choice(CITIES)
        customers.append(
            {
                "customer_id": customer_id,
                "customer_name": f"Customer {customer_id:03d}",
                "email": f"customer{customer_id:03d}@email.com",
                "city": city,
                "state": state,
                "created_at": str(date(2024, 1, 1) + timedelta(days=random.randint(0, 365))),
            }
        )

    return customers


def build_products() -> list[dict]:
    return [
        {
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "unit_price": unit_price,
        }
        for product_id, (product_name, category, unit_price) in enumerate(PRODUCTS, start=1)
    ]


def build_orders(customers: list[dict], total: int = 500) -> tuple[list[dict], list[dict]]:
    orders = []
    order_items = []
    order_item_id = 1
    start_date = date(2025, 1, 1)

    for order_id in range(1, total + 1):
        customer = random.choice(customers)
        order_date = start_date + timedelta(days=random.randint(0, 364))
        status = random.choices(
            ["paid", "shipped", "delivered", "cancelled"],
            weights=[20, 30, 40, 10],
        )[0]

        orders.append(
            {
                "order_id": order_id,
                "customer_id": customer["customer_id"],
                "order_date": str(order_date),
                "status": status,
                "ingestion_date": str(date.today()),
            }
        )

        selected_products = random.sample(PRODUCTS, random.randint(1, 5))
        for product in selected_products:
            product_id = PRODUCTS.index(product) + 1
            order_items.append(
                {
                    "order_item_id": order_item_id,
                    "order_id": order_id,
                    "product_id": product_id,
                    "quantity": random.randint(1, 5),
                    "unit_price": product[2],
                    "ingestion_date": str(date.today()),
                }
            )
            order_item_id += 1

    return orders, order_items


def main() -> None:
    random.seed(42)

    customers = build_customers()
    products = build_products()
    orders, order_items = build_orders(customers)

    write_json_lines("customers.json", customers)
    write_json_lines("products.json", products)
    write_json_lines("orders.json", orders)
    write_json_lines("order_items.json", order_items)

    print(f"Raw data generated at: {RAW_DIR}")


if __name__ == "__main__":
    main()

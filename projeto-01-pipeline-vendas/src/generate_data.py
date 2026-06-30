from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path


RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


FIRST_NAMES = [
    "Ana",
    "Bruno",
    "Carla",
    "Diego",
    "Fernanda",
    "Gabriel",
    "Juliana",
    "Lucas",
    "Mariana",
    "Rafael",
]

LAST_NAMES = [
    "Silva",
    "Souza",
    "Oliveira",
    "Santos",
    "Pereira",
    "Costa",
    "Rodrigues",
    "Almeida",
    "Nascimento",
    "Lima",
]

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


def write_csv(file_name: str, fieldnames: list[str], rows: list[dict]) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with (RAW_DIR / file_name).open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_customers(total: int = 80) -> list[dict]:
    customers = []
    start_date = date(2024, 1, 1)

    for customer_id in range(1, total + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        city, state = random.choice(CITIES)
        full_name = f"{first_name} {last_name}"

        customers.append(
            {
                "customer_id": customer_id,
                "customer_name": full_name,
                "email": f"{first_name.lower()}.{last_name.lower()}{customer_id}@email.com",
                "city": city,
                "state": state,
                "created_at": start_date + timedelta(days=random.randint(0, 365)),
            }
        )

    return customers


def build_products() -> list[dict]:
    return [
        {
            "product_id": index,
            "product_name": product_name,
            "category": category,
            "unit_price": unit_price,
        }
        for index, (product_name, category, unit_price) in enumerate(PRODUCTS, start=1)
    ]


def build_orders(customers: list[dict], total: int = 300) -> tuple[list[dict], list[dict]]:
    orders = []
    order_items = []
    start_date = date(2025, 1, 1)
    order_item_id = 1

    for order_id in range(1, total + 1):
        customer = random.choice(customers)
        order_date = start_date + timedelta(days=random.randint(0, 364))
        status = random.choices(
            ["paid", "shipped", "delivered", "cancelled"],
            weights=[20, 25, 45, 10],
        )[0]

        orders.append(
            {
                "order_id": order_id,
                "customer_id": customer["customer_id"],
                "order_date": order_date,
                "status": status,
            }
        )

        selected_products = random.sample(PRODUCTS, random.randint(1, 4))
        for product_index, (_, _, unit_price) in enumerate(selected_products, start=1):
            product_id = PRODUCTS.index(selected_products[product_index - 1]) + 1
            order_items.append(
                {
                    "order_item_id": order_item_id,
                    "order_id": order_id,
                    "product_id": product_id,
                    "quantity": random.randint(1, 5),
                    "unit_price": unit_price,
                }
            )
            order_item_id += 1

    return orders, order_items


def main() -> None:
    random.seed(42)

    customers = build_customers()
    products = build_products()
    orders, order_items = build_orders(customers)

    write_csv(
        "customers.csv",
        ["customer_id", "customer_name", "email", "city", "state", "created_at"],
        customers,
    )
    write_csv(
        "products.csv",
        ["product_id", "product_name", "category", "unit_price"],
        products,
    )
    write_csv(
        "orders.csv",
        ["order_id", "customer_id", "order_date", "status"],
        orders,
    )
    write_csv(
        "order_items.csv",
        ["order_item_id", "order_id", "product_id", "quantity", "unit_price"],
        order_items,
    )

    print(f"Arquivos gerados em: {RAW_DIR}")


if __name__ == "__main__":
    main()

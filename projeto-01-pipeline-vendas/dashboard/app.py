from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_DIR / "data" / "sales_dw.sqlite"


st.set_page_config(
    page_title="Sales Data Warehouse",
    page_icon="bar_chart",
    layout="wide",
)


@st.cache_data
def load_sales_data() -> pd.DataFrame:
    query = """
        select
            f.sales_key,
            f.order_id,
            f.order_item_id,
            f.quantity,
            f.unit_price,
            f.gross_amount,
            f.status,
            d.full_date as order_date,
            d.year,
            d.month,
            c.customer_id,
            c.customer_name,
            c.city,
            c.state,
            p.product_id,
            p.product_name,
            p.category
        from fact_sales f
        join dim_date d on d.date_key = f.order_date_key
        join dim_customer c on c.customer_key = f.customer_key
        join dim_product p on p.product_key = f.product_key
    """

    with sqlite3.connect(DATABASE_PATH) as conn:
        dataframe = pd.read_sql_query(query, conn)

    dataframe["order_date"] = pd.to_datetime(dataframe["order_date"])
    dataframe["month_period"] = dataframe["order_date"].dt.to_period("M").astype(str)
    return dataframe


def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_number(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def show_empty_state() -> None:
    st.warning(
        "Banco SQLite nao encontrado. Execute `python src/run_pipeline_sqlite.py` antes de abrir o dashboard."
    )
    st.stop()


st.title("Sales Data Warehouse")
st.caption("Dashboard analitico construido sobre o modelo dimensional do pipeline de vendas.")

if not DATABASE_PATH.exists():
    show_empty_state()

sales = load_sales_data()

with st.sidebar:
    st.header("Filtros")

    min_date = sales["order_date"].min().date()
    max_date = sales["order_date"].max().date()
    start_date, end_date = st.date_input(
        "Periodo",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    states = sorted(sales["state"].unique())
    selected_states = st.multiselect("Estados", states, default=states)

    categories = sorted(sales["category"].unique())
    selected_categories = st.multiselect("Categorias", categories, default=categories)

    statuses = sorted(sales["status"].unique())
    selected_statuses = st.multiselect("Status", statuses, default=statuses)

filtered_sales = sales[
    (sales["order_date"].dt.date >= start_date)
    & (sales["order_date"].dt.date <= end_date)
    & (sales["state"].isin(selected_states))
    & (sales["category"].isin(selected_categories))
    & (sales["status"].isin(selected_statuses))
]

if filtered_sales.empty:
    st.info("Nenhuma venda encontrada para os filtros selecionados.")
    st.stop()

total_revenue = filtered_sales["gross_amount"].sum()
total_orders = filtered_sales["order_id"].nunique()
units_sold = filtered_sales["quantity"].sum()
average_ticket = total_revenue / total_orders if total_orders else 0

kpi_revenue, kpi_orders, kpi_ticket, kpi_units = st.columns(4)
kpi_revenue.metric("Receita", format_currency(total_revenue))
kpi_orders.metric("Pedidos", format_number(total_orders))
kpi_ticket.metric("Ticket medio", format_currency(average_ticket))
kpi_units.metric("Unidades vendidas", format_number(units_sold))

st.divider()

monthly_revenue = (
    filtered_sales.groupby("month_period", as_index=False)["gross_amount"]
    .sum()
    .sort_values("month_period")
)

category_revenue = (
    filtered_sales.groupby("category", as_index=False)["gross_amount"]
    .sum()
    .sort_values("gross_amount", ascending=False)
)

left_chart, right_chart = st.columns(2)

with left_chart:
    st.subheader("Receita por mes")
    st.line_chart(monthly_revenue, x="month_period", y="gross_amount")

with right_chart:
    st.subheader("Receita por categoria")
    st.bar_chart(category_revenue, x="category", y="gross_amount")

top_products = (
    filtered_sales.groupby("product_name", as_index=False)
    .agg(units_sold=("quantity", "sum"), revenue=("gross_amount", "sum"))
    .sort_values("revenue", ascending=False)
    .head(10)
)

state_revenue = (
    filtered_sales.groupby("state", as_index=False)["gross_amount"]
    .sum()
    .sort_values("gross_amount", ascending=False)
)

left_table, right_table = st.columns(2)

with left_table:
    st.subheader("Top 10 produtos")
    st.dataframe(
        top_products.rename(
            columns={
                "product_name": "Produto",
                "units_sold": "Unidades",
                "revenue": "Receita",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

with right_table:
    st.subheader("Receita por estado")
    st.bar_chart(state_revenue, x="state", y="gross_amount")

status_revenue = (
    filtered_sales.groupby("status", as_index=False)
    .agg(orders=("order_id", "nunique"), revenue=("gross_amount", "sum"))
    .sort_values("revenue", ascending=False)
)

st.subheader("Status dos pedidos")
st.dataframe(
    status_revenue.rename(
        columns={
            "status": "Status",
            "orders": "Pedidos",
            "revenue": "Receita",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

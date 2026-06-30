insert into dw.dim_customer (
    customer_id,
    customer_name,
    email,
    city,
    state,
    created_at
)
select
    customer_id,
    customer_name,
    email,
    city,
    state,
    created_at
from staging.customers
on conflict (customer_id) do update set
    customer_name = excluded.customer_name,
    email = excluded.email,
    city = excluded.city,
    state = excluded.state,
    created_at = excluded.created_at;

insert into dw.dim_product (
    product_id,
    product_name,
    category,
    unit_price
)
select
    product_id,
    product_name,
    category,
    unit_price
from staging.products
on conflict (product_id) do update set
    product_name = excluded.product_name,
    category = excluded.category,
    unit_price = excluded.unit_price;

insert into dw.dim_date (
    date_key,
    full_date,
    year,
    quarter,
    month,
    day,
    weekday
)
select distinct
    to_char(order_date, 'YYYYMMDD')::integer as date_key,
    order_date as full_date,
    extract(year from order_date)::integer as year,
    extract(quarter from order_date)::integer as quarter,
    extract(month from order_date)::integer as month,
    extract(day from order_date)::integer as day,
    extract(isodow from order_date)::integer as weekday
from staging.orders
on conflict (date_key) do nothing;

insert into dw.fact_sales (
    order_item_id,
    order_id,
    customer_key,
    product_key,
    order_date_key,
    quantity,
    unit_price,
    gross_amount,
    status
)
select
    oi.order_item_id,
    o.order_id,
    dc.customer_key,
    dp.product_key,
    dd.date_key,
    oi.quantity,
    oi.unit_price,
    oi.quantity * oi.unit_price as gross_amount,
    o.status
from staging.order_items oi
join staging.orders o on o.order_id = oi.order_id
join dw.dim_customer dc on dc.customer_id = o.customer_id
join dw.dim_product dp on dp.product_id = oi.product_id
join dw.dim_date dd on dd.full_date = o.order_date
on conflict (order_item_id) do update set
    order_id = excluded.order_id,
    customer_key = excluded.customer_key,
    product_key = excluded.product_key,
    order_date_key = excluded.order_date_key,
    quantity = excluded.quantity,
    unit_price = excluded.unit_price,
    gross_amount = excluded.gross_amount,
    status = excluded.status;

insert into dim_customer (
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
from customers;

insert into dim_product (
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
from products;

insert into dim_date (
    date_key,
    full_date,
    year,
    quarter,
    month,
    day,
    weekday
)
select distinct
    cast(replace(order_date, '-', '') as integer) as date_key,
    order_date as full_date,
    cast(strftime('%Y', order_date) as integer) as year,
    ((cast(strftime('%m', order_date) as integer) - 1) / 3) + 1 as quarter,
    cast(strftime('%m', order_date) as integer) as month,
    cast(strftime('%d', order_date) as integer) as day,
    cast(strftime('%w', order_date) as integer) as weekday
from orders;

insert into fact_sales (
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
    round(oi.quantity * oi.unit_price, 2) as gross_amount,
    o.status
from order_items oi
join orders o on o.order_id = oi.order_id
join dim_customer dc on dc.customer_id = o.customer_id
join dim_product dp on dp.product_id = oi.product_id
join dim_date dd on dd.full_date = o.order_date;

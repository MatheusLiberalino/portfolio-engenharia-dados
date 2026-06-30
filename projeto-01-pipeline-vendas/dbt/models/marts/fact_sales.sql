select
    oi.order_item_id as sales_key,
    oi.order_item_id,
    o.order_id,
    dc.customer_key,
    dp.product_key,
    dd.date_key as order_date_key,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price)::numeric(12, 2) as gross_amount,
    o.status
from {{ ref('stg_order_items') }} oi
join {{ ref('stg_orders') }} o
    on o.order_id = oi.order_id
join {{ ref('dim_customer') }} dc
    on dc.customer_id = o.customer_id
join {{ ref('dim_product') }} dp
    on dp.product_id = oi.product_id
join {{ ref('dim_date') }} dd
    on dd.full_date = o.order_date

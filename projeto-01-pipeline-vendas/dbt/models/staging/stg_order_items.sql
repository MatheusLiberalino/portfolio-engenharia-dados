select
    order_item_id,
    order_id,
    product_id,
    quantity::integer as quantity,
    unit_price::numeric(12, 2) as unit_price
from {{ source('sales_raw', 'order_items') }}

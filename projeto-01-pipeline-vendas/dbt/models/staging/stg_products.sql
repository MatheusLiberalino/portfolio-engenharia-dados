select
    product_id,
    product_name,
    category,
    unit_price::numeric(12, 2) as unit_price
from {{ source('sales_raw', 'products') }}

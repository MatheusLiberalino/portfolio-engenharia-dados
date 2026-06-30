select
    customer_id,
    customer_name,
    lower(email) as email,
    city,
    state,
    created_at::date as created_at
from {{ source('sales_raw', 'customers') }}

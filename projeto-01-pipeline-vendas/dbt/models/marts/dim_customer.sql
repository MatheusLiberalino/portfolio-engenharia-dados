select
    row_number() over (order by customer_id) as customer_key,
    customer_id,
    customer_name,
    email,
    city,
    state,
    created_at
from {{ ref('stg_customers') }}

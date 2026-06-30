select distinct
    to_char(order_date, 'YYYYMMDD')::integer as date_key,
    order_date as full_date,
    extract(year from order_date)::integer as year,
    extract(quarter from order_date)::integer as quarter,
    extract(month from order_date)::integer as month,
    extract(day from order_date)::integer as day,
    extract(isodow from order_date)::integer as weekday
from {{ ref('stg_orders') }}

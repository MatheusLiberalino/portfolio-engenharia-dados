select *
from {{ ref('fact_sales') }}
where gross_amount <> (quantity * unit_price)::numeric(12, 2)

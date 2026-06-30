select *
from {{ ref('fact_sales') }}
where gross_amount <= 0
   or quantity <= 0

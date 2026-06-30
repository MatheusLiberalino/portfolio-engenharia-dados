drop table if exists dw.fact_sales;
drop table if exists dw.dim_date;
drop table if exists dw.dim_product;
drop table if exists dw.dim_customer;

create table dw.dim_customer (
    customer_key integer generated always as identity primary key,
    customer_id integer not null unique,
    customer_name text not null,
    email text not null,
    city text not null,
    state text not null,
    created_at date not null
);

create table dw.dim_product (
    product_key integer generated always as identity primary key,
    product_id integer not null unique,
    product_name text not null,
    category text not null,
    unit_price numeric(12, 2) not null
);

create table dw.dim_date (
    date_key integer primary key,
    full_date date not null unique,
    year integer not null,
    quarter integer not null,
    month integer not null,
    day integer not null,
    weekday integer not null
);

create table dw.fact_sales (
    sales_key integer generated always as identity primary key,
    order_item_id integer not null unique,
    order_id integer not null,
    customer_key integer not null references dw.dim_customer(customer_key),
    product_key integer not null references dw.dim_product(product_key),
    order_date_key integer not null references dw.dim_date(date_key),
    quantity integer not null,
    unit_price numeric(12, 2) not null,
    gross_amount numeric(12, 2) not null,
    status text not null
);

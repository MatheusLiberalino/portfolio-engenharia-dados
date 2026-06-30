drop table if exists fact_sales;
drop table if exists dim_date;
drop table if exists dim_product;
drop table if exists dim_customer;
drop table if exists order_items;
drop table if exists orders;
drop table if exists products;
drop table if exists customers;

create table customers (
    customer_id integer primary key,
    customer_name text not null,
    email text not null,
    city text not null,
    state text not null,
    created_at text not null
);

create table products (
    product_id integer primary key,
    product_name text not null,
    category text not null,
    unit_price real not null
);

create table orders (
    order_id integer primary key,
    customer_id integer not null,
    order_date text not null,
    status text not null
);

create table order_items (
    order_item_id integer primary key,
    order_id integer not null,
    product_id integer not null,
    quantity integer not null,
    unit_price real not null
);

create table dim_customer (
    customer_key integer primary key autoincrement,
    customer_id integer not null unique,
    customer_name text not null,
    email text not null,
    city text not null,
    state text not null,
    created_at text not null
);

create table dim_product (
    product_key integer primary key autoincrement,
    product_id integer not null unique,
    product_name text not null,
    category text not null,
    unit_price real not null
);

create table dim_date (
    date_key integer primary key,
    full_date text not null unique,
    year integer not null,
    quarter integer not null,
    month integer not null,
    day integer not null,
    weekday integer not null
);

create table fact_sales (
    sales_key integer primary key autoincrement,
    order_item_id integer not null unique,
    order_id integer not null,
    customer_key integer not null,
    product_key integer not null,
    order_date_key integer not null,
    quantity integer not null,
    unit_price real not null,
    gross_amount real not null,
    status text not null,
    foreign key (customer_key) references dim_customer(customer_key),
    foreign key (product_key) references dim_product(product_key),
    foreign key (order_date_key) references dim_date(date_key)
);

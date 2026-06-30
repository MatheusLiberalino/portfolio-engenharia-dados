drop table if exists staging.order_items;
drop table if exists staging.orders;
drop table if exists staging.products;
drop table if exists staging.customers;

create table staging.customers (
    customer_id integer primary key,
    customer_name text not null,
    email text not null,
    city text not null,
    state text not null,
    created_at date not null
);

create table staging.products (
    product_id integer primary key,
    product_name text not null,
    category text not null,
    unit_price numeric(12, 2) not null
);

create table staging.orders (
    order_id integer primary key,
    customer_id integer not null,
    order_date date not null,
    status text not null
);

create table staging.order_items (
    order_item_id integer primary key,
    order_id integer not null,
    product_id integer not null,
    quantity integer not null,
    unit_price numeric(12, 2) not null
);

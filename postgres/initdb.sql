create schema commerce;

set search_path = commerce;

show search_path;

CREATE TABLE products (
    id int PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price REAL NOT NULL
);

CREATE TABLE users (
    id int PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

ALTER TABLE products
     REPLICA IDENTITY FULL;

ALTER TABLE users
     REPLICA IDENTITY FULL;

CREATE TABLE attributed_checkouts (
    checkout_id VARCHAR PRIMARY KEY,
    user_name VARCHAR,
    click_id VARCHAR,
    product_id VARCHAR,
    payment_method VARCHAR,
    total_amount DECIMAL(5, 2),
    shipping_address VARCHAR,
    billing_address VARCHAR,
    user_agent VARCHAR,
    ip_address VARCHAR,
    checkout_time TIMESTAMP,
    click_time TIMESTAMP
);

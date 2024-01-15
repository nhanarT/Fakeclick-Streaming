CREATE TEMPORARY TABLE users (
    id INT,
    username STRING,
    password STRING,
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = '{{ connector }}',
    'url' = '{{ url }}',
    'table-name' = '{{ table_name }}',
    'username' = '{{ username }}',
    'password' = '{{ password }}',
    'driver' = '{{ driver }}'
);

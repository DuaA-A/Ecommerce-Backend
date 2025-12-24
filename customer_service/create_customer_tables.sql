CREATE DATABASE customer_service;

CREATE USER 'customer_service'@'localhost'
IDENTIFIED BY 'Zatona99';

GRANT ALL PRIVILEGES ON customer_service.*
TO 'customer_service'@'localhost';

FLUSH PRIVILEGES;

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    loyalty_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    password_hash VARCHAR(255) NOT NULL
);
drop table customers;
SHOW DATABASES;
USE customer_service;
SHOW TABLES;

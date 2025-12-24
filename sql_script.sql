-- Create DB
CREATE DATABASE IF NOT EXISTS ecommerce_system;
USE ecommerce_system;

-- customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    loyalty_points INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- inventory
CREATE TABLE IF NOT EXISTS inventory (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL,
    quantity_available INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- pricing_rules
CREATE TABLE IF NOT EXISTS pricing_rules (
    rule_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    min_quantity INT,
    discount_percentage DECIMAL(5,2),
    CONSTRAINT fk_pricing_product FOREIGN KEY (product_id) REFERENCES inventory(product_id)
);

-- tax_rates
CREATE TABLE IF NOT EXISTS tax_rates (
    region VARCHAR(50) PRIMARY KEY,
    tax_rate DECIMAL(5,2)
);

-- notification_log
CREATE TABLE IF NOT EXISTS notification_log (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    customer_id INT,
    notification_type VARCHAR(50),
    message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--  orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    total_amount DECIMAL(12,2),
    status VARCHAR(50) DEFAULT 'created',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

--  order_items table (store products & qty per order)
CREATE TABLE IF NOT EXISTS order_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2),
    CONSTRAINT fk_items_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_items_product FOREIGN KEY (product_id) REFERENCES inventory(product_id)
);

-- Sample seed data
INSERT INTO inventory (product_name, quantity_available, unit_price)
VALUES ('Laptop',50,999.99),('Mouse',200,29.99),('Keyboard',150,79.99),('Monitor',75,299.99),('Headphones',100,149.99);

INSERT INTO customers (name, email, phone, loyalty_points)
VALUES ('Ahmed Hassan','ahmed@example.com','01012345678',100),
       ('Sara Mohamed','sara@example.com','01098765432',250),
       ('Omar Ali','omar@example.com','01055555555',50);

INSERT INTO pricing_rules (product_id, min_quantity, discount_percentage)
VALUES (1,5,10.00),(2,10,15.00),(3,10,12.00);

INSERT INTO tax_rates (region, tax_rate)
VALUES ('Cairo',14.00),('Giza',14.00),('Alexandria',14.00);

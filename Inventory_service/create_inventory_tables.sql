CREATE USER 'inventory_service'@'localhost'
IDENTIFIED WITH mysql_native_password
BY 'Zatona99';

GRANT ALL PRIVILEGES ON inventory_service.* 
TO 'inventory_service'@'localhost';
FLUSH PRIVILEGES;
SELECT user, host FROM mysql.user
WHERE user = 'inventory_service';
CREATE DATABASE IF NOT EXISTS inventory_service;
USE inventory_service;
select * from inventory;
CREATE TABLE IF NOT EXISTS inventory (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL,
    quantity_available INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    last_updated TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO inventory (product_name, quantity_available, unit_price)
VALUES
('Laptop', 50, 999.99),
('Mouse', 200, 29.99),
('Keyboard', 150, 79.99),
('Monitor', 75, 299.99),
('Headphones', 100, 149.99);

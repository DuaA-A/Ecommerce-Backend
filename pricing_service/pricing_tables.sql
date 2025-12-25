CREATE DATABASE pricing_service;

CREATE USER 'pricing_service'@'localhost'
IDENTIFIED BY 'Zatona99';

GRANT ALL PRIVILEGES ON pricing_service.*
TO 'pricing_service'@'localhost';

FLUSH PRIVILEGES;

use pricing_service;

CREATE TABLE IF NOT EXISTS pricing_rules (
    rule_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    min_quantity INT,
    discount_percentage DECIMAL(5,2),
    CONSTRAINT fk_pricing_product FOREIGN KEY (product_id) REFERENCES inventory_service.inventory(product_id)
);

CREATE TABLE IF NOT EXISTS tax_rates (
    region VARCHAR(50) PRIMARY KEY,
    tax_rate DECIMAL(5,2)
);

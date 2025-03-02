CREATE DATABASE IF NOT EXISTS sales_data;
USE sales_data;

CREATE TABLE IF NOT EXISTS processed_sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(50),
    product_id VARCHAR(50),
    quantity INT,
    price DECIMAL(10, 2),
    total_amount DECIMAL(10, 2),
    order_date VARCHAR(50),
    process_date DATE,
    report_key VARCHAR(255)
);

-- Create a user with necessary permissions
CREATE USER IF NOT EXISTS 'sales_user'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON sales_data.* TO 'sales_user'@'%';
FLUSH PRIVILEGES; 
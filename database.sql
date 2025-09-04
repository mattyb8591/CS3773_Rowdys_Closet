CREATE DATABASE rc_db;
USE rc_db;

CREATE TABLE products(
  productID int PRIMARY KEY,
  productName VARCHAR(50),
  numInStock int,
  price DECIMAL(10,2)
);

INSERT INTO products(productID, productName, numInStock, price) VALUES 
(1, 'Jeans', 45, 59.99),
(2, 'Khakis', 67, 30.99),
(3, 'T-shirt', 23, 19.99),
(4, 'Hoodie', 44, 25.99),
(5, 'Shoes', 56, 80.99);

SELECT * FROM products;


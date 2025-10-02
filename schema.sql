USE rowdys_closet_db;

CREATE TABLE products(
  productID int PRIMARY KEY,
  productName VARCHAR(50),
  numInStock int,
  price DECIMAL(10,2),
  rating DEcIMAL(2,1)
);

CREATE TABLE accounts(
  accountID int AUTO_INCREMENT PRIMARY KEY,
  userName VARCHAR(50),
  passwordHash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products(productID, productName, numInStock, price, rating) VALUES 
(1, 'Jeans', 45, 59.99, 4.5),
(2, 'Khakis', 67, 30.99, 1.1),
(3, 'T-shirt', 23, 19.99, 3.9),
(4, 'Hoodie', 44, 25.99, 5.0),
(5, 'Shoes', 56, 80.99, 4.8);


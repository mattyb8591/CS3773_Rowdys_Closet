
USE rowdys_closet_db;

CREATE TABLE IF NOT EXISTS addresses(
  address_id INT PRIMARY KEY AUTO_INCREMENT,
  city VARCHAR(50) NOT NULL,
  state_abrev VARCHAR(2) NOT NULL,
  zip_code INT NOT NULL
);

CREATE TABLE IF NOT EXISTS users(
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  password VARCHAR(50) NOT NULL,
  email VARCHAR(25) NOT NULL,
  phone_number VARCHAR(20),
  address_id INT,
  FOREIGN KEY (address_id) references addresses(address_id)
);

CREATE TABLE IF NOT EXISTS cart_products(
  cart_product_id INT PRIMARY KEY AUTO_INCREMENT,
  cart_id INT NOT NULL,
  product_id INT NOT NULL,
  FOREIGN KEY (cart_id) REFERENCES carts(cart_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS customers(
  customer_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS admins(
  admin_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS products(
  product_id INT PRIMARY KEY AUTO_INCREMENT,
  price DECIMAL(10,2) NOT NULL,
  size  VARCHAR(5) NOT NULL,
  name VARCHAR(50) NOT NULL,
  stock INT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders(
  order_id INT PRIMARY KEY AUTO_INCREMENT,
  total DECIMAL(10,2) NOT NULL,
  discount_code VARCHAR(50),
  order_status VARCHAR(20) NOT NULL,
  order_date DATE NOT NULL,
  customer_id INT NOT NULL,
  cart_product_id INT NOT NULL,
  payment_id INT NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (cart_product_id) REFERENCES cart_products(cart_product_id),
  FOREIGN KEY (payment_id) REFERENCES payments(payment_id)
);

CREATE TABLE IF NOT EXISTS payments(
  payment_id INT PRIMARY KEY AUTO_INCREMENT,
  payment_type VARCHAR(20) NOT NULL,
  details VARCHAR(200) NOT NULL,
  status VARCHAR(20) NOT NULL,
  customer_id INT NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS carts(
  cart_id INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

SELECT * FROM admins;

SELECT * FROM users;

ALTER TABLE products
ADD type varchar(25);

INSERT INTO admins (user_id) VALUES (2);

ALTER TABLE products
ADD description varchar(500);

SELECT * FROM addresses;

SELECT user_id FROM users WHERE username = 'mattyb';

ALTER TABLE products
ADD img_file_path varchar(500);

ALTER TABLE users
ADD img_profile_path varchar(500);

ALTER TABLE products
MODIFY stock INT NOT NULL DEFAULT 0;

ALTER TABLE addresses
MODIFY COLUMN street_name VARCHAR(100);

ALTER TABLE users
ADD account_type varchar(50);

ALTER TABLE products
MODIFY COLUMN size VARCHAR(10);

ALTER TABLE products
MODIFY COLUMN name VARCHAR(100);

SELECT * FROM users;

SELECT * FROM customers

SELECT * FROM carts;

SELECT * FROM users;

SELECT u.user_id, 
      u.username, 
      u.email, 
      u.phone_number, 
      CONCAT(a.street_number, " ", a.street_name, ", ", a.city, ", ", a.state_abrev, " ", a.zip_code) AS full_address,
      CASE WHEN ad.user_id IS NOT NULL THEN 'Admin' ELSE 'Customer' END AS user_role
    FROM users u
    LEFT JOIN addresses a ON u.address_id = a.address_id
    LEFT JOIN admins ad ON u.user_id = ad.user_id
    ORDER BY u.user_id DESC;
-- Create a new MySQL user
CREATE USER 'auth_user'@'localhost' IDENTIFIED BY 'Auth123';

-- Create the database
CREATE DATABASE auth;

-- Grant privileges to the new user
GRANT ALL PRIVILEGES ON auth.* TO 'auth_user'@'localhost';

-- Use the 'auth' database
USE auth;

-- Create the 'user' table
CREATE TABLE user (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Insert a sample user
INSERT INTO user (email, password) VALUES ('user@mail.com', '11223344');

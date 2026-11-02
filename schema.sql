-- Chitrabaddh database setup
-- Run once:  mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS chitrabaddh
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE chitrabaddh;

CREATE TABLE IF NOT EXISTS users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    phone       VARCHAR(15)  NOT NULL,
    password    VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

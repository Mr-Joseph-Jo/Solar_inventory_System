CREATE DATABASE IF NOT EXISTS solar_inventory;
USE solar_inventory;

-- Users
CREATE TABLE users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('owner', 'admin', 'sales') NOT NULL DEFAULT 'sales',
    active        TINYINT(1) NOT NULL DEFAULT 1,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Company settings (one row only)
CREATE TABLE company_settings (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    gstin        VARCHAR(20),
    address      TEXT,
    phone        VARCHAR(20),
    email        VARCHAR(100),
    bank_name    VARCHAR(100),
    account_no   VARCHAR(50),
    ifsc         VARCHAR(20),
    branch       VARCHAR(100),
    pin_code     VARCHAR(10)
);

-- Inventory
CREATE TABLE inventory_items (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(150) NOT NULL,
    category   VARCHAR(100) NOT NULL,
    hsn_code   VARCHAR(20),
    unit       VARCHAR(20),
    price      DECIMAL(10,2) NOT NULL DEFAULT 0,
    gst_rate   DECIMAL(5,2)  NOT NULL DEFAULT 0,
    quantity   INT           NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sales
CREATE TABLE sales (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    invoice_no     VARCHAR(50)    NOT NULL UNIQUE,
    sold_by        INT            NOT NULL,
    gst_applied    TINYINT(1)     NOT NULL DEFAULT 0,
    subtotal       DECIMAL(10,2)  NOT NULL DEFAULT 0,
    gst_amount     DECIMAL(10,2)  NOT NULL DEFAULT 0,
    total_amount   DECIMAL(10,2)  NOT NULL DEFAULT 0,
    invoice_file   VARCHAR(255),
    buyer_name     VARCHAR(150),
    buyer_address  TEXT,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sold_by) REFERENCES users(id)
);

-- Sale line items
CREATE TABLE sale_items (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    sale_id    INT           NOT NULL,
    item_id    INT           NOT NULL,
    quantity   INT           NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    gst_rate   DECIMAL(5,2)  NOT NULL DEFAULT 0,
    gst_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    line_total DECIMAL(10,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (sale_id) REFERENCES sales(id),
    FOREIGN KEY (item_id) REFERENCES inventory_items(id)
);

-- Audit log
CREATE TABLE audit_logs (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT,
    role       VARCHAR(20),
    action     VARCHAR(100),
    details    TEXT,
    ip_address VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed: company settings row (always id=1)
INSERT INTO company_settings (company_name) VALUES ('Green INN Solutions');

-- Seed: owner account (password: change this immediately after first login)
INSERT INTO users (name, username, password_hash, role)
VALUES (
    'Owner',
    'owner',
    -- This is the hash for "changeme123" — change it immediately
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TiGSn5QkrGQsVVWL6OvKn5E8gu8.',
    'owner'
);
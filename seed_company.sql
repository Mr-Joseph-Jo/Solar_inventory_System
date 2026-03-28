-- Run this once after creating the database to prepopulate company details
-- from the Green INN Solutions template.

UPDATE company_settings SET
    company_name = 'Green INN Solutions',
    address      = "PONMANI'S BUILDING, North Junction, CHALAKUDY, THRISSUR(DT), Kerala - 680307",
    phone        = '7034952000 and 9447222610',
    gstin        = '32AGTPJ4296N1ZN',
    email        = '',
    bank_name    = 'South Indian Bank',
    account_no   = '0065073000000358',
    ifsc         = 'SIBL0000065',
    branch       = 'Pariyaram, Kerala',
    pin_code     = '680721'
WHERE id = 1;


-- GST rates table — add this to your DB setup
CREATE TABLE IF NOT EXISTS gst_rates (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    rate       DECIMAL(5,2) NOT NULL UNIQUE
);

-- Default rates matching the template
INSERT IGNORE INTO gst_rates (rate) VALUES (0), (2.5), (6), (9), (14), (18), (28);

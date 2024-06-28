USE APPLICATION PACKAGE {{package_name}};

CREATE SCHEMA IF NOT EXISTS shared_data;
USE SCHEMA shared_data;
CREATE TABLE IF NOT EXISTS accounts (ID INT, NAME VARCHAR, VALUE VARCHAR);
TRUNCATE TABLE accounts;
INSERT INTO accounts VALUES
  (1, 'Joe', 'Snowflake'),
  (2, 'Nima', 'Snowflake'),
  (3, 'Sally', 'Snowflake'),
  (4, 'Juan', 'Acme');
-- grant usage on the ``ACCOUNTS`` table
GRANT USAGE ON SCHEMA shared_data TO SHARE IN APPLICATION PACKAGE {{package_name}};
GRANT SELECT ON TABLE accounts TO SHARE IN APPLICATION PACKAGE {{package_name}};
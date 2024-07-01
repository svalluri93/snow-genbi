USE APPLICATION PACKAGE {{package_name}};

CREATE SCHEMA IF NOT EXISTS shared_data;
USE SCHEMA shared_data;

create or replace table shared_data.NAV_DATA as select * from ML_APP.ML_MODELS.NAV_DATA;

-- grant usage on the ``ACCOUNTS`` table
GRANT USAGE ON SCHEMA shared_data TO SHARE IN APPLICATION PACKAGE {{package_name}};
GRANT SELECT ON TABLE NAV_DATA TO SHARE IN APPLICATION PACKAGE {{package_name}};
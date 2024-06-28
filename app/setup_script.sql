-- Setup script for the Hello Snowflake! app.

CREATE APPLICATION ROLE IF NOT EXISTS invstintl_app_role;
CREATE SCHEMA IF NOT EXISTS core;
GRANT USAGE ON SCHEMA core TO APPLICATION ROLE invstintl_app_role;

CREATE OR REPLACE PROCEDURE CORE.HELLO()
  RETURNS STRING
  LANGUAGE SQL
  EXECUTE AS OWNER
  AS
  BEGIN
    RETURN 'Hello Snowflake!';
  END;

GRANT USAGE ON PROCEDURE core.hello() TO APPLICATION ROLE invstintl_app_role;


CREATE OR ALTER VERSIONED SCHEMA code_schema;
GRANT USAGE ON SCHEMA code_schema TO APPLICATION ROLE invstintl_app_role;


CREATE VIEW IF NOT EXISTS code_schema.accounts_view
  AS SELECT ID, NAME, VALUE
  FROM shared_data.accounts;
GRANT SELECT ON VIEW code_schema.accounts_view TO APPLICATION ROLE invstintl_app_role;

CREATE OR REPLACE FUNCTION code_schema.open_ai_api(sentence STRING)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = 3.11
IMPORTS = ('/python/open_ai_func.py')
HANDLER = 'open_ai_func.get_response'
EXTERNAL_ACCESS_INTEGRATIONS = (openai_ext_access_int)
PACKAGES = ('openai')
SECRETS = ('cred' = open_ai_api )

GRANT USAGE ON FUNCTION code_schema.open_ai_api(STRING) TO APPLICATION ROLE invstintl_app_role;
-- Setup script for the Hello Snowflake! app.
CREATE APPLICATION ROLE IF NOT EXISTS invstintl_app_role;
CREATE OR ALTER VERSIONED SCHEMA code_schema;
GRANT USAGE ON SCHEMA code_schema TO APPLICATION ROLE invstintl_app_role;


CREATE VIEW IF NOT EXISTS code_schema.NAV_DATA
  AS SELECT *
  FROM shared_data.NAV_DATA;
GRANT SELECT ON VIEW code_schema.NAV_DATA TO APPLICATION ROLE invstintl_app_role;

CREATE OR REPLACE PROCEDURE code_schema.init_app(config variant)
  RETURNS string
  LANGUAGE python
  runtime_version = '3.8'
  packages = ('snowflake-snowpark-python', 'openai', 'simplejson')
  imports = ('/python/open_ai_func.py')
  handler = 'open_ai_func.init_app';

GRANT USAGE ON PROCEDURE code_schema.init_app(variant) TO APPLICATION ROLE invstintl_app_role;

CREATE OR REPLACE FUNCTION code_schema.open_ai_api(sentence STRING)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = 3.11
IMPORTS = ('/python/open_ai_func.py')
HANDLER = 'open_ai_func.get_response'
PACKAGES = ('snowflake-snowpark-python','openai','simplejson');

GRANT USAGE ON FUNCTION code_schema.open_ai_api(STRING) TO APPLICATION ROLE invstintl_app_role;


create or replace procedure code_schema.update_reference(ref_name string, operation string, ref_or_alias string)
returns string
language sql
as $$
begin
  case (operation)
    when 'ADD' then
       select system$set_reference(:ref_name, :ref_or_alias);
    when 'REMOVE' then
       select system$remove_reference(:ref_name, :ref_or_alias);
    when 'CLEAR' then
       select system$remove_all_references(:ref_name);
    else
       return 'Unknown operation: ' || operation;
  end case;
  return 'Success';
end;
$$;

grant usage on procedure code_schema.update_reference(string, string, string) to application role invstintl_app_role;
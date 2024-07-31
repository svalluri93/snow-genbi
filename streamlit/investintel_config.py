import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import json

st.title("CREDENTIALS CONFIGURATION")

session = get_active_session()

def main():
    try:
        check_data = "SELECT SECRET_NAME, EXT_ACCESS_INTEGRATION_NAME FROM CORE.CRED_DATA"
        result = session.sql(check_data).to_pandas()

        # st.write("Columns in result DataFrame:", result.columns.tolist())
        st.write("Data in result DataFrame:", result)
        
        st.write('Do you want to proceed with existing credentials or do you want to update')
        option = st.radio('Choose an option', ('proceed with existing credentials', 'update'))

        if option == 'proceed with existing credentials':
            proceed = st.button("Proceed")
            if proceed:
                if not result.empty:
                    if 'SECRET_NAME' in result.columns and 'EXT_ACCESS_INTEGRATION_NAME' in result.columns:
                        secret_name = result.iloc[0]['SECRET_NAME']
                        external_access_integration_name = result.iloc[0]['EXT_ACCESS_INTEGRATION_NAME']
                        
                        data = {
                            'secret_name': secret_name,
                            'external_access_integration_name': external_access_integration_name
                        }
                        json_data = json.dumps(data)
                        update_open_ai_func_query = f"CALL investintel.code_schema.init_app(PARSE_JSON('{json_data}'));"
                        session.sql(update_open_ai_func_query).collect()
                        st.write('Credentials initialized. Please navigate to investintel_sql')
                    else:
                        st.write('Expected columns are missing in the result.')
                else:
                    st.write('No existing credentials found. Initializing with default credentials.')
                    default_credentials_query = """
                    CALL INVESTINTEL.code_schema.init_app(PARSE_JSON('{
                        "secret_name": "ML_APP.ML_MODELS.open_ai_api",
                        "external_access_integration_name": "openai_ext_access_int"
                    }'));
                    """
                    session.sql(default_credentials_query).collect()
                    st.write('Default credentials initialized. Please navigate to investintel_sql')

        elif option == 'update':
            with st.form(key='update_form'):
                secret_name = st.text_input('Secret Name')
                external_access_integration_name = st.text_input('External access integration name')

                submitted = st.form_submit_button("Submit")

                if submitted:
                    try:
                        insert_query = f"""
                        INSERT OVERWRITE INTO CORE.CRED_DATA(SECRET_NAME, EXT_ACCESS_INTEGRATION_NAME) 
                        VALUES ('{secret_name}', '{external_access_integration_name}')
                        """
                        session.sql(insert_query).collect()
                        
                        data = {
                            'secret_name': secret_name,
                            'external_access_integration_name': external_access_integration_name
                        }
                        json_data = json.dumps(data)
                        update_open_ai_func_query = f"CALL investintel.code_schema.init_app(PARSE_JSON('{json_data}'));"
                        session.sql(update_open_ai_func_query).collect()

                        st.write('Data saved. Please navigate to investintel_sql')
                        st.write('Refresh the current webpage to check the latest credentials')
                    except Exception as e:
                        st.write('An error occurred:', e)
                        st.write('Please make sure you have given the necessary permissions to the app for accessing secret and external integration.')
    except Exception as e:
        st.write('An error occurred while fetching credentials:', e)

if __name__ == "__main__":
    main()

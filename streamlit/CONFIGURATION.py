import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import json

st.title("CREDENTIALS CONFIGURATION")

session = get_active_session()


def func_init(secret_name,external_access_integration_name,insert = False):

    data = {'secret_name': secret_name,'external_access_integration_name': external_access_integration_name}
    json_data = json.dumps(data)
    update_open_ai_func_query = f"CALL investintel.code_schema.init_app(PARSE_JSON('{json_data}'));"
    session.sql(update_open_ai_func_query).collect()

    if insert == True:
        
        insert_query = f"""INSERT OVERWRITE INTO CORE.CRED_DATA(SECRET_NAME, EXT_ACCESS_INTEGRATION_NAME) 
                    VALUES ('{secret_name}', '{external_access_integration_name}')"""
        session.sql(insert_query).collect()


def main():
    try:
        check_data = "SELECT SECRET_NAME, EXT_ACCESS_INTEGRATION_NAME FROM CORE.CRED_DATA"
        result = session.sql(check_data).to_pandas()

        # st.write("Columns in result DataFrame:", result.columns.tolist())
        st.write("Current Configuration:", result)

        if result.empty:
            with st.form(key='update_form_1'):
                secret_name = st.text_input('Secret Name')
                external_access_integration_name = st.text_input('External access integration name')

                submitted_1 = st.form_submit_button("Submit")

            if submitted_1:
                try:
                    func_init(secret_name,external_access_integration_name,insert = True)
                    st.write('Data saved. Please navigate to investintel')
                    st.write('Refresh the current webpage to check the updated credentials')
                except Exception as e:
                    st.write('An error occurred:', e)
                    st.write('Please make sure you have given the necessary permissions to the app for accessing secret and external integration.')

        


        if not result.empty:
            

            #secret_name = result['secret_name'].iloc[0]
            secret_name = result['SECRET_NAME'].values[0]
            external_access_integration_name = result['EXT_ACCESS_INTEGRATION_NAME'].values[0]
            #external_access_integration_name = result['secret_name'].iloc[0]

            func_init(secret_name,external_access_integration_name)

            st.write('Credentials initialized , please navigate to investintel page or update your existing credentials by submitting below form')

            with st.form(key='update_form_2'):
                secret_name = st.text_input('Secret Name')
                external_access_integration_name = st.text_input('External access integration name')

                submitted_2 = st.form_submit_button(label="Submit")

                if submitted_2:
                    try:
                        func_init(secret_name,external_access_integration_name,insert = True)
                        st.write('Data saved. Please navigate to investintel')
                        st.write('Refresh the current webpage to check the updated credentials')
  
                    except Exception as e:
                        st.write('An error occurred:', e)
                        st.write('Please make sure you have given the necessary permissions to the app for accessing secret and external integration.')
    except Exception as e:
        st.write('An error occurred while fetching credentials:', e)

if __name__ == "__main__":
    main()

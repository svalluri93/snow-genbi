import streamlit as st
#from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
import pandas as pd
import json


# def init_app(session):
#     init_statement = """
#     CALL INVESTINTEL.code_schema.init_app(PARSE_JSON('{
#     "secret_name": "ML_APP.ML_MODELS.open_ai_api",
#     "external_access_integration_name": "openai_ext_access_int"
#     }'));
#     """
#     session.sql(init_statement).execute()

st.title("CREDENTIALS CONFIGURATION")

session = get_active_session()

def main():

    check_data = f"SELECT secret_name, ext_access_integration_name FROM CORE.CRED_DATA"
    result = session.sql(check_data).to_pandas()
    st.write(result, use_container_width=True)

    st.write('Do you want to proceed with existing credentials or do you want to update')
    option = st.radio('choose an option', ('proceed with existing credentials', 'update'))

    if option == 'proceed with existing credentials':
        if st.button('Proceed'):
            st.write('Please navigate to investintel_sql')

    elif option == 'update':
        with st.form(key='update_form'):
            secret_name = st.text_input('Secret Name')
            external_access_integration_name = st.text_input('External access integration name')
            
            #df = pd.DataFrame({"secret_name": secret_name, "ext_access_integration_name": external_access_integration_name }, index=[0])

            #snowpark_df = session.create_dataframe(data=df)

            submitted = st.form_submit_button("Submit")

            if submitted:

                try:                    

                    insert_query = f"INSERT OVERWRITE INTO CORE.CRED_DATA(secret_name, ext_access_integration_name) VALUES ('{secret_name}', '{external_access_integration_name}')"
                    df = session.sql(insert_query)
                    data = {}
                    data['secret_name'] = secret_name
                    data['external_access_integration_name'] = external_access_integration_name
                    json_data = json.dumps(data)
                    update_open_ai_func_query = f"call investintel.code_schema.init_app(PARSE_JSON('" + json_data + f"'));"

                    app_init = session.sql(update_open_ai_func_query)
                    #df = session.sql(update_open_ai_func_query)
                    #session.sql('')
                    st.dataframe(df, use_container_width=True)
                    st.write('Data saved.Please navigate to investintel_sql')
                    st.write('Refresh the current webpage to check latest credentials')
                except:
                    st.write('Please make sure you have given the necessary permissions to the app for accessing secret and external integration.')
                        


if __name__ == "__main__":
    main()







   
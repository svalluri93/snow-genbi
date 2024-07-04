import streamlit as st
from snowflake.snowpark import Session

st.title("Investintel Streamlit App")
st.write(
   """The following data is from the accounts table in the application package.
      However, the Streamlit app queries this data from a view called
      code_schema.accounts_view.
   """
)

def fetch_credentials(session):
    query = "SELECT secret_name, ext_access_integration_name FROM CORE.CRED_DATA"
    result = session.sql(query).to_pandas()
    return result

def update_credentials(session, secret_name, external_access_integration_name):
    query = f"""CALL INVESTINTEL.code_schema.init_app(PARSE_JSON(
        '{{
            "secret_name": "{secret_name}",
            "external_access_integration_name": "{external_access_integration_name}"
        }}'
        ));"""
    session.sql(query)

def main():
    session = Session.builder.getOrCreate()
    
    # Fetch existing credentials
    credentials_df = fetch_credentials(session)
    
    if not credentials_df.empty:
        st.write("Existing credentials:")
        st.dataframe(credentials_df, use_container_width=True)
        
        # Display form to update credentials
        with st.form(key='update_credentials_form'):
            if 'secret_name' in credentials_df.columns and 'ext_access_integration_name' in credentials_df.columns:
                secret_name = credentials_df.iloc[0]['secret_name']
                external_access_integration_name = credentials_df.iloc[0]['ext_access_integration_name']
            else:
                secret_name = ""
                external_access_integration_name = ""
            
            st.subheader("Update Credentials")
            new_secret_name = st.text_input("New Secret Name", value=secret_name)
            new_ext_access_integration_name = st.text_input("New External Access Integration Name", value=external_access_integration_name)
            
            submit_button = st.form_submit_button("Update Credentials")
            
            if submit_button:
                update_credentials(session, new_secret_name, new_ext_access_integration_name)
                st.success('Credentials updated successfully.')
                
                # Fetch updated credentials
                updated_credentials_df = fetch_credentials(session)
                st.write("Updated credentials:")
                st.dataframe(updated_credentials_df, use_container_width=True)
                
    
    else:
        st.warning("No credentials found.")
 
if __name__ == "__main__":
    main()
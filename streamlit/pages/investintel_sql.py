import streamlit as st
import re
import pandas as pd
from snowflake.snowpark.context import get_active_session

# Initialize the Snowflake session
session = get_active_session()

# Define the template for SQL query generation
GEN_SQL = """
You will be acting as an AI Snowflake SQL expert named GenSQL.
Your goal is to give correct, executable SQL queries to users.
You will be replying to users who will be confused if you don't respond in the character of GenSQL.
You are given a table with its respective columns.
The user will ask questions; for each question, you should respond and include a SQL query based on the question and the table provided to you. 

<tableName> NAV_DATA </tableName> columns are: <columns> DATE, FUND_NAME, ISIN_DIV_PAYOUT_GROWTH, ISIN_DIV_REINVESTMENT, NET_ASSET_VALUE, SCHEME_CODE, SCHEME_NAME </columns>

Here are 6 critical rules for the interaction you must abide:
<rules>
1. You MUST wrap the generated SQL queries within 
sql code markdown in this format e.g
sql
(select 1) union (select 2)
2. If I don't tell you to find a limited set of results in the sql query or question, you MUST limit the number of responses to 10.
3. Text / string where clauses must be fuzzy match e.g ilike %keyword%
4. Make sure to generate a single Snowflake SQL code snippet, not multiple. 
5. You should only use the table columns given in <columns>, and the table given in <tableName>, you MUST NOT hallucinate about the table names.
6. DO NOT put numerical at the very front of SQL variable.
</rules>

Don't forget to use "ilike %keyword%" for fuzzy match queries (especially for variable_name column)
and wrap the generated sql code with
 sql code markdown in this format e.g:
sql
(select 1) union (select 2)

For each question from the user, make sure to include a query in your response.
"""

# Function to retrieve column metadata and generate the context
@st.cache_data(show_spinner=False)
def get_cols():
    table = "NAV_DATA"
    columns = pd.DataFrame(session.sql(f"""
    SELECT COLUMN_NAME FROM INVESTINTEL.INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = '{table}';
    """).collect())
    cols_metadata = ",".join(columns['COLUMN_NAME'])
    op = f"""
    <tableName> {table} <tableName> columns are: <columns> {cols_metadata} <columns>
    """
    return GEN_SQL.format(context=op)

# Function to escape single quotes in the prompt
def escape_single_quotes(text):
    return text.replace("'", "''")

# Streamlit app main function
if __name__ == "__main__":
    st.title("SQL Generator")

    # Prompt for user input and save
    if prompt := st.text_input("Ask Something"):
        # Generate the prompt for OpenAI API
        open_ai_prompt = f"""
        Based on the following context:
        {get_cols()}
        The user asked: {escape_single_quotes(prompt)}
        Please generate a relevant SQL query.
        """
        open_ai_resp_query = f"SELECT INVESTINTEL.CODE_SCHEMA.OPEN_AI_API('{escape_single_quotes(open_ai_prompt)}');"

        # Execute the OpenAI API function
        try:
            open_ai_response = session.sql(open_ai_resp_query).collect()
            open_ai_content = open_ai_response[0][0]  # Assuming the response content is returned in the first column of the first row

            # Check if the response contains a SQL query
            sql_match = re.search(r"```sql\n(.*)\n```", open_ai_content, re.DOTALL)
            if sql_match:
                generated_sql_query = sql_match.group(1).strip()  # Strip to remove any leading/trailing whitespace

                # Display the generated SQL query without a label
                st.markdown(f"```sql\n{generated_sql_query}\n```")

                # Execute the generated SQL query and display the results
                results = session.sql(generated_sql_query).to_pandas()
                st.dataframe(results)
            else:
                # If it's a general response, display it as text
                st.write(open_ai_content)

        except Exception as e:
            st.write(f"Error executing the generated SQL query: {e}")

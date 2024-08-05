import streamlit as st
import re
import pandas as pd
from snowflake.snowpark.context import get_active_session

session = get_active_session()

def escape_single_quotes(prompt):
    return prompt.replace("'", "''")

def get_response(session, sentence):
    open_ai_prompt = f"""Generate Python Code Script. The script should only include code. no comments.
    When generating Python code ensure that you do not include Markdown formatting backticks within the script.
    Simply write the Python code directly without any backticks. based on the following description: "{sentence}",
    please Use the Relevant Streamlit Function.do not use st.pyplot(fig) use st.@my_chart() adjest as per chart type and you can add lable as well. 
    you can use st.map() as well.for pie charts only use fig = go.Figure(...) st.write(fig)"""
    open_ai_resp_query = f"SELECT INVESTINTEL.CODE_SCHEMA.OPEN_AI_API('{escape_single_quotes(open_ai_prompt)}');"
    result = session.sql(open_ai_resp_query).collect()
    res = result[0][0]  
    return res

def format_response(res):
    csv_line = res.find("read_csv")
    if csv_line > 0:
        return_before_csv_line = res[0:csv_line].rfind("\n")
        if return_before_csv_line == -1:
            res_before = ""
        else:
            res_before = res[0:return_before_csv_line]
        res_after = res[csv_line:]
        return_after_csv_line = res_after.find("\n")
        if return_after_csv_line == -1:
            res_after = ""
        else:
            res_after = res_after[return_after_csv_line:]
        res = res_before + res_after
    return res

def format_question(primer_desc, primer_code, question):
    return '"""\n' + primer_desc + question + '\n"""\n' + primer_code

def get_primer(df_dataset, df_name):
    primer_desc = f"Use a dataframe called {df_name} with columns '" \
        + "','".join(str(x) for x in df_dataset.columns) + "'. "
    for i in df_dataset.columns:
        if len(df_dataset[i].drop_duplicates()) < 20 and df_dataset.dtypes[i] == "O":
            primer_desc = primer_desc + "\nThe column '" + i + "' has categorical values '" + \
                "','".join(str(x) for x in df_dataset[i].drop_duplicates()) + "'. "
        elif df_dataset.dtypes[i] == "int64" or df_dataset.dtypes[i] == "float64":
            primer_desc = primer_desc + "\nThe column '" + i + "' is type " + str(df_dataset.dtypes[i]) + " and contains numeric values. "
    primer_desc = primer_desc + "\nLabel the x and y axes appropriately."
    primer_desc = primer_desc + "\nAdd a title. Set the fig suptitle as empty."
    primer_desc = primer_desc + "\nUsing Python version 3.9.12, create a script using the dataframe df to graph the following: "
    primer_code = "import pandas as pd\nimport matplotlib.pyplot as plt\n"
    primer_code = primer_code + "fig,ax = plt.subplots(1,1,figsize=(10,4))\n"
    primer_code = primer_code + "ax.spines['top'].set_visible(False)\nax.spines['right'].set_visible(False) \n"
    primer_code = primer_code + f"df = {df_name}.copy()\n"
    return primer_desc, primer_code

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

def escape_single_quotes(text):
    return text.replace("'", "''")

# Streamlit app main function
if __name__ == "__main__":
    st.title("SQL Generator")
    if 'snowflake_session' not in st.session_state:
        st.session_state.snowflake_session = None

    if prompt := st.text_input("Ask Something"):
        open_ai_prompt = f"""
        Based on the following context:
        {get_cols()}
        The user asked: {escape_single_quotes(prompt)}
        Please generate a relevant SQL query.
        """
        open_ai_resp_query = f"SELECT INVESTINTEL.CODE_SCHEMA.OPEN_AI_API('{escape_single_quotes(open_ai_prompt)}');"

        if st.session_state.snowflake_session is None:
            st.write("Initializing Snowflake session...")
            st.session_state.snowflake_session = get_active_session()

        # Execute the OpenAI API function
        try:
            if "GenSQL_op_df" not in st.session_state:
                open_ai_response = session.sql(open_ai_resp_query).collect()
                open_ai_content = open_ai_response[0][0]

                sql_match = re.search(r"```sql\n(.*)\n```", open_ai_content, re.DOTALL)
                if sql_match:
                    generated_sql_query = sql_match.group(1).strip()

                    st.markdown(f"```sql\n{generated_sql_query}\n```")

                    results = session.sql(generated_sql_query).to_pandas()

                    st.session_state.GenSQL_op_df = results

                    st.dataframe(results)
                # if "GenSQL_op_df" not in st.session_state:
                #     st.error('Run query in investintel sql to visualize')
                # else:
                #     datasets = st.session_state["GenSQL_op_df"]
                #     # st.dataframe(datasets)
            datasets = st.session_state["GenSQL_op_df"]
            chart_types = ["Bar Chart", "Line Chart", "Pie Chart","Area Chart","Histogram"]
            selected_chart = st.selectbox("What would you like to visualize?", chart_types)
            go_btn = st.button("Go...")

            if go_btn:
                try:
                    primer_desc, primer_code = get_primer(datasets, 'datasets')
                    question_to_ask = format_question(primer_desc, primer_code, selected_chart)

                    answer = get_response(session, question_to_ask)
                    answer = primer_code + answer

                            # st.markdown("### Generated Python Code:")     # remove comment to see generated python code for charts
                            # st.code(answer, language='python')            # remove comment to see generated python code for charts

                    local_vars = {"datasets": datasets}
                    try:
                        exec(answer, {"__builtins__": __builtins__}, local_vars)
                    except Exception as e:
                        st.error(f"Error executing the generated code: {e}")

                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.write(open_ai_content)

        except Exception as e:
            st.write(f"Error executing the generated SQL query: {e}")

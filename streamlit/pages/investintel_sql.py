import streamlit as st
import re
import pandas as pd
from snowflake.snowpark.context import get_active_session

session = get_active_session()

GEN_SQL = """
You will be acting as an AI Snowflake SQL expert named GenSQL.
Your goal is to give correct, executable SQL queries to users.
You will be replying to users who will be confused if you don't respond in the character of GenSQL.
You are given multiple tables with their respective columns.
The user will ask questions; for each question, you should respond and include a SQL query based on the question and the tables provided to you. 

{context}

Here are 6 critical rules for the interaction you must abide:
<rules>
1. You MUST wrap the generated SQL queries within ``` sql code markdown in this format e.g
```sql
(select 1) union (select 2)
```
2. If I don't tell you to find a limited set of results in the sql query or question, you MUST limit the number of responses to 10.
3. Text / string where clauses must be fuzzy match e.g ilike %keyword%
4. Make sure to generate a single Snowflake SQL code snippet, not multiple. 
5. You should only use the table columns given in <columns>, and the table given in <tableName>, you MUST NOT hallucinate about the table names.
6. DO NOT put numerical at the very front of SQL variable.
</rules>

Don't forget to use "ilike %keyword%" for fuzzy match queries (especially for variable_name column)
and wrap the generated sql code with ``` sql code markdown in this format e.g:
```sql
(select 1) union (select 2)
```

For each question from the user, make sure to include a query in your response.

Now to get started, please briefly introduce yourself, show the list of tables available to you , and share the available metrics in 2-3 sentences.
"""

@st.cache_data(show_spinner=False)
def get_cols():

    tables = ["NAV_DATA"]

    op = "Tables are given below : \n"
    for j in tables:
        
        columns = pd.DataFrame(session.sql(f"""
        SELECT COLUMN_NAME FROM INVESTINTEL.INFORMATION_SCHEMA.COLUMNS
        Where TABLE_NAME ='{j}';
        """,
        ).collect())
    
        cols_metadata = ",".join(
                        [
                f"{columns['COLUMN_NAME'][j]}"
                for j in range(len(columns["COLUMN_NAME"]))
                        ]
                                )
        op = op + f"\n <tableName> {j} <tableName>" + " columns are: <columns>" + cols_metadata + " <columns> \n"
        
    return GEN_SQL.format(context=op)


if __name__ == "__main__":

    st.title("SQL Generator")

    if "messages" not in st.session_state:

        st.session_state.messages = [{"role": "system", "content": get_cols()}]

    # Prompt for user input and save
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        open_ai_resp_query = f"select INVESTINTEL.CODE_SCHEMA.OPEN_AI_API('"+ prompt + f"');"
    # display the existing chat messages
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "results" in message:
                st.dataframe(message["results"])

    # If last message is not from assistant, we need to generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response = ""
            resp_container = st.empty()
            for chunk in client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            ):
                #response += delta.choices[0].delta.get("content", "")
                if chunk.choices[0].delta.content is not None:
                    response += chunk.choices[0].delta.content
                    resp_container.markdown(response)
            
            open_ai_resp_query = f"select INVESTINTEL.CODE_SCHEMA.OPEN_AI_API('tell me a joke');"


            message = {"role": "assistant", "content": response}
            # Parse the response for a SQL query and execute if available
            sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
            if sql_match:
                sql = sql_match.group(1)
                message["results"] = pd.DataFrame(session.sql(sql).collect())
                st.dataframe(message["results"])
                st.session_state["GenSQL_op_df"] = message["results"]
            st.session_state.messages.append(message)
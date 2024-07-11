import streamlit as st
import pandas as pd

from snowflake.snowpark.context import get_active_session

session = get_active_session()

def escape_single_quotes(prompt):
    return prompt.replace("'", "''")

# def get_response(session, sentence):
#     open_ai_prompt = f"""Generate Python Code Script. The script should only include code, no comments.Generate Python code to create a chart based on the following description: "{sentence}"""
#     open_ai_resp_query = f"SELECT INVESTINTEL.CODE_SCHEMA.OPEN_AI_API('{escape_single_quotes(open_ai_prompt)}');"
#     result = session.sql(open_ai_resp_query).collect()
#     res = result[0][0]  # Assuming the response directly provides Python code for charting
#     return res



def get_response(session, sentence):
    open_ai_prompt = f"""Generate Python Code Script. The script should only include code. no comments.Generate Python code to create a chart based on the following description: "{sentence}". 
    and show code as well.When generating Python code that combines these two parts, ensure that you do not include Markdown formatting backticks within the script. Simply write the Python code directly without any backticks"""
    open_ai_resp_query = f"SELECT INVESTINTEL.CODE_SCHEMA.OPEN_AI_API('{escape_single_quotes(open_ai_prompt)}');"
    result = session.sql(open_ai_resp_query).collect()
    res = result[0][0]  # Assuming the response directly provides Python code for charting
    return res

def format_response( res):
    # Remove the load_csv from the answer if it exists
    csv_line = res.find("read_csv")
    if csv_line > 0:
        return_before_csv_line = res[0:csv_line].rfind("\n")
        if return_before_csv_line == -1:
            # The read_csv line is the first line so there is nothing to need before it
            res_before = ""
        else:
            res_before = res[0:return_before_csv_line]
        res_after = res[csv_line:]
        return_after_csv_line = res_after.find("\n")
        if return_after_csv_line == -1:
            # The read_csv is the last line
            res_after = ""
        else:
            res_after = res_after[return_after_csv_line:]
        res = res_before + res_after
    return res

def format_question(primer_desc,primer_code , question):
    # Put the question at the end of the description primer within quotes, then add on the code primer.
    return  '"""\n' + primer_desc + question + '\n"""\n' + primer_code

def get_primer(df_dataset,df_name):
    # Primer function to take a dataframe and its name
    # and the name of the columns
    # and any columns with less than 20 unique values it adds the values to the primer
    # and horizontal grid lines and labeling
    primer_desc = "Use a dataframe called df from data_file.csv with columns '" \
        + "','".join(str(x) for x in df_dataset.columns) + "'. "
    for i in df_dataset.columns:
        if len(df_dataset[i].drop_duplicates()) < 20 and df_dataset.dtypes[i]=="O":
            primer_desc = primer_desc + "\nThe column '" + i + "' has categorical values '" + \
                "','".join(str(x) for x in df_dataset[i].drop_duplicates()) + "'. "
        elif df_dataset.dtypes[i]=="int64" or df_dataset.dtypes[i]=="float64":
            primer_desc = primer_desc + "\nThe column '" + i + "' is type " + str(df_dataset.dtypes[i]) + " and contains numeric values. "   
    primer_desc = primer_desc + "\nLabel the x and y axes appropriately."
    primer_desc = primer_desc + "\nAdd a title. Set the fig suptitle as empty."
    primer_desc = primer_desc + "\nUsing Python version 3.9.12, create a script using the dataframe df to graph the following: "
    pimer_code = "import pandas as pd\nimport matplotlib.pyplot as plt\n"
    pimer_code = pimer_code + "fig,ax = plt.subplots(1,1,figsize=(10,4))\n"
    pimer_code = pimer_code + "ax.spines['top'].set_visible(False)\nax.spines['right'].set_visible(False) \n"
    pimer_code = pimer_code + "df=" + df_name + ".copy()\n"
    return primer_desc,pimer_code

def main():
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.set_page_config(layout="wide", page_title="vizAI")
    st.markdown("<h1 style='text-align: center; font-weight:bold; font-family:comic sans ms; padding-top: 0rem;'>VizAI</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;padding-top: 0rem;'>Creating Visualisations using Natural Language with ChatGPT</h2>", unsafe_allow_html=True)

    if "GenSQL_op_df" not in st.session_state:
        st.error('Run query in GenSQL to visualize')
    else:
        datasets = st.session_state["GenSQL_op_df"]
        st.dataframe(datasets)

    question = st.text_area(":eyes: What would you like to visualise?", height=10)
    go_btn = st.button("Go...")

    if go_btn:
        try:
            primer_desc, primer_code = get_primer(datasets, 'datasets')
            question_to_ask = format_question(primer_desc, primer_code, question)

            # Ensure session is correctly passed to get_response function
            answer = get_response(session, question_to_ask)
            answer = primer_code + answer  # Prepend primer_code to the generated Python code
            
            st.markdown("### Generated Python Code:")
            st.code(answer, language='python')
            # Execute the generated Python code
            local_vars = {}
            try:
                exec(answer, {"__builtins__": __builtins__}, local_vars)
            except Exception as e:
                st.error(f"Error executing the generated code: {e}")

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

session = get_active_session()

def escape_single_quotes(prompt):
    return prompt.replace("'", "''")

def get_response(session, sentence):
    open_ai_prompt = f"""Generate Python Code Script. The script should only include code. no comments. When generating Python code ensure that you do not include Markdown formatting backticks within the script. Simply write the Python code directly without any backticks. based on the following description: "{sentence}",
    please Use the Relevant Streamlit Function. i dont want to use st.pyplot(fig) use st.@my_chart() adjest as per chart type and you can add lable as well. you can use st.map() this as well."""
    open_ai_resp_query = f"SELECT INVESTINTEL.CODE_SCHEMA.OPEN_AI_API('{escape_single_quotes(open_ai_prompt)}');"
    result = session.sql(open_ai_resp_query).collect()
    res = result[0][0]  # Assuming the response directly provides Python code for charting
    return res
# please Use the Relevant Streamlit Function. Streamlit provides various functions to display different types of charts insted of st.pyplot(fig) use st.@my_chart(data=None, *, x=None, y=None, x_label=None, y_label=None, color=None, horizontal=False, width=None, height=None, use_container_width=True) adjest as per chart type and you can remove lable as well if not needed.
#     i want to disply this in streamlit snowflake native app please use supported display method for showing charts.
#      dont use st.pyplot(fig)
# Generate Python code to create a chart 
# using "matplotlib.pyplot" directly instead of assigning it to the alias "plt" like "matplotlib.pyplot.subplots"
# Streamlit provides various functions to display different types of charts insted of st.pyplot(fig) use st.@my_chart(data=None, *, x=None, y=None, x_label=None, y_label=None, color=None, horizontal=False, width=None, height=None, use_container_width=True) adjest as per chart type and you can remove lable as well if not needed.
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


def get_primer(df_dataset, df_name):
    primer_desc = f"Use a dataframe called {df_name} with columns '" \
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
    primer_code = "import pandas as pd\nimport matplotlib.pyplot as plt\n"
    primer_code = primer_code + "fig,ax = plt.subplots(1,1,figsize=(10,4))\n"
    primer_code = primer_code + "ax.spines['top'].set_visible(False)\nax.spines['right'].set_visible(False) \n"
    primer_code = primer_code + f"df = {df_name}.copy()\n"  # Correctly use df_name to reference dataframe
    return primer_desc, primer_code


def main():
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.set_page_config(layout="wide", page_title="vizAI")

    if "GenSQL_op_df" not in st.session_state:
        st.error('Run query in GenSQL to visualize')
    else:
        datasets = st.session_state["GenSQL_op_df"]
        st.dataframe(datasets)

    question = st.text_area(":eyes: What would you like to visualise?", height=10)
    go_btn = st.button("Go...")

    if go_btn:
        # primer_desc, primer_code = get_primer(datasets, 'datasets')  # Pass datasets and its name
        # question_to_ask = format_question(primer_desc, primer_code, question)
        try:
            
            primer_desc, primer_code = get_primer(datasets, 'datasets')
            question_to_ask = format_question(primer_desc, primer_code, question)

            # Ensure session is correctly passed to get_response function
            answer = get_response(session, question_to_ask)
            answer = primer_code + answer  # Prepend primer_code to the generated Python code
            
            st.markdown("### Generated Python Code:")
            st.code(answer, language='python')
            
            
            local_vars = {"datasets": datasets}  # Include datasets in local_vars
            try:
                exec(answer, {"__builtins__": __builtins__}, local_vars)
            except Exception as e:
                st.error(f"Error executing the generated code: {e}")
            

            # Run the question
            
            
            # answer = primer_code + answer
            # plot_area = st.empty()
            # plot_area.pyplot(exec(answer))
            
            # Execute the generated Python code
            # local_vars = {"datasets": datasets}  # Include datasets in local_vars
            # try:
            #     exec(answer, {"__builtins__": __builtins__}, local_vars)
            # except Exception as e:
            #     st.error(f"Error executing the generated code: {e}")
            # plot_area.pyplot(local_vars["fig"])

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()

# 1)Create a function to generate the plot  and return it as a base64 encoded image.2)Import matplotlib.pyplot within the function. 3)Convert plot to PNG image in memory. 4) Encode PNG image to base64 string 5)return image_base64. 6)Get the base64 encoded image. 7)Generate HTML to display the image. 8)Display the image in your Streamlit app 8) solved name 'plt' is not defined isuee and rewrite code
# 9) insted of BytesIO use tempfile











# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np

# def main():
#     st.set_page_config(layout="wide", page_title="Streamlit Line Chart Example")

#     # Simulate a DataFrame with 'date' and 'NET_ASSET_VALUE' columns
#     data = {
#         'date': pd.date_range(start='2023-01-01', periods=10),
#         'NET_ASSET_VALUE': np.random.randint(1000, 1500, 10)  # Random values for demonstration
#     }
#     df = pd.DataFrame(data)

#     # Display the DataFrame
#     st.write("### Simulated Dataset:")
#     st.dataframe(df)

#     # Visualization section
#     st.write("### Visualization:")

#     # Create a basic line chart
#     fig, ax = plt.subplots()
#     ax.plot(df['date'], df['NET_ASSET_VALUE'])
#     ax.set_xlabel('Date')
#     ax.set_ylabel('NET ASSET VALUE')
#     ax.set_title('Line Chart of NET ASSET VALUE over Time')

#     # Display the chart in Streamlit
#     st.pyplot(fig)

# if __name__ == "__main__":
#     main()


# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt

# # Sample data
# data = {
#     'Category': ['Category A', 'Category B', 'Category C'],
#     'Values': [30, 50, 20]
# }

# # Convert data to DataFrame
# df = pd.DataFrame(data)

# # Title of the web app
# st.title('Pie Chart Example')

# # Pie chart
# fig, ax = plt.subplots()
# ax.pie(df['Values'], labels=df['Category'], autopct='%1.1f%%', startangle=90)
# ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
# st.pyplot(fig)





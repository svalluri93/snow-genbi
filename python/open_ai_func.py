import _snowflake
from openai import OpenAI
import json
import simplejson as json
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session

from snowflake.snowpark import Row
import pandas as pd


def init_app(session: Session, config) -> str:
  """
    Initializes function API endpoints with access to the secret and API integration.

    Args:
      session (Session): An active session object for authentication and communication.
      config (Any): The configuration settings for the connector.

    Returns:
      str: A status message indicating the result of the provisioning process.
   """
  secret_name = config['secret_name']
  external_access_integration_name = config['external_access_integration_name']

  alter_function_sql = f'''
    ALTER FUNCTION code_schema.open_ai_api(STRING) SET 
    SECRETS = ('cred' = {secret_name}) 
    EXTERNAL_ACCESS_INTEGRATIONS = ({external_access_integration_name})'''
  
  session.sql(alter_function_sql).collect()

  return 'Snowflake genbi app initialized'

def chat(client,system, user_assistant):
    assert isinstance(system, str), "`system` should be a string"
    assert isinstance(user_assistant, list), "`user_assistant` should be a list"
    system_msg = [{"role": "system", "content": system}]
    user_assistant_msgs = [
      {"role": "assistant", "content": user_assistant[i]} if i % 2 else {"role": "user", "content": user_assistant[i]}
      for i in range(len(user_assistant))]
 
    msgs = system_msg + user_assistant_msgs
  #for delay_secs in (2**x for x in range(0, 6)):
    try:
        completion = client.chat.completions.create(model="gpt-4o",
                                          messages=msgs,
                                          temperature=0,  # Control the randomness of the generated response
                                          n=1,  # Generate a single response
                                          stop=None )
    except client.OpenAIError as e:
        return "Failed to fetch response from OpenAI"

    return completion.choices[0].message.content

def get_response(sentence): 
    
    secret_object = _snowflake.get_generic_secret_string('cred')

    client = OpenAI( api_key = str(secret_object) )

    prompt = """ Answer questions asked by user """
    response_fn_test = chat(client,prompt,['''question is  - ''' + '''"''' + sentence + '''"'''+ '''.'''])
    return response_fn_test




import _snowflake
from openai import OpenAI
import json

secret_object = _snowflake.get_generic_secret_string('cred')

client = OpenAI( api_key = str(secret_object) )

prompt = """ Answer questions asked by user """

def chat(system, user_assistant):
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

    response_fn_test = chat(prompt,['''question is  - ''' + '''"''' + sentence + '''"'''+ '''.'''])
    return response_fn_test

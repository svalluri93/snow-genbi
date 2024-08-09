# INVESTINTEL

## Introduction


Investintel is a powerful tool designed to provide the latest information on large-cap mutual funds in the Indian capital market. Users can ask questions in natural language, which are then translated into SQL queries using OpenAI's capabilities. The results of these queries are instantly returned, offering precise and up-to-date data. Additionally, the platform allows users to visualize the results without writing any code. With Investintel, users can easily access critical metrics such as the Net Asset Value (NAV) of specific schemes, essential for assessing fund performance.

## Description

### Business Benefits

#### Query data using Natural Language

  User queries in natural language are seamlessly converted into SQL queries, making it easy for business users to access and analyze data without requiring technical expertise.

#### Up to date information

  The latest data for all large-cap funds is available daily by 9:00 A.M. IST. 

#### Inbuilt Visualization

  The application also has the capability to generate visualizations without the need for writing any code.

#### Zero development

  The client does not have to handle any development activities as it is entirely handled by the NSEIT team.


## Application configuration

### Please follow the below instructions for configuring the Investintel application:

1.) Create a network rule using the below query which will allow snowflake to access OpenAI endpoint

```
CREATE OR REPLACE NETWORK RULE OPENAI_NETWORK_RULE
 MODE = EGRESS
 TYPE = HOST_PORT
 VALUE_LIST = ('api.openai.com');

```

2.) create a secret which contains your OpenAI API KEY. Use the below query to create the same, place your key inside single quotes of SECRET_STRING variable.

```
CREATE OR REPLACE SECRET SAMPLE_DB.SAMPLE_SCHEMA.OPENAI_SECRET
 TYPE = GENERIC_STRING
 SECRET_STRING = '';

```

3.) Create an external access integration object using below Query,which will allow network traffic from snowflake to OpenAI.
    Make sure to set the value of ALLOWED_NETWORK_RULES to the object created in step 1 and value of ALLOWED_AUTHENTICATION_SECRETS to the 
    object created in step 2

```
 CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION SAMPLE_DB.SAMPLE_SCHEMA.OPENAI_EXT_ACCESS_INT
 ALLOWED_NETWORK_RULES = (OPENAI_NETWORK_RULE)
 ALLOWED_AUTHENTICATION_SECRETS = (SAMPLE_DB.SAMPLE_SCHEMA.OPENAI_SECRET)
 ENABLED = true;

```

4.)Provide access for the application to access the objects created in steps 1,2,3 by running below queries.
   Below Queries needs to be executed after every re-installation.

```
GRANT USAGE ON DATABASE SAMPLE_DB TO APPLICATION INVESTINTEL;                                                   --- Database where the secret and external access integration are created
GRANT USAGE ON SCHEMA SAMPLE_DB.SAMPLE_SCHEMA TO APPLICATION INVESTINTEL;                                       --- Schema where the secret and external access integration are created
GRANT USAGE ON INTEGRATION SAMPLE_DB.SAMPLE_SCHEMA.OPENAI_EXT_ACCESS_INT TO APPLICATION INVESTINTEL;
GRANT READ ON SECRET SAMPLE_DB.SAMPLE_SCHEMA.OPENAI_SECRET TO APPLICATION INVESTINTEL;

```

5.) Once the application is installed navigate to the configuration page of the streamlit application and input the secret object created in step 2 and external access integration object created in step 3. 
     

## Sample Questions

1.) which schemes had the best avg NAV since last year

2.) show me top 5 schemes with highest NAV as per latest date
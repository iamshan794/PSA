from google.adk.agents import LlmAgent
from google.adk.tools import google_search,load_artifacts
from google.adk.tools.agent_tool import AgentTool

from .utils.get_tree import get_schema_tree
from .utils.product_retrieval import html_to_text_h2t, retrieve_products_from_api

class agent_definition:

    schema_agent = LlmAgent(
    name="schema_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to obtain JSON schema from schema.org from user input."
    ),
    instruction=(
        '''You are a helpful agent that retrieves JSON schema from schema.org based on input.
            1. Use the get_schema_tree function to obtain the list of all possible products.
            2. Find the exact or closest match to the input product name from the schema tree.
            3. Return the finalized product name to the root agent.
            '''
    ),
    tools=[get_schema_tree, load_artifacts],
    )
    
    research_agent=LlmAgent(
    name="product_research_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to frame questions based on given JSON schema."
    ),
    instruction=(
        '''You are an AI agent to help the customer buy a product. Do the following:

            1. Use the google_search tool to obtain JSON schema of product.
            2. Select X key attributes that maximize product performance. They could also be 
            key variables that act as filters for the product search.
            (X could any number, but keep it simple)
            3. Return the follow-up questions to the user based on the selected attributes.
            '''
    ),
    tools=[google_search],
    )

    api_sub_agent_1=LlmAgent(
    name="query_param_optimizer",
    model="gemini-2.0-flash",
    description=(
        "Agent that optimizes a query param given a JSON schema."
    ),
    instruction=(
        '''You are an AI agent that uses JSON schema to modify the API query to retrieve most relevant products.   
        1. Use the html_to_text_h2t tool to obtain rubrics to design the querystring variable used for the API call.
        Be aware of syntaxes and case sensitivity of the API query parameters.
        2. Call API to obtain JSON object of products.
        3. Process the API result and show it as collection of product cards similar to an e-commerce website.
        4. If the API call fails, investigate and try one last time after informing the user about the failure.
        '''
    ),
    tools=[html_to_text_h2t,retrieve_products_from_api],  # Assuming retrieve_products_from_api is defined elsewhere
    )

    root_agent = LlmAgent(
    name="product_identifier_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent that identifies product and extracts product information through questions given a product."
    ),
    instruction=(
        '''You are an AI agent to help the customer buy a product.  Ask the following questions as soon as you know what item the user
        is looking for. These are essential questions to help the user find the right product.

        1.Budget Range
        2.User's Location  
        3.Available Date 
        4.Other user comments
        5. Product condition? Options: New, Used, or Refurbished

        Do the following in the background:
        1. Use the schema_agent to obtain the product category once product is known from user. 
        2. Use the product_research_agent to obtain follow-up questions according to the context.            
        3. Based on chat history, autofill the questions if the user has not provided answers. 

        Save the JSON schema of the product in the same schema.org format. Transfer control to corresponding sub-agent to retrieve products from API.
            '''
    ),
    tools=[AgentTool(agent=schema_agent), AgentTool(agent=research_agent)],
    sub_agents=[
        api_sub_agent_1,
    ],
)
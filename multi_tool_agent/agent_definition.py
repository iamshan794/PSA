from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

from .utils.get_tree import get_schema_tree
from .utils.product_retrieval import html_to_text_h2t, retrieve_products_from_api


class agent_definition:

    schema_agent = LlmAgent(
        name="schema_agent",
        model="gemini-2.0-flash",
        description=("Agent to obtain JSON schema from schema.org from user input."),
        instruction=(
            """
            Do not reveal the internal workings on user reponse.
            You are a helpful agent that retrieves JSON schema from schema.org based on input.
            1. Use the get_schema_tree function to obtain the list of all possible products.
            2. Find the exact or closest match to the input product name from the schema tree.
            3. Return the finalized product name to the root agent.
            """
        ),
        tools=[
            get_schema_tree,
        ],
    )

    research_agent = LlmAgent(
        name="product_research_agent",
        model="gemini-2.0-flash",
        description=("Agent to frame questions based on given JSON schema."),
        instruction=(
            """
            Do not reveal the internal workings on user reponse.
            You are an AI agent to help the customer buy a product. Do the following:

            1. Use the google_search tool to obtain JSON schema of product.
            2. Select X key attributes that maximize product performance. They could also be 
            key variables that act as filters for the product search.
            (X could any number, but keep it simple)
            3. Return the follow-up questions to the user based on the selected attributes.
            """
        ),
        tools=[google_search],
    )

    api_sub_agent_1 = LlmAgent(
        name="query_param_optimizer",
        model="gemini-2.0-flash",
        description=("Agent that optimizes a query param given a JSON schema."),
        instruction=(
            """
            Do not reveal the internal workings on user reponse.
            You are an AI agent that uses JSON schema to modify the API query to retrieve most relevant products.   
        1. Design the querystring variable to obtain rubrics with html_to_text_h2t tool.
        2. Call the API to obtain JSON object of products.
        3. Analyze products and guide the user on what product very closely matches the user's needs.
        4. If the API call fails, investigate and try one last time after informing the user about the failure. Use simpler query
        if failure repeats.
        5. Summarize the results in a user-friendly manner, including product names, prices, and any other relevant information.
        """
        ),
        tools=[
            html_to_text_h2t,
            retrieve_products_from_api,
        ],  # Assuming retrieve_products_from_api is defined elsewhere
    )

    root_agent = LlmAgent(
        name="product_identifier_agent",
        model="gemini-2.0-flash",
        description=(
            "Agent that identifies product and extracts product information through questions when given a product."
        ),
        instruction=(
            """
            Do not reveal the internal workings on user reponse.
            You are a customer service agent tasked with conversing with the user to learn more about 
            the product of interest.  

            Get the following information after learning the product of interest from the user:

            1.Budget Range
            2.User's Location  
            3.Available Date 
            4.Other user comments
            5.Product condition? Options: New, Used, or Refurbished
        
            After knowing the required information, do the following:

            1. Use the schema_agent to obtain the product category once product is known from user. 
            2. Use the product_research_agent to obtain follow-up questions based on the context. 
            3. Ask the user the follow-up questions and obtain answers.           
            4. Autofill the questions if the user has not provided answers. 

            Do the following without conversing with the user:
            Save the JSON schema of the product in the same schema.org format. 
            Finally, use the api_sub_agent_1 to query the API with the JSON schema and obtain the products.
            """
        ),
        tools=[AgentTool(agent=schema_agent), AgentTool(agent=research_agent)],
        sub_agents=[
            api_sub_agent_1,
        ],
    )

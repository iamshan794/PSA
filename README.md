#   Multi-Agent AI shopping assistant for new vs used. 

# Agents and their tasks
1. PA agent:  Master agent that interfaces with the customer
2. Image2Image Agent: Find relevant images that are products.
3. VLM Inspection agent: Agent that verifies image and text relation tasked to do quality analysis to evaluate its fitness.
4. Product summarizer.Rag agent that can perform
Functionalities.
1) Discover products through conversations. Aka text 2 product, or voice to product
2) Use Image 2 Image to find same or similar items online. Aka Image 2 product

# Potential Areas to view products 

1. New products
    a) Walmart
    b) Amazon
    c) ebay
2. Used products 
    a) Facebook Maketplace 

# New product tasks 
1) Use a PA agent to identify the product and constraints imposed by user. 
2) Search new and used products.
3) Display options and 
# References 
1. Image to Image search for identifying similar products
2. IBM workshop https://www.youtube.com/watch?v=JUL1kvMVLAg
3. SerpAPI
4. Encore AI https://www.shopencore.ai/

Frontend (React)          Backend (Python FastAPI)
─────────────────────────┬───────────────────────────────
  Chat Interface          │  Agent Orchestrator
  Product Grid            │  - ADK Agents [3]
  Filter Controls         │  - LibreChat Adapter [2]
                          │  Database (MongoDB)
                          │  - Products [1]
                          │  - Conversations
# To Do:
1. Create guardrails for root_agent
# Archived 
1. https://github.com/mckaywrigley/clarity-ai (CLARITY AI)
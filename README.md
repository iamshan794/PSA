## Inspiration

While one-stop shop sites excel at fulfilling orders once you know what you want, they fall short when customers need genuine product education and unbiased guidance through complex purchasing decisions, which is where platforms for product discovery become invaluable as neutral starting points for discovery across the entire retail ecosystem. However, these apps require customers to already understand product categories and specifications, leaving a gap for those who are completely clueless about what features matter or how to evaluate products. Multi-agent AI systems could revolutionize this process by deploying collaborative agents to interview customers about their needs, research unfamiliar product categories, analyze technical specifications against real-world usage, and synthesize insights from thousands of reviews to recommend optimal choices. The inspiration for building such systems lies in democratizing expertise that was once exclusive to seasoned shoppers—most people buying cameras, laptops, or appliances lack the technical knowledge to navigate overwhelming specifications and marketing hype. These AI agents could transform product research from a confusing maze into a personalized, educational journey that empowers every consumer to make informed decisions with confidence, regardless of their prior knowledge.

## What it does

This shopping application is primarily built with *Gemini 2.0 Flash* as the Vision-Language Large Model (VLLM) that interfaces with customers. The product identifier agent identifies the specific product that the user is seeking. Upon receiving logistical information such as location and date of availability, the agent obtains the closest or most accurate schema that matches the user's product of interest.
With a known schema, the tool agent uses its best judgment to select attributes critical to product search. This key step helps understand the user's knowledge of the product and obtains essential attributes that influence product discovery. Through one or several rounds of interaction, the agent finalizes these parameters.

The subsequent stage of the application follows a conventional product retrieval workflow that utilizes open-source and proprietary APIs to obtain relevant products. The query parameter optimizer agent is responsible for optimizing API fields based on its prior research into user requirements. The agent receives additional context about the API to ensure efficient usage, where efficiency refers to minimizing the number of API calls.
Finally, the agent summarizes information about the retrieved products and provides a detailed walkthrough of which items best fit the user's needs.

## How I built it
1. **Google Agent Development Kit**: Multi-tool LLM Agents 
2. [Rapid API](https://rapidapi.com/): API service that retrieves new, used and refurbished products. Provides 100 requests/month for non-commercial purposes.
2. **Frontend**: [Streamlit.io](https://streamlit.io/)  with left layout for customer interaction and right layout to display product cards. 
3. **Backend**: Google ADK enabled FastAPI + Uvicorn server.
4. **MongoDB Atlas**: Store history of product cards viewed by the user. 
5. **Gitlab CI/CD**: Test, build and deploy application that used a runner VM instance hosted on Google Compute Engine
6. **Google Container Registry**: Gitlab built containers are pushed here for deployment.
7. **Google Cloud Run**: Host the final website

## Challenges I Ran Into
The major challenge was in handling complex structured data (JSON, XML) returned by various APIs and web scraping processes. 

## Accomplishments 
Successfully developed a minimal viable product that draws inspiration from innovative startups like  [Encore.ai @YCombinator](https://www.ycombinator.com/companies/encore) and established platforms like Google Shopping. The system demonstrates the potential to bridge the gap between product discovery and personalized education, creating a more intelligent shopping experience than traditional comparison sites.

## What I learned
- Concepts in Agentic AI through ADK
- Structured data markup on webpages for advertisement and shopping.
- Hosting websites on Google Cloud. 

## What's next
1. Refine results feature: With Parallel Agents, we can inspect used or refurbished products to re-rank the product candidates for the user. 
2. Image to Image product search features.
2. Perform an ablation study and define metrics to measure the significance of giving schema context to the agents.
3. Use web agents that can further search for products instead of APIs.
4. Add form based filters that minimizes interactions with bot.
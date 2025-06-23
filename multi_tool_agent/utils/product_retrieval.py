import html2text
import httpx
from typing import *
import requests
import json
import datetime
from datetime import datetime
from .ping_mongodb import agent_tool_insert_product
import pathlib
import os 
import asyncio

RATE_COUNT = 0


def html_to_text_h2t()-> str:

    PROJECT_ROOT=pathlib.Path(os.environ["PROJECT_ROOT"])
    template_path = PROJECT_ROOT / "assets" / "inputs" / "template.html"

    assert template_path.exists(), f"Template file not found at {template_path}"

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0  # Don't wrap lines

    return h.handle(html)


async def retrieve_products_from_api(
    product_name_search: str,
    country: str = "de",
    language: str = "en",
    sort_by: str = "BEST_MATCH",
    product_condition: str = "ANY",
    min_rating: str = "ANY",
    **kwdargs: Any,
) -> Dict[str, Any]:
    """
    Function to search for products using the Real-Time Product Search API.
    Returns the JSON response from the API.
    Refer template docs for data types, constraints and options to configure querystring
    """
    # Define the API endpoint and parameters
    url = os.environ.get("API_URL")

    page: int = 1
    limit: int = 10

    querystring = {
        "q": product_name_search,
        "country": country,
        "language": language,
        "page": page,
        "limit": limit,
        "sort_by": sort_by,
        "product_condition": product_condition,
        "min_rating": min_rating,
    }
    querystring.update(kwdargs)
    headers = {
        "x-rapidapi-key": os.environ["API_KEY"],
        "x-rapidapi-host": os.environ["API_HOST"],
    }

    global RATE_COUNT
    if RATE_COUNT > os.environ.get("API_RATE_LIMIT", 4):
        return {"status": "ERROR", "message": "Rate limit reached. Abort."}
    else:
        RATE_COUNT += 1
    try:

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=querystring)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            try:
                #Insert to mongoDB collection
                agent_tool_insert_product(response.json())
                return {"status": "OK", "data": response.json()}
            
            except Exception as e:

                return {"status": "OK", "data": response.json(), "message":"MongoDB insertion failed"}

    except Exception as e:
        print(f"Error running the API call : {e}")
        return {
            "status": "ERROR",
            "message": "Error: " + str(e),
        }

if __name__ == "__main__":
    # Example usage of the retrieve_products_from_api function
    product_name_search = "laptop"
    country = "us"
    language = "en"
    page = 1
    limit = 10
    sort_by = "BEST_MATCH"
    product_condition = "ANY"
    min_rating = "ANY"
    result = asyncio.run(retrieve_products_from_api(
        product_name_search,
    ))

    PROJECT_ROOT=pathlib.Path(os.environ["PROJECT_ROOT"])
    template_path = PROJECT_ROOT / "assets" / "outputs" / f"product_search_results_{product_name_search}.json"

    with open(template_path, "w") as f:
        json.dump(result["data"], f, indent=4)

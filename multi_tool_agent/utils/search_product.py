import requests
import typing 
from typing import *


async def get_product_search_results(product:str,country:str="de",page:int=1,limit:int=10,sort_by:str="BEST_MATCH",product_condition:str="ANY",min_rating:str="ANY") -> typing.Dict[str, typing.Any]:
    """
    Function to search for products using the Real-Time Product Search API.
    Returns the JSON response from the API.
    """
    # Define the API endpoint and parameters
    url = "https://real-time-product-search.p.rapidapi.com/search"
    
    querystring = {
        "q": product,
        "country": "de",
        "language": "en",
        "page": page,
        "limit": limit,
        "sort_by": "BEST_MATCH",
        "product_condition": "ANY",
        "min_rating": "ANY"
    }
    
    headers = {
        "x-rapidapi-key": "1ea1e31cfemshfe587adc5c86704p14d35cjsn4b260d16d0a0",
        "x-rapidapi-host": "real-time-product-search.p.rapidapi.com"
    }
    
    # Make the GET request to the API
    await response = requests.get(url, headers=headers, params=querystring)
    
    return {"status":"OK", "data": response.json()}

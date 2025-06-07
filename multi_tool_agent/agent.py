import os 
import datetime
from zoneinfo import ZoneInfo
import yaml 
import json
from pydantic import BaseModel

#Google ADK imports
from google import genai 
from google.genai import types
from google.adk import Agent
from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.agents.run_config import RunConfig
from google.adk.cli.utils import logs
from google.adk.runners import InMemoryRunner
from google.adk.sessions import Session

from google.adk.tools import google_search,load_artifacts
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# Local Imports
from .utils.get_tree import get_schema_tree
from .utils.product_retrieval import html_to_text_h2t, retrieve_products_from_api
from .agent_definition import agent_definition

# Root Agent's Tool 1
schema_agent = agent_definition.schema_agent
# Root Agent's Tool 2
research_agent = agent_definition.research_agent
# Sub Agent 1 -> root_agent
api_sub_agent_1 = agent_definition.api_sub_agent_1
# Root Agent
root_agent = agent_definition.root_agent
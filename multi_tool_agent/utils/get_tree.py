import requests
from bs4 import BeautifulSoup, Tag
import typing 
from typing import *

from google.adk.tools import ToolContext
from google.genai import types


class TreeNode:
    '''
    A tree data structure
    '''
    text: str
    node: "TreeNode"

    def __init__(self, text:str)-> None:
        self.text = text
        self.children = []

    def add_child(self, node:"TreeNode") -> None:
        self.children.append(node)


def fetch_html_as_text(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_li(li: Tag) -> TreeNode:

    label_tag = li.find(["span", "a"], class_=["dttsubtree", "dttBranch", "dttLeaf"])
    if label_tag:
        text = label_tag.get_text(strip=True)
    else:
        text = li.get_text(strip=True, separator=" ")

    # Remove 'C.' prefix if present
    if text.startswith("C."):
        text = text[2:]
    text = text.strip()

    node = TreeNode(text)

    # If this is a leaf, no children
    if "dttLeaf" in li.get("class", []) or (
        label_tag and "dttLeaf" in label_tag.get("class", [])
    ):
        return node

    # Otherwise, look for nested <ul>
    nested_ul = li.find("ul", recursive=False)
    if nested_ul:
        for child_li in nested_ul.find_all("li", recursive=False):
            child_node = parse_li(child_li)
            node.add_child(child_node)

    return node


def extract_tree_from_container(html: str) -> TreeNode:
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find("div", class_="dttTreeContainer")
    if not container:
        print("No dttTreeContainer found.")
        return None
    ul = container.find("ul")
    if not ul:
        print("No <ul> found in dttTreeContainer.")
        return None

    # Try to find the root node "C.Thing" or "Thing"
    for li in ul.find_all("li", recursive=False):
        label_tag = li.find(
            ["span", "a"], class_=["dttsubtree", "dttBranch", "dttLeaf"]
        )
        text = (
            label_tag.get_text(strip=True)
            if label_tag
            else li.get_text(strip=True, separator=" ")
        )
        text = text.strip()
        if text.startswith("C."):
            text = text[2:].strip()
        if text.lower().startswith("thing"):
            return parse_li(li)

    # Fallback: just parse the first <li>
    first_li = ul.find("li", recursive=False)
    if first_li:
        print("Warning: 'Thing' root not found, using first <li> as root.")
        return parse_li(first_li)
    print("No <li> found in <ul>.")
    return None


def print_tree(node: TreeNode, prefix:Optional[str]="") -> str:
    if not node:
        return ""
    lines = [prefix + node.text]
    child_count = len(node.children)
    for idx, child in enumerate(node.children):
        connector = "├─ " if idx < child_count - 1 else "└─ "
        next_prefix = prefix + ("│  " if idx < child_count - 1 else "   ")
        lines.append(print_tree(child, next_prefix + connector))
    return "\n".join(lines)


async def get_schema_tree(tool_context=ToolContext) -> dict[str,str]:
    '''
    Get schema as a text structure. Switches to a generic type of product if
    retrieval is not successful.
    '''

    url = "https://schema.org/docs/full.html"
    try:
        html_content = fetch_html_as_text(url) # Get text version of the HTML document
        root_node = extract_tree_from_container(html_content) #Parse as tree structure
        if root_node:
            tree_str = print_tree(root_node)
    except requests.RequestException as e:
        # Default to a generic product
        tree_str = "Product"
    await tool_context.save_artifact(
        "schema_tree.txt", types.Part.from_text(text=tree_str)
    )
    return {
        "status": "success",
        "detail": "Schema retrieved successfully and stored in artifacts.",
        "filename": "schema_tree.txt",
    }

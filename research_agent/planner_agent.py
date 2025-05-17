from pydantic import BaseModel
from agents import Agent

MAX_NUM_SEARCHES = 5

INSTRUCTIONS = """
You're a research assistant tasked with creating a web search plan. 
Given a research topic, then come up with a list of search queries that \
will help answer the main research question. You can use up to \
{MAX_NUM_SEARCHES} searches to gather the necessary information.
"""


class WebSearchQuery(BaseModel):
    reason: str
    """Your reasoning for searching for this query"""

    query: str
    """The search terms used to find the results"""


class WebSearchPlan(BaseModel):
    searches: list[WebSearchQuery]
    """The list of Web Search queries to answer the research question"""


planner_agent = Agent(
    name="planner_agent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)

from agents import Agent, WebSearchTool, ModelSettings, tool


INSTRUCTIONS = """
You're a research assistant responsible for answering research questions using web searches.

Given a research question, use your tools to search the web and find the most relevant and accurate information. 
Summarize your findings in a clear and concise format—2 to 3 short paragraphs, no more than 300 words.

Your summary will be used by another agent to compile a report, so include only essential facts. 
Avoid unnecessary details, commentary, or fluff. Complete sentences and perfect grammar are not required—just focus \
on delivering the core information.
"""


search_agent = Agent(
    name="search_agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
)

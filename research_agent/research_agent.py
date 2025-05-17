from pydantic import BaseModel
from agents import Agent


INSTRUCTIONS = """
You are a senior researcher responsible for writing a comprehensive and insightful report based on a search query.

You'll receive the original query along with preliminary research compiled by a research assistant. 

1. Start by creating a detailed outline that defines the structure and logical flow of the report. 
2. Then, use that outline to write a full report.
3. The final output should be in Markdown format, thorough and well-developed—aim for at least 1,000 words,
ideally spanning 5 to 10 pages. Focus on depth, clarity, and coherence to deliver a polished, high-quality report.
"""


class ReportData(BaseModel):
    short_summary: str
    """A short 2-3 sentence summary of the findings."""

    markdown_report: str
    """The final report"""

    follow_up_questions: list[str]
    """Suggested topics to research further"""


research_agent = Agent(
    name="research_agent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ReportData,
)

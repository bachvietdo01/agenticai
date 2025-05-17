from agents import Agent, function_tool
from postmarker.core import PostmarkClient
import os

INSTRUCTIONS = """
You are an email agent with expertise in crafting professionally toned emails that are also witty and clever.
You will be given a detailed report on a specific topic, and your task is to use your tools to write a well-formatted 
HTML email with a professional and engaging subject line.
"""

@function_tool
def send_email(subject: str, html_body: str):
    """Send an email given a subject and html body"""
    postmark = PostmarkClient(server_token=os.environ.get("POSTMARK_API_KEY"))
    from_email = "vietdo@umich.edu"  # Change to your verified sender
    to_email = "vietdo@umich.edu"  # Change to your recipient
    content = html_body
    response = postmark.emails.send(
        From=from_email, To=to_email, Subject=subject, HtmlBody=content
    )
    return {"status": "success"}


email_agent = Agent(
    name="email_agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)

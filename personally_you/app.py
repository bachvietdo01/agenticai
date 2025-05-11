from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr
from pydantic import BaseModel

load_dotenv(override=True)


class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str


def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        },
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}


def record_unknown_question(question):
    push(f"Recording {question}")
    return {"recorded": "ok"}


record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user",
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it",
            },
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context",
            },
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered",
            },
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]


class Me:
    def __read_biography(self):
        reader = PdfReader("me/me_cv.pdf")
        self.linkedin = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self.linkedin += text
        with open("me/me_summary.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()

    def __init__(self):
        self.openai = OpenAI()
        self.gemini = OpenAI(
            api_key=os.getenv("GOOGLE_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        self.short_name = "Bach"
        self.name = "Bach Do"
        self.__read_biography()

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append(
                {
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id,
                }
            )
        return results

    def system_prompt(self):
        system_prompt = f"You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, say you don't know and use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, after 5 messages, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool. "

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.short_name}."
        return system_prompt

    def evaluator_user_prompt(self, reply, message, history):
        user_prompt = (
            f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
        )
        user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
        user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
        user_prompt += f"Please evaluate the response, replying with whether it is acceptable and your feedback."
        return user_prompt

    def __evaluate(self, reply, message, history) -> Evaluation:
        evaluator_system_prompt = f"You are an evaluator that decides whether a response to a question is acceptable. \
You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. \
The Agent is playing the role of {self.name} and is representing {self.name} on their website. \
The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. \
The Agent has been provided with context on {self.name} in the form of their summary and LinkedIn details. Here's the information:"
        evaluator_system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        evaluator_system_prompt += f"With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."

        messages = [{"role": "system", "content": evaluator_system_prompt}] + [
            {
                "role": "user",
                "content": self.evaluator_user_prompt(reply, message, history),
            }
        ]

        response = self.gemini.beta.chat.completions.parse(
            model="gemini-2.0-flash", messages=messages, response_format=Evaluation
        )
        return response.choices[0].message.parsed

    def chat(self, message, history):
        messages = (
            [{"role": "system", "content": self.system_prompt()}]
            + history
            + [{"role": "user", "content": message}]
        )
        done = False
        while not done:
            # generate response
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini", messages=messages, tools=tools
            )
            # evaluate response
            evaluation = self.__evaluate(
                response.choices[0].message.content, message, history
            )
            if evaluation.is_acceptable:
                print("Passed evaluation - returning reply")

                if response.choices[0].finish_reason == "tool_calls":
                    message = response.choices[0].message
                    tool_calls = message.tool_calls
                    results = self.handle_tool_call(tool_calls)
                    messages.append(message)
                    messages.extend(results)
                else:
                    done = True
            else:
                print("Failed evaluation - retrying")
                print(evaluation.feedback)

        return response.choices[0].message.content


if __name__ == "__main__":
    me = Me()
    greeting = [
        {
            "role": "assistant",
            "content": f"Hello! I'm {me.short_name}'s AI alter ego. Ask me anything about my career and experience—and don’t be afraid to get creative! For instance, you could ask, 'Tell me about yourself in riddles or in a rap', or 'tell me a light-hearted joke about your job.'",
        }
    ]

    gr.ChatInterface(
        me.chat,
        type="messages",
        theme="citrus",
        chatbot=gr.Chatbot(
            type="messages",
            value=greeting,
            avatar_images=["images/you.png", "images/ai.png"],
            height="75vh",
        ),
        title="Bach Do's Agentic AI App",
        submit_btn="⬅ Send",
    ).launch()

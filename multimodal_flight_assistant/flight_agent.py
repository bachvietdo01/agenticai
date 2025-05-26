from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import base64
from io import BytesIO
from PIL import Image
import tempfile
import gradio as gr

INSTRUCTIONS = """
You are Emily, a cheerful, professional flight ticket assistant. 
Speak with a clear, positive American accent as you help customers 
find information and book flights.
"""

def artist(city):
    image_response = openai.images.generate(
            model="dall-e-3",
            prompt=f"An image representing a vacation in {city}, showing tourist spots and everything unique about {city}, in a vibrant pop-art style",
            size="1024x1024",
            n=1,
            response_format="b64_json",
        )
    image_base64 = image_response.data[0].b64_json
    image_data = base64.b64decode(image_base64)
    return Image.open(BytesIO(image_data))

def talker(message):
    response = openai.audio.speech.create(
      model="gpt-4o-mini-tts",
      voice="alloy",    # Also, try replacing onyx with alloy
      input=message,
      instructions=INSTRUCTIONS,
    )
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(response.content)
    
    return temp_file.name


ticket_prices = {"london": "$799", "paris": "$899", "tokyo": "$1400", "berlin": "$499", "saigon" : "$1000" }

def get_ticket_price(destination_city: str)->float:
    """
        use this function to find ticket price to a city

        args:
            destination_city: destination city
    """
    city = destination_city.lower()
    return ticket_prices.get(city, "Unknown")

price_function = {
    "name": "get_ticket_price",
    "description": "Get the price of a return ticket to the destination city. Call this whenever you need to know the ticket price, for example when a customer asks 'How much is a ticket to this city'",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to",
            },
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}

def handle_tool_call(message):
    tool_call = message.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    city = arguments.get('destination_city')
    price = get_ticket_price(city)
    response = {
        "role": "tool",
        "content": json.dumps({"destination_city": city,"price": price}),
        "tool_call_id": tool_call.id
    }
    return response, city

tools = [{"type": "function", "function": price_function}]


MODEL = 'gpt-4o-mini'
openai = OpenAI()


system_message = "You are Emily, a helpful assistant for an Airline Ticket Agency called VirtualArlineAI. "
system_message += "Give short, courteous answers, no more than 1 sentence. "
system_message += "Always be accurate. If you don't know the answer, say so."
system_message += "In addition, use your available to accomplish the task."

def chat(history):
    messages = [{"role": "system", "content": system_message}] + history
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    image = None
    
    if response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        response, city = handle_tool_call(message)
        messages.append(message)
        messages.append(response)
        image = artist(city)
        response = openai.chat.completions.create(model=MODEL, messages=messages)
        
    reply = response.choices[0].message.content
    history += [{"role":"assistant", "content":reply}]

    # Comment out or delete the next line if you'd rather skip Audio for now..
    #talker(reply)
    
    return history, image, talker(reply)


if __name__ == "__main__":
    with gr.Blocks() as ui:
        with gr.Row():
            chatbot = gr.Chatbot(height=500, type="messages")
            image_output = gr.Image(height=512, width=512, streaming=True)
            audio_output = gr.Audio(streaming=True, autoplay=True, format='mp3', visible=False)
        with gr.Row():
            entry = gr.Textbox(label="Chat with our AI Assistant:")
        with gr.Row():
            clear = gr.Button("Clear")

        def do_entry(message, history):
            history += [{"role":"user", "content":message}]
            return "", history

        entry.submit(do_entry, inputs=[entry, chatbot], outputs=[entry, chatbot]).then(
            chat, inputs=chatbot, outputs=[chatbot, image_output, audio_output]
        )
        clear.click(lambda: None, inputs=None, outputs=chatbot, queue=False)

        ui.launch(inbrowser=True)
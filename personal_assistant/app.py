import gradio as gr
from pa import PersonalAssistant


async def setup():
    pa = PersonalAssistant()
    await pa.setup()
    return pa

async def process_message(pa, message, success_criteria, history):
    results = await pa.run_superstep(message, success_criteria, history)
    return results, pa
    
async def reset():
    new_pa = PersonalAssistant()
    await new_pa.setup()
    return "", "", None, new_pa

def free_resources(pa):
    print("Cleaning up")
    try:
        if pa:
            pa.free_resources()
    except Exception as e:
        print(f"Exception during cleanup: {e}")


with gr.Blocks(title="AIPersonalAssistant", theme=gr.themes.Default(primary_hue="emerald")) as ui:
    gr.Markdown("## Agentic AI Personal Assistant")
    pa = gr.State(delete_callback=free_resources)
    
    with gr.Row():
        chatbot = gr.Chatbot(label="Personal Assistant", height=300, type="messages")
    with gr.Group():
        with gr.Row():
            message = gr.Textbox(show_label=False, placeholder="Your request to AI Personal Assistant")
        with gr.Row():
            success_criteria = gr.Textbox(show_label=False, placeholder="What are your success critiera?")
    with gr.Row():
        reset_button = gr.Button("Reset", variant="stop")
        go_button = gr.Button("Go!", variant="primary")
        
    ui.load(setup, [], [pa])
    message.submit(process_message, [pa, message, success_criteria, chatbot], [chatbot, pa])
    success_criteria.submit(process_message, [pa, message, success_criteria, chatbot], [chatbot, pa])
    go_button.click(process_message, [pa, message, success_criteria, chatbot], [chatbot, pa])
    reset_button.click(reset, [], [message, success_criteria, chatbot, pa])

    
ui.launch(inbrowser=True)
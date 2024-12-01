import gradio as gr
import base64
from io import BytesIO
import requests
from PIL import Image, ImageGrab
import keyboard
import threading
import time

def capture_screenshot():
    # Wait a moment for user to switch windows
    time.sleep(0.5)
    screenshot = ImageGrab.grab()
    return screenshot

def process_image(image, model_name="llama3.2-vision", prompt="What do you see in this image? Please provide a clear and concise description."):
    if image is None:
        return "Please provide an image first."
        
    # Convert PIL Image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Prepare the request to Ollama
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "images": [img_str],
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'No response from model')
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def process_with_custom_prompt(image, model_name, custom_prompt):
    if not custom_prompt.strip():
        custom_prompt = "What do you see in this image? Please provide a clear and concise description."
    return process_image(image, model_name, custom_prompt)

class HotkeyCapture:
    def __init__(self, callback):
        self.callback = callback
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        keyboard.add_hotkey('alt+shift+c', self.callback)
        while self.running:
            time.sleep(0.1)

    def stop(self):
        self.running = False
        keyboard.unhook_all()

# Create the Gradio interface
with gr.Blocks(title="Smart Vision Assistant") as demo:
    gr.Markdown("""
    # Smart Vision Assistant 🔍
    Upload an image or capture your screen to get AI analysis. Choose between two vision models:
    - llama3.2-vision
    - minicpm-v
    
    **Quick Tips:**
    - Press **Alt+Shift+C** anytime to capture your screen
    - Upload any image for analysis
    - Ask specific questions about the image (e.g., "What color is the car?", "How many people are in the image?")
    - Use the chat interface to have a conversation about the image
    """)
    
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(label="Image Input", type="pil")
            capture_btn = gr.Button("📸 Capture Screen (Alt+Shift+C)")
            model_choice = gr.Dropdown(
                label="Choose Vision Model",
                choices=["llama3.2-vision", "minicpm-v"],
                value="llama3.2-vision"
            )
            
        with gr.Column():
            chatbot = gr.Chatbot(
                label="Conversation",
                height=300,
                show_copy_button=True
            )
            question = gr.Textbox(
                label="Ask a question about the image",
                placeholder="Example: What objects do you see? What's happening in this image? What color is the car?",
                lines=2
            )
            with gr.Row():
                clear_btn = gr.Button("🗑️ Clear Chat")
                ask_btn = gr.Button("🔍 Ask Question", variant="primary")
            
    def add_question_and_get_response(image, model, user_question, history):
        if image is None:
            return history + [[user_question, "Please upload an image first."]]
        
        response = process_image(image, model, user_question)
        history = history + [[user_question, response]]
        return history
    
    def clear_chat_history():
        return []
    
    def capture_and_update():
        return capture_screenshot()
    
    capture_btn.click(
        capture_and_update,
        outputs=[image_input]
    )
    
    ask_btn.click(
        add_question_and_get_response,
        inputs=[image_input, model_choice, question, chatbot],
        outputs=[chatbot]
    )
    
    clear_btn.click(
        clear_chat_history,
        outputs=[chatbot]
    )
    
    ask_btn.click(lambda: "", None, [question])
    
    # Setup hotkey capture
    hotkey = HotkeyCapture(lambda: gr.update(value=capture_screenshot()))

# Launch the app
if __name__ == "__main__":
    print("Starting Smart Vision Assistant...")
    print("Access the web interface at http://127.0.0.1:7860")
    print("Press Alt+Shift+C anytime to capture your screen")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True
    )

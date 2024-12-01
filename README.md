# Smart Vision Assistant

A powerful image analysis tool that uses AI vision models to analyze images and answer questions about them.

## Features

- Support for multiple vision models:
  - llama3.2-vision
  - minicpm-v
- Interactive chat interface for asking questions about images
- Screen capture functionality
- Real-time image analysis
- Customizable prompts and questions

## Requirements

- Python 3.x
- Ollama (for running the vision models)
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Make sure Ollama is running with the required models:
- llama3.2-vision
- minicpm-v

## Usage

1. Run the application:
```bash
python gradio_vision_app.py
```

2. Open your web browser and navigate to http://127.0.0.1:7860

3. Use the interface to:
   - Upload images or capture your screen
   - Select your preferred vision model
   - Ask questions about the images
   - View AI-generated responses

## Hotkeys

- `Alt+Shift+C`: Capture screen

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

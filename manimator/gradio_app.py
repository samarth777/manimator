import gradio as gr
from main import generate_animation_response, process_pdf_with_gemini, ManimProcessor
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_prompt(prompt: str):
    try:
        processor = ManimProcessor()
        with processor.create_temp_dir() as temp_dir:
            response = generate_animation_response(prompt)
            code = processor.extract_code(response)

            if not code:
                return None, "No valid Manim code generated"

            class_match = re.search(r"class (\w+)\(Scene\)", code)
            if not class_match:
                return None, "No Scene class found in code"

            scene_name = class_match.group(1)
            scene_file = processor.save_code(code, temp_dir)
            video_path = processor.render_scene(scene_file, scene_name, temp_dir)

            if not video_path:
                return None, "Failed to render animation"

            return video_path, "Animation generated successfully!"
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return None, f"Error: {str(e)}"


def process_pdf(file):
    try:
        content = file.read()
        scene_description = process_pdf_with_gemini(content)
        return scene_description
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"Error processing PDF: {str(e)}"


def interface_fn(prompt=None, pdf_file=None):
    if prompt:
        video_path, message = process_prompt(prompt)
        if video_path:
            return gr.Video.update(value=video_path), message
        return None, message
    elif pdf_file:
        scene_description = process_pdf(pdf_file)
        return None, scene_description
    return None, "Please provide either a prompt or upload a PDF file"


demo = gr.Interface(
    fn=interface_fn,
    inputs=[
        gr.Textbox(
            label="Enter your prompt",
            placeholder="Describe the concepts you want to visualize...",
        ),
        gr.File(label="Or upload a PDF", file_types=[".pdf"]),
    ],
    outputs=[
        gr.Video(label="Generated Animation"),
        gr.Textbox(label="Output Message/Scene Description"),
    ],
    title="Manim Animation Generator",
    description="Generate animations from text prompts or analyze PDF papers",
)

if __name__ == "__main__":
    demo.launch()

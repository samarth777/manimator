import gradio as gr
from main import (
    generate_animation_response,
    process_pdf_with_gemini,
    process_prompt_scene,
    ManimProcessor,
)
import re


def process_prompt(prompt: str):
    max_attempts = 2
    attempts = 0

    while attempts < max_attempts:
        try:
            processor = ManimProcessor()
            with processor.create_temp_dir() as temp_dir:
                scene_description = process_prompt_scene(prompt)
                response = generate_animation_response(scene_description)
                code = processor.extract_code(response)

                if not code:
                    attempts += 1
                    if attempts < max_attempts:
                        continue
                    return None, "No valid Manim code generated after multiple attempts"

                class_match = re.search(r"class (\w+)\(Scene\)", code)
                if not class_match:
                    attempts += 1
                    if attempts < max_attempts:
                        continue
                    return None, "No Scene class found after multiple attempts"

                scene_name = class_match.group(1)
                scene_file = processor.save_code(code, temp_dir)
                video_path = processor.render_scene(scene_file, scene_name, temp_dir)

                if not video_path:
                    return None, "Failed to render animation"

                return video_path, "Animation generated successfully!"

        except Exception as e:
            attempts += 1
            if attempts < max_attempts:
                continue
            return None, f"Error after multiple attempts: {str(e)}"


def process_pdf(file_path: str):
    print("file_path", file_path)
    try:
        if not file_path:
            return "Error: No file uploaded"
        with open(file_path, "rb") as file_path:
            file_bytes = file_path.read()
            scene_description = process_pdf_with_gemini(file_bytes)
            print("scene_description", scene_description)
        return scene_description
    except Exception as e:
        return f"Error processing PDF: {str(e)}"


def interface_fn(prompt=None, pdf_file=None):
    if prompt:
        video_path, message = process_prompt(prompt)
        if video_path:
            return video_path, message
        return None, message
    elif pdf_file:
        scene_description = process_pdf(pdf_file)
        if scene_description:
            video_path, message = process_prompt(scene_description)
            if video_path:
                return video_path, message
            return None, message
    return None, "Please provide either a prompt or upload a PDF file"


description_md = """
## 🎬 manimator

This tool helps you create visualizations of complex concepts using natural language or PDF papers:

- **Text Prompt**: Describe the concept you want to visualize
- **PDF Upload**: Upload a research paper to extract key visualizations

### Links
- [Manim Documentation](https://docs.manim.community/)
- [Project Repository](https://github.com/yourusername/manimator)
"""

with gr.Blocks(title="manimator") as demo:
    gr.Markdown(description_md)

    with gr.Tabs():
        with gr.TabItem("✍️ Text Prompt"):
            with gr.Column():
                text_input = gr.Textbox(
                    label="Describe the animation you want to create",
                    placeholder="Explain the working of neural networks",
                    lines=3,
                )
                text_button = gr.Button("Generate Animation from Text")

            # Only show output UI elements here (not in the sample tab)
            with gr.Row():
                video_output = gr.Video(label="Generated Animation")
            status_output = gr.Textbox(
                label="Status", interactive=False, show_copy_button=True
            )

            text_button.click(
                fn=interface_fn,
                inputs=[text_input],
                outputs=[video_output, status_output],
            )

        with gr.TabItem("📄 PDF Upload"):
            with gr.Column():
                file_input = gr.File(label="Upload a PDF paper", file_types=[".pdf"])
                pdf_button = gr.Button("Generate Animation from PDF")

            # Show output UI elements here as well
            with gr.Row():
                pdf_video_output = gr.Video(label="Generated Animation")
            pdf_status_output = gr.Textbox(
                label="Status", interactive=False, show_copy_button=True
            )

            pdf_button.click(
                fn=lambda pdf: interface_fn(prompt=None, pdf_file=pdf),
                inputs=[file_input],
                outputs=[pdf_video_output, pdf_status_output],
            )

        with gr.TabItem("Sample Examples"):
            sample_select = gr.Dropdown(
                choices=[
                    "What is a CNN?",
                    "BitNet Paper",
                    "Explain Fourier Transform",
                    "How does backpropagation work in Neural Networks?",
                    "What is SVM?",
                ],
                label="Choose an example to display",
                value=None,
            )
            sample_video = gr.Video()
            sample_markdown = gr.Markdown()

            def show_sample(example):
                if example == "What is a CNN?":
                    return "./few_shot/CNNExplanation.mp4", "Output: Example Output 1"
                elif example == "BitNet Paper":
                    return "./few_shot/BitNet.mp4", "Output: Example Output 2"
                elif example == "Explain Fourier Transform":
                    return (
                        ".few_shot/FourierTransformExplanation.mp4",
                        "Output: Example Output 3",
                    )
                elif example == "How does backpropagation work in Neural Networks?":
                    return (
                        ".few_shot/NeuralNetworksBackPropagationExample.mp4",
                        "Output: Example Output 4",
                    )
                elif example == "What is SVM?":
                    return "./few_shot/SVMExplanation.mp4", "Output: Example Output 5"
                return None, ""

            sample_select.change(
                fn=show_sample,
                inputs=sample_select,
                outputs=[sample_video, sample_markdown],
            )

if __name__ == "__main__":
    demo.launch(share=True)

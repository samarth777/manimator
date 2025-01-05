from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import re
import litellm
import base64
import requests
from dotenv import load_dotenv
from utils.models import PromptRequest
from utils.schema import ManimProcessor
from utils.prompts import MANIM_SYSTEM_PROMPT, SCENE_SYSTEM_PROMPT
from PyPDF2 import PdfReader, PdfWriter
import io

load_dotenv()

few_shot_pdf_bytes = open("few_shot/few_shot_1.pdf", "rb").read()
few_shot_pdf = base64.b64encode(few_shot_pdf_bytes).decode("utf-8")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def compress_pdf(content: bytes, compression_level: int = 5) -> str:
    try:
        reader = PdfReader(io.BytesIO(content))
        output = io.BytesIO()
        writer = PdfWriter(output)

        for page in reader.pages:
            writer.add_page(page)

        writer.set_compression(compression_level)
        writer.write(output)

        compressed_bytes = output.getvalue()
        return base64.b64encode(compressed_bytes).decode("utf-8")
    except Exception as e:
        return base64.b64encode(content).decode("utf-8")


def generate_animation_response(prompt: str) -> str:
    try:
        messages = [
            {
                "role": "system",
                "content": MANIM_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"{prompt}\n\n NOTE!!!: Make sure the objects or text in the generated code are not overlapping at any point in the video. Make sure that each scene is properly cleaned up before transitioning to the next scene.",
            },
        ]
        response = litellm.completion(
            model="deepseek/deepseek-chat", messages=messages, num_retries=2
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate animation response: {str(e)}"
        )


def process_prompt_scene(prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": SCENE_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": "Fourier Transform",
        },
        {
            "role": "assistant",
            "content": r"""### *Topic*: Fourier Transform
*Key Points*:
- Time domain vs frequency domain
- Decomposing signals into sine waves: \( f(t) = \sum_{n} A_n \sin(2\pi n t + \phi_n) \)
- Fourier Transform formula: \( \hat{f}(\xi) = \int_{-\infty}^{\infty} f(t) e^{-2\pi i \xi t} dt \)
- Applications in signal processing
*Visual Elements*:
- Animate a complex signal being decomposed into sine waves.
- Show the Fourier Transform as a graph in the frequency domain.
*Style*: Smooth animations with mathematical formulas and graphs.""",
        },
        {
            "role": "user",
            "content": "Explain Gradient Descent",
        },
        {
            "role": "assistant",
            "content": r"""### *Topic*: Gradient Descent
*Key Points*:
- Loss function: \( L(\theta) = \frac{1}{N} \sum_{i=1}^{N} (y_i - f(x_i; \theta))^2 \)
- Gradient calculation: \( \nabla L(\theta) = \frac{\partial L}{\partial \theta} \)
- Update rule: \( \theta_{new} = \theta_{old} - \alpha \nabla L(\theta) \)
- Convergence to the minimum
*Visual Elements*:
- 3D surface plot of the loss function.
- Animate the gradient descent steps moving toward the minimum.
*Style*: 3D visualizations with step-by-step explanations.""",
        },
        {
            "role": "user",
            "content": "How does backpropogation work in neural networks?",
        },
        {
            "role": "assistant",
            "content": r"""### *Topic*: Neural Networks (Backpropagation)
*Key Points*:
- Loss function: \( L(\theta) = \frac{1}{N} \sum_{i=1}^{N} (y_i - f(x_i; \theta))^2 \)
- Chain rule: \( \frac{\partial L}{\partial f} \frac{\partial f}{\partial \theta} \)
- Weight updates: \( \theta_{new} = \theta_{old} - \alpha \nabla L(\theta) \)
*Visual Elements*:
- Animate the flow of gradients through the network.
- Show the loss surface and gradient descent steps.
*Style*: Step-by-step, with clear visualizations of gradients and updates.""",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]
    response = litellm.completion(
        model="sambanova/Meta-Llama-3.3-70B-Instruct",
        messages=messages,
        num_retries=2,
    )
    return response.choices[0].message.content


def process_pdf_with_gemini(
    file_content: bytes, model="gemini/gemini-1.5-flash", retry=False
) -> str:
    encoded_pdf = compress_pdf(file_content)
    try:
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": SCENE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": "data:application/pdf;base64,{}".format(
                                few_shot_pdf
                            ),
                        },
                    ],
                },
                {
                    "role": "assistant",
                    "content": r"""*Topic*: Deep Residual Learning for Image Recognition
*Key Points*:
1. *Degradation Problem*: Explain how deeper networks suffer from higher training error despite having more capacity.
2. *Residual Learning*: Show how residual learning reformulates the problem by learning residual functions \( \mathcal{F}(\mathbf{x}) = \mathcal{H}(\mathbf{x}) - \mathbf{x} \) instead of direct mappings \( \mathcal{H}(\mathbf{x}) \).
3. *Shortcut Connections*: Visualize how identity shortcuts (skip connections) are added to the network to enable residual learning.
4. *Deep Residual Networks*: Demonstrate the architecture of deep residual networks (e.g., ResNet-34, ResNet-152) and how they outperform plain networks.
5. *Bottleneck Design*: Explain the bottleneck design in deeper ResNets (e.g., ResNet-50/101/152) using \(1 \times 1\), \(3 \times 3\), and \(1 \times 1\) convolutions.

*Style*: 3Blue1Brown style (clean, minimalistic, with smooth animations and clear labels)
*Additional Requirements*:
- Include mathematical formulas (e.g., \( \mathcal{F}(\mathbf{x}) = \mathcal{H}(\mathbf{x}) - \mathbf{x} \)) and graphs (e.g., training error vs. depth).
- Use color coding to differentiate between plain networks and residual networks.
- Animate the flow of data through shortcut connections and residual blocks.
- Provide step-by-step explanations for each concept.""",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": "data:application/pdf;base64,{}".format(
                                encoded_pdf
                            ),
                        },
                    ],
                },
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        if retry == False:
            return process_pdf_with_gemini(
                file_content,
                model="gemini/gemini-2.0-flash-exp",
                retry=True,
            )
        else:
            raise HTTPException(
                status_code=500, detail=f"Failed to process PDF with Gemini: {str(e)}"
            )


def download_arxiv_pdf(url: str) -> bytes:
    """Download PDF from arxiv URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to download arxiv PDF: {str(e)}"
        )


@app.get("/health-check")
async def health_check():
    return {"status": "ok"}


@app.post("/generate-pdf-scene")
async def generate_pdf_scene(file: UploadFile = File(...)):
    try:
        content = await file.read()
        scene_description = process_pdf_with_gemini(content)
        return {"scene_description": scene_description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-prompt-scene")
async def generate_prompt_scene(request: PromptRequest):
    try:
        return {"scene_description": process_prompt_scene(request.prompt)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating scene descriptions: {str(e)}"
        )


@app.get("/pdf/{arxiv_id}")
async def process_arxiv_by_id(arxiv_id: str):
    """Process arxiv paper by ID"""
    try:
        arxiv_url = f"https://arxiv.org/pdf/{arxiv_id}"
        pdf_content = download_arxiv_pdf(arxiv_url)
        scene_description = process_pdf_with_gemini(pdf_content)
        return {"scene_description": scene_description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-animation")
async def generate_animation(request: PromptRequest):
    processor = ManimProcessor()

    try:
        with processor.create_temp_dir() as temp_dir:
            response = generate_animation_response(request.prompt)
            code = processor.extract_code(response)
            if not code:
                raise HTTPException(
                    status_code=400, detail="No valid Manim code generated"
                )
            class_match = re.search(r"class (\w+)\(Scene\)", code)
            if not class_match:
                raise HTTPException(
                    status_code=400, detail="No Scene class found in code"
                )
            scene_name = class_match.group(1)
            scene_file = processor.save_code(code, temp_dir)
            video_path = processor.render_scene(scene_file, scene_name, temp_dir)
            if not video_path:
                raise HTTPException(
                    status_code=500, detail="Failed to render animation"
                )
            return FileResponse(video_path, media_type="video/mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

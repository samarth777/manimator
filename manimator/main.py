from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
import re
import subprocess
import tempfile
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import logging
import traceback
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    prompt: str


class ManimProcessor:
    @contextmanager
    def create_temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        try:
            yield temp_dir
        finally:
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(temp_dir)

    def extract_code(self, rag_response: str) -> Optional[str]:
        pattern = r"```python\n(.*?)```"
        match = re.search(pattern, rag_response, re.DOTALL)
        return match.group(1).strip() if match else None

    def save_code(self, code: str, temp_dir: str) -> str:
        scene_file = os.path.join(temp_dir, "scene.py")
        with open(scene_file, "w") as f:
            f.write("from manim import *\n\n")
            f.write(code)
        return scene_file

    def render_scene(
        self, scene_file: str, scene_name: str, temp_dir: str
    ) -> Optional[str]:
        cmd = [
            "manim",
            "-pql",
            "--media_dir",
            temp_dir,
            scene_file,
            scene_name,
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            video_path = os.path.join(
                temp_dir, "videos", "scene", "480p15", f"{scene_name}.mp4"
            )

            if not os.path.exists(video_path):
                return None

            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            with open(video_path, "rb") as f:
                temp_video.write(f.read())
            return temp_video.name

        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Render error: {e.stderr}")


class RAGSystem:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv("SAMBANOVA_API_KEY"),
            base_url="https://api.sambanova.ai/v1",
        )

    def generate_response(self, prompt: str) -> str:
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant specializing in generating Manim visualizations.",
                },
                {
                    "role": "user",
                    "content": f"Generate precise and error-free Manim code in Python for: {prompt}. Ensure scenes are rendered properly, visually pleasing, with smooth animations and professional quality.",
                },
            ]

            logger.debug(f"Sending prompt to SambaNova: {prompt}")
            response = self.client.chat.completions.create(
                model="Qwen2.5-Coder-32B-Instruct",
                messages=messages,
                temperature=0.1,
                top_p=0.1,
            )
            logger.debug(f"Received response from SambaNova: {response}")

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in generate_response: {str(e)}")
            logger.error(traceback.format_exc())
            raise


@app.post("/generate-animation")
async def generate_animation(request: PromptRequest):
    rag = RAGSystem()
    processor = ManimProcessor()

    try:
        with processor.create_temp_dir() as temp_dir:
            logger.info(f"Processing prompt: {request.prompt}")

            response = rag.generate_response(request.prompt)
            logger.debug(f"RAG response: {response}")

            code = processor.extract_code(response)
            if not code:
                logger.error("No valid Manim code found in response")
                raise HTTPException(
                    status_code=400, detail="No valid Manim code generated"
                )

            logger.debug(f"Extracted code: {code}")

            class_match = re.search(r"class (\w+)\(Scene\)", code)
            if not class_match:
                logger.error("No Scene class found in code")
                raise HTTPException(
                    status_code=400, detail="No Scene class found in code"
                )

            scene_name = class_match.group(1)
            logger.info(f"Found scene class: {scene_name}")

            scene_file = processor.save_code(code, temp_dir)
            logger.debug(f"Saved code to: {scene_file}")

            video_path = processor.render_scene(scene_file, scene_name, temp_dir)
            logger.debug(f"Render result path: {video_path}")

            if not video_path:
                logger.error("Failed to render animation")
                raise HTTPException(
                    status_code=500, detail="Failed to render animation"
                )

            return FileResponse(video_path, media_type="video/mp4")

    except Exception as e:
        logger.error(f"Error in generate_animation: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

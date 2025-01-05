from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import logging
import traceback
from dotenv import load_dotenv
from utils.schema import ManimProcessor, RAGSystem

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

    uvicorn.run(app, host="0.0.0.0", port=10000)

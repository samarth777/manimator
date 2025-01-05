import os
import re
import subprocess
import tempfile
from contextlib import contextmanager
from typing import Optional
import logging
from fastapi import HTTPException


# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)


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

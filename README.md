# manimator

![manimator](https://raw.githubusercontent.com/HyperCluster-Tech/manimator/assets/HyperCluster.png)
[![GitHub Stars](https://img.shields.io/github/stars/HyperCluster-Tech/manimator?style=social)](https://github.com/HyperCluster-Tech/manimator/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/HyperCluster-Tech/manimator?style=social)](https://github.com/HyperCluster-Tech/manimator/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/HyperCluster-Tech/manimator)](https://github.com/HyperCluster-Tech/manimator/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/HyperCluster-Tech/manimator)](https://github.com/HyperCluster-Tech/manimator/pulls)
[![License](https://img.shields.io/github/license/HyperCluster-Tech/manimator)](https://github.com/HyperCluster-Tech/manimator/blob/main/LICENSE)

> [!IMPORTANT]
>
> manimator is a tool to transform research papers and mathematical concepts into stunning visual explanations, powered by AI and the [manim](https://github.com/ManimCommunity/manim) engine

### 🔗 Try it out:

- [![**On Gradio (Hugging Face):**](https://huggingface.co/datasets/huggingface/badges/blob/main/open-in-hf-spaces-md-dark.svg)](https://huggingface.co/spaces/HyperCluster/manimator)
- Or replace `arxiv.org` with `manimator.hypercluster.tech` in any arXiv PDF URL for instant visualizations!

### What is _manimator_?

Building on the incredible work by 3Blue1Brown and the manim community, _manimator_ turns complex research papers and user prompts into clear, animated explainer videos.

---

### 🌟 Highlights so far:

- Over **1000+ uses** within 24 hours of launch and over **5000 uses** within a week
- Featured as Hugging Face's **Space of the Week**!
- 16th in Hugging Face's Top Trending Spaces

## Installation

> [!IMPORTANT]
> This project is built using the [poetry](https://python-poetry.org/) tool to manage Python packages and dependencies. Download it from [here](https://python-poetry.org/docs/#installing-with-the-official-installer) to run this project or use the Docker image.
> This project is dependent on the [manim](https://github.com/ManimCommunity/manim) engine and hence has certain dependencies for running the engine properly which can be found [here](https://docs.manim.community/en/stable/installation.html).

```
bash
git clone https://github.com/HyperCluster-Tech/manimator
cd manimator
```

Install Dependencies:
`poetry install`

Activate the environment:
`poetry env activate`

(If you're using a version before Poetry 2.0, you should use `poetry shell`)

## Usage

After successfully installing all the project dependencies and manim dependencies, set the environment variables in a .env file according to the .env.example:

Run the FastAPI server:

```
poetry run app
```

and visit `localhost:8000/docs` to open SwaggerUI

Run the Gradio interface:

```
poetry run gradio-app
```

and open `localhost:7860`

### Notes

To change the models being used, you can set the environment variables for the models according to [LiteLLM syntax](https://docs.litellm.ai/docs/providers) and set the corresponding API keys accordingly.

To prompt engineer to better suit your use case, you can modify the system prompts in `utils/system_prompts.py` and change the few shot examples in `few_shot/few_shot_prompts.py`.

## 🛳️ Docker

To use manimator with Docker, execute the following commands:

1. Clone the manimator repo to get the Docker image (we will be publishing the image in DockerHub soon)
2. Run the Docker container, exposing port 8000 for the FastAPI server or 7860 for the Gradio interface

Build the Docker image locally. Then, run the Docker container as follows:

`docker build -t manimator .`

If you are running the FastAPI server

`docker run -p 8000:8000 manimator`

Else for the Gradio interface

`docker run -p 7860:7860 manimator`

<details>
<summary><h2>API Endpoints</h2></summary>

- [API Endpoints](#api-endpoints)
  - [Health Check](#health-check)
  - [PDF Processing](#pdf-processing)
    - [Generate PDF Scene](#generate-pdf-scene)
    - [Process ArXiv PDF](#process-arxiv-pdf)
  - [Scene Generation](#scene-generation)
    - [Generate Prompt Scene](#generate-prompt-scene)
  - [Animation Generation](#animation-generation)
    - [Generate Animation](#generate-animation)

### Health Check

#### Check API Health Status

Endpoint: `/health-check`  
Method: GET

Returns the health status of the API.

Response:

```json
{
  "status": "ok"
}
```

Curl command:

```bash
curl http://localhost:8000/health-check
```

### PDF Processing

#### Generate PDF Scene

Endpoint: `/generate-pdf-scene`  
Method: POST

Processes a PDF file and generates a scene description for animation.

Request:

- Content-Type: `multipart/form-data`
- Body: PDF file

Response:

```json
{
  "scene_description": "Generated scene description based on PDF content"
}
```

Curl command:

```bash
curl -X POST -F "file=@/path/to/file.pdf" http://localhost:8000/generate-pdf-scene
```

#### Process ArXiv PDF

Endpoint: `/pdf/{arxiv_id}`  
Method: GET

Downloads and processes an arXiv paper by ID to generate a scene description.

Parameters:

- `arxiv_id`: The arXiv paper identifier

Response:

```json
{
  "scene_description": "Generated scene description based on arXiv paper"
}
```

Curl command:

```bash
curl http://localhost:8000/pdf/2312.12345
```

### Scene Generation

#### Generate Prompt Scene

Endpoint: `/generate-prompt-scene`  
Method: POST

Generates a scene description from a text prompt.

Request:

- Content-Type: `application/json`
- Body:

```json
{
  "prompt": "Your scene description prompt"
}
```

Response:

```json
{
  "scene_description": "Generated scene description based on prompt"
}
```

Curl command:

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Explain how neural networks work"}' \
     http://localhost:8000/generate-prompt-scene
```

### Animation Generation

#### Generate Animation

Endpoint: `/generate-animation`  
Method: POST

Generates a Manim animation based on a text prompt.

Request:

- Content-Type: `application/json`
- Body:

```json
{
  "prompt": "Your animation prompt"
}
```

Response:

- Content-Type: `video/mp4`
- Body: Generated MP4 animation file

Curl command:

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Create an animation explaining quantum computing"}' \
     --output animation.mp4 \
     http://localhost:8000/generate-animation
```

### Error Handling

All endpoints follow consistent error handling:

- 400: Bad Request - Invalid input or missing required fields
- 500: Internal Server Error - Processing or generation failure

Error responses include a detail message:

```json
{
  "detail": "Error description"
}
```

### Notes

1. The API processes PDFs and generates animations using the Manim library
2. Scene descriptions are generated using Language Models (LLMs)
3. Animations are rendered using Manim with specific quality settings (-pql flag)
4. All generated files are handled in temporary directories and cleaned up automatically
5. PDF processing includes automatic compression for optimal performance

</details>

## Coming Soon

- **Improved Generation Quality**  
  Enhance the clarity and precision of generated animations and videos.

- **Video Transcription**  
  Automatically generate scripts explaining how concepts in the video relate to the research paper.

- **Adding Audio**  
  Support for adding voiceovers and background music to create more engaging visualizations.

## Limitations

- **LLM Limitations**  
  For accurate document parsing and code generation, we require large models like Gemini, DeepSeek V3 and Qwen 2.5 Coder 32B, which cannot be run locally.

- **Video Generation Limitations**  
  The generated video may sometimes exhibit overlap between scenes and rendered elements, leading to visual inconsistencies. Additionally, it sometimes fails to effectively visualize complex papers in a relevant and meaningful manner.

## License

manimator is licensed under the MIT License. See `LICENSE` for more information.
The project uses the [Manim engine](https://github.com/ManimCommunity/manim) under the hood, which is double-licensed under the MIT license, with copyright by 3blue1brown LLC and copyright by Manim Community Developers.

## Acknowledgements

We acknowledge the [Manim Community](https://www.manim.community/) for developing and maintaining the Manim library, which serves as the foundation for this project. We would also like to recognize [Samarth P](https://github.com/your-github-profile), [Vyoman Jain](https://github.com/VyoJ), [Shiva Golugula](https://github.com/Shiva4113), and [M Sai Sathvik](https://github.com/User-LazySloth) for their efforts in developing **manimator**.  

Models and Providers being used:

- DeepSeek-V3
- Llama 3.3 70B via SambaNova
- Gemini 1.5 Flash / 2.0 Flash-experimental

---

## Contact

<p align="center">
  <a href="https://www.hypercluster.tech/">
    <img src="https://api.star-history.com/svg?repos=HyperCluster-Tech/manimator&type=Date" alt="Star History Chart">
  </a>
</p>
For any inquiries, please contact us at hypercluster.tech@gmail.com

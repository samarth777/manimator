# manimator

Transform research papers and mathematical concepts into stunning visual explanations (using the manim engine), powered by AI

## Installation

This Python project's dependencies are managed using Poetry

Run `poetry install` to install the dependencies to run the backend and then activate the environment using `poetry shell`.

To use Manim locally, follow the instructions using the official [Manim Community docs](https://docs.manim.community/en/stable/installation.html).

## Usage

Populate the .env file using the .env.example as a template

Run the FastAPI backend with the command `python manimator/main.py` and access the endpoints at [http://localhost:8000/docs](http://localhost:8000/docs)
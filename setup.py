from setuptools import setup, find_packages

setup(
    name="mcp",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "groq",
        "requests",
        "python-dotenv",
        "langchain-openai",
        "python-multipart",
        "markdown"
    ],
)
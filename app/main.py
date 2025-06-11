import os
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from groq import Groq
import requests
from dotenv import load_dotenv
from mcp_integration import MCPIntegration
from rag_integration import RAGIntegration
import markdown

load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize integrations
mcp = MCPIntegration()
rag = RAGIntegration()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ChatMessage(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(message: ChatMessage):
    try:
        # Get context from all sources
        github_context = mcp.get_github_context()
        rag_context = rag.get_context()

        # Search RAG content for relevant information
        rag_search = rag.search_content(message.message)
        rag_data = rag_search["content"] if rag_search["found"] else "No specific information found in the records."

        # Create system message
        system_message = f"""Hi! I'm Dhurkesh's personal assistant. I have access to his information and can help answer questions about him.

        Here's what I know about Dhurkesh:
        {rag_data}

        Additional Information:
        {github_context}
        
        I can help you with:
        - Information about Dhurkesh's background and experience
        - Details about his projects and work
        - Any other questions you might have about him
        
        Please feel free to ask your question, and I'll provide a helpful response based on the available information."""

        # Generate response with Groq
        chat_completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": message.message
                }
            ],
            temperature=0.5,
            max_tokens=1024,
            stream=False,
        )

        # Convert the response to HTML using markdown
        response_text = chat_completion.choices[0].message.content
        response_html = markdown.markdown(response_text)

        return {"response": response_html}

    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            
            # Get context from all sources
            github_context = mcp.get_github_context()
            rag_context = rag.get_context()

            # Search RAG content for relevant information
            rag_search = rag.search_content(message)
            rag_data = rag_search["content"] if rag_search["found"] else "No specific information found in the records."

            # Create system message
            system_message = f"""Hi! I'm Dhurkesh's personal assistant. I have access to his information and can help answer questions about him.

            Here's what I know about Dhurkesh:
            {rag_data}

            Additional Information:
            {github_context}
            
            I can help you with:
            - Information about Dhurkesh's background and experience
            - Details about his projects and work
            - Any other questions you might have about him
            
            Please feel free to ask your question, and I'll provide a helpful response based on the available information."""

            # Generate response with Groq
            chat_completion = groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                temperature=0.5,
                max_tokens=1024,
                stream=False,
            )

            # Convert the response to HTML using markdown
            response_text = chat_completion.choices[0].message.content
            response_html = markdown.markdown(response_text)

            await websocket.send_text(response_html)
    except Exception as e:
        await websocket.close()

def get_github_context():
    token = os.getenv("GITHUB_TOKEN")
    username = os.getenv("GITHUB_USER")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get user repositories
    repos_response = requests.get(
        f"https://api.github.com/users/{username}/repos",
        headers=headers
    )
    repos = [repo["name"] for repo in repos_response.json()] if repos_response.ok else []
    
    # Get user activity
    events_response = requests.get(
        f"https://api.github.com/users/{username}/events",
        headers=headers
    )
    events = [event["type"] for event in events_response.json()[:5]] if events_response.ok else []
    
    return {
        "username": username,
        "repositories": repos,
        "recent_activity": events
    }

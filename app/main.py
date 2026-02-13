import os
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import requests
from dotenv import load_dotenv
from mcp.protocol import MCPProtocol
from mcp.context import ContextManager
from mcp.memory import MemoryManager
from rag_integration import RAGIntegration
import markdown

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize MCP components
mcp_protocol = MCPProtocol()
context_manager = ContextManager(mcp_protocol)
memory_manager = MemoryManager(mcp_protocol)
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
        github_context = get_github_context()
        context_manager.add_github_context(github_context)
        
        rag_context = rag.get_context()
        context_manager.add_rag_context(rag_context)

        # Add user message to context
        context_manager.add_user_message(message.message)

        # Search RAG content for relevant information
        rag_search = rag.search_content(message.message)
        rag_data = rag_search["content"] if rag_search["found"] else "No specific information found in the records."

        # Get relevant memories
        relevant_memories = memory_manager.get_relevant_memories(message.message)

        # Create system message with repository information
        repo_info = ""
        for repo in github_context["repositories"]:
            repo_info += f"\nRepository: {repo['name']}\n"
            repo_info += f"Description: {repo['description']}\n"
            repo_info += f"Language: {repo['language']}\n"
            if repo['readme']:
                repo_info += f"README Preview: {repo['readme'][:200]}...\n"
            repo_info += "---\n"

        system_message = f"""Hi! I'm Dhurkesh's personal assistant. I have access to his information and can help answer questions about him.

        Here's what I know about Dhurkesh:
        {rag_data}

        Repository Information:
        {repo_info}

        Recent Activity:
        {', '.join(github_context['recent_activity'])}
        
        I can help you with:
        - Information about Dhurkesh's background and experience
        - Details about his projects and work
        - Any other questions you might have about him
        
        Please feel free to ask your question, and I'll provide a helpful response based on the available information."""

        # Generate response with Groq
        chat_completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
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

        # Add assistant response to context
        context_manager.add_assistant_message(response_text)

        # Store important information in memory
        if "project" in message.message.lower():
            memory_manager.add_important_fact(f"User asked about projects: {message.message}")

        return {"response": response_html}

    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        print("WebSocket connection accepted")
        
        while True:
            try:
                message = await websocket.receive_text()
                print(f"Received message: {message}")
                
                # Get context from all sources
                github_context = get_github_context()
                context_manager.add_github_context(github_context)
                
                rag_context = rag.get_context()
                context_manager.add_rag_context(rag_context)

                # Add user message to context
                context_manager.add_user_message(message)

                # Search RAG content for relevant information
                rag_search = rag.search_content(message)
                rag_data = rag_search["content"] if rag_search["found"] else "No specific information found in the records."

                # Get relevant memories
                relevant_memories = memory_manager.get_relevant_memories(message)

                # Create system message with repository information
                repo_info = ""
                for repo in github_context["repositories"]:
                    repo_info += f"\nRepository: {repo['name']}\n"
                    repo_info += f"Description: {repo['description']}\n"
                    repo_info += f"Language: {repo['language']}\n"
                    if repo['readme']:
                        repo_info += f"README Preview: {repo['readme'][:200]}...\n"
                    repo_info += "---\n"

                system_message = f"""Hi! I'm Dhurkesh's personal assistant. I have access to his information and can help answer questions about him.

                Here's what I know about Dhurkesh:
                {rag_data}

                Repository Information:
                {repo_info}

                Recent Activity:
                {', '.join(github_context['recent_activity'])}
                
                I can help you with:
                - Information about Dhurkesh's background and experience
                - Details about his projects and work
                - Any other questions you might have about him
                
                Please feel free to ask your question, and I'll provide a helpful response based on the available information."""

                # Generate response with Groq
                chat_completion = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
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

                # Add assistant response to context
                context_manager.add_assistant_message(response_text)

                # Store important information in memory
                if "project" in message.lower():
                    memory_manager.add_important_fact(f"User asked about projects: {message}")

                await websocket.send_text(response_html)
                print("Response sent successfully")
                
            except Exception as e:
                print(f"Error processing message: {str(e)}")
                await websocket.send_text(f"Error: {str(e)}")
                
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        try:
            await websocket.close()
        except:
            pass

def get_github_context():
    token = os.getenv("GITHUB_TOKEN")
    username = os.getenv("GITHUB_USER")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get user repositories
    repos_response = requests.get(
        f"https://api.github.com/users/{username}/repos",
        headers=headers
    )
    repos_data = repos_response.json() if repos_response.ok else []
    
    # Process each repository
    repos_info = []
    for repo in repos_data:
        repo_name = repo["name"]
        
        # Get README content
        readme_response = requests.get(
            f"https://api.github.com/repos/{username}/{repo_name}/readme",
            headers=headers
        )
        
        readme_content = ""
        if readme_response.ok:
            import base64
            readme_content = base64.b64decode(readme_response.json()["content"]).decode("utf-8")
        
        # Get repository details
        repo_info = {
            "name": repo_name,
            "description": repo.get("description", ""),
            "language": repo.get("language", ""),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "readme": readme_content,
            "url": repo.get("html_url", ""),
            "created_at": repo.get("created_at", ""),
            "updated_at": repo.get("updated_at", "")
        }
        repos_info.append(repo_info)
    
    # Get user activity
    events_response = requests.get(
        f"https://api.github.com/users/{username}/events",
        headers=headers
    )
    events = [event["type"] for event in events_response.json()[:5]] if events_response.ok else []
    
    return {
        "username": username,
        "repositories": repos_info,
        "recent_activity": events
    }

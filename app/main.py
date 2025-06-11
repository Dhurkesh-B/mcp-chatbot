import os
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from groq import Groq
import requests
from dotenv import load_dotenv
from app.linkedin_service import LinkedInService
from mcp_integration import MCPIntegration
from rag_integration import RAGIntegration

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
linkedin_service = LinkedInService()

class Query(BaseModel):
    query: str
    include_linkedin: bool = True
    linkedin_username: str = None

class LinkedInQuery(BaseModel):
    username: str
    action: str
    params: dict = {}

class ChatMessage(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(message: ChatMessage):
    try:
        # Get combined context from all sources
        mcp_context = mcp.get_combined_context()
        rag_context = rag.get_context()

        # Search RAG content for relevant information
        rag_search = rag.search_content(message.message)
        rag_data = rag_search["content"] if rag_search["found"] else "No specific information found in the records."

        # Create system message
        system_message = f"""Hi! I'm Dhurkesh's personal assistant. I have access to his information and can help answer questions about him.

        Here's what I know about Dhurkesh:
        {rag_data}

        Additional Information:
        {mcp_context}
        
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

        return {"response": chat_completion.choices[0].message.content}

    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            
            # Get combined context from all sources
            mcp_context = mcp.get_combined_context()
            rag_context = rag.get_context()

            # Search RAG content for relevant information
            rag_search = rag.search_content(message)
            rag_data = rag_search["content"] if rag_search["found"] else "No specific information found in the records."

            # Create system message
            system_message = f"""Hi! I'm Dhurkesh's personal assistant. I have access to his information and can help answer questions about him.

            Here's what I know about Dhurkesh:
            {rag_data}

            Additional Information:
            {mcp_context}
            
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

            await websocket.send_text(chat_completion.choices[0].message.content)
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

def get_linkedin_context(username: str):
    try:
        # Fetch and save posts
        linkedin_service.fetch_and_save_posts(username)
        
        # Get saved posts
        posts_data = linkedin_service.get_saved_posts(limit=5)
        posts = posts_data.get("posts", [])
        
        # Get top posts
        top_posts = linkedin_service.get_top_posts(metric="Like Count", top_n=3)
        
        # Format posts content for context
        recent_posts_content = []
        for post in posts:
            recent_posts_content.append(
                f"Post: {post.get('Text', '')}\n"
                f"Likes: {post.get('Like Count', 0)}\n"
                f"Posted on: {post.get('Posted Date', '')}\n"
            )
        
        top_posts_content = []
        for post in top_posts.get("posts", []):
            top_posts_content.append(
                f"Top Post: {post.get('Text', '')}\n"
                f"Likes: {post.get('Like Count', 0)}\n"
                f"Posted on: {post.get('Posted Date', '')}\n"
            )
        
        return {
            "username": username,
            "recent_posts": posts,
            "top_posts": top_posts.get("posts", []),
            "total_posts": posts_data.get("total_posts", 0),
            "recent_posts_content": recent_posts_content,
            "top_posts_content": top_posts_content
        }
    except Exception as e:
        print(f"Error getting LinkedIn context: {str(e)}")
        return {
            "username": username,
            "recent_posts": [],
            "top_posts": [],
            "total_posts": 0,
            "recent_posts_content": [],
            "top_posts_content": []
        }

@app.post("/query")
async def process_query(query: Query):
    try:
        # Get GitHub context
        github_context = get_github_context()
        context_str = (
            f"GitHub User: {github_context['username']}\n"
            f"Repositories: {', '.join(github_context['repositories'])}\n"
            f"Recent Activity: {', '.join(github_context['recent_activity'])}\n"
        )
        
        # Get LinkedIn context if requested
        if query.include_linkedin and query.linkedin_username:
            linkedin_context = get_linkedin_context(query.linkedin_username)
            context_str += (
                f"\nLinkedIn User: {linkedin_context['username']}\n"
                f"Total Posts: {linkedin_context['total_posts']}\n"
                f"Recent Posts: {len(linkedin_context['recent_posts'])}\n"
                f"Top Posts: {len(linkedin_context['top_posts'])}\n\n"
                f"Recent Posts Content:\n"
                f"{''.join(linkedin_context['recent_posts_content'])}\n"
                f"Top Posts Content:\n"
                f"{''.join(linkedin_context['top_posts_content'])}\n"
            )
        
        # Generate response with Groq
        chat_completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a technical assistant with access to GitHub and LinkedIn data. "
                               "Use the following context to answer user queries. You have access to the full content "
                               "of LinkedIn posts, including their text, likes, and posting dates:\n"
                               f"{context_str}"
                },
                {
                    "role": "user",
                    "content": query.query
                }
            ],
            temperature=0.5,
            max_tokens=1024,
            stream=False,
        )
        
        return {"response": chat_completion.choices[0].message.content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/linkedin")
async def process_linkedin_query(query: LinkedInQuery):
    try:
        if query.action == "fetch_posts":
            result = linkedin_service.fetch_and_save_posts(query.username)
        elif query.action == "get_posts":
            result = linkedin_service.get_saved_posts(
                start=query.params.get("start", 0),
                limit=query.params.get("limit", 5)
            )
        elif query.action == "search_posts":
            result = linkedin_service.search_posts(query.params.get("keyword", ""))
        elif query.action == "top_posts":
            result = linkedin_service.get_top_posts(
                metric=query.params.get("metric", "Like Count"),
                top_n=query.params.get("top_n", 5)
            )
        elif query.action == "posts_by_date":
            result = linkedin_service.get_posts_by_date(
                start_date=query.params.get("start_date", ""),
                end_date=query.params.get("end_date", "")
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid action specified")
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Model Context Protocol (MCP) Chatbot

A chatbot implementation that follows the Model Context Protocol specification, combining RAG (Retrieval Augmented Generation) with GitHub integration. This implementation ensures proper context management and memory handling for AI interactions.

## Features

- 🤖 MCP-compliant context management
- 📚 RAG (Retrieval Augmented Generation) for local content search
- 🔗 GitHub integration for accessing public repository information
- 💬 WebSocket support for real-time communication
- 🎨 Modern UI with responsive design
- 📝 Markdown support for rich text formatting

## Prerequisites

- Python 3.8 or higher
- GitHub account with a fine-grained personal access token
- Groq API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
GROQ_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_token
GITHUB_USER=your_github_username
```

## GitHub Token Setup

Create a fine-grained personal access token with the following permissions:

1. Repository access: "Public repositories" (read-only)
2. Repository permissions:
   - `Metadata` (read-only)
3. Account permissions:
   - `Events` (read-only)

## Project Structure

```
.
├── app/
│   ├── main.py           # FastAPI application
│   └── __init__.py
├── static/
│   ├── styles.css        # CSS styles
│   └── images/          # Image assets
├── templates/
│   └── index.html       # Chat interface template
├── mcp/
│   ├── __init__.py
│   ├── protocol.py      # MCP protocol implementation
│   ├── context.py       # Context management
│   └── memory.py        # Memory handling
├── integrations/
│   ├── __init__.py
│   ├── github.py        # GitHub integration
│   └── rag.py          # RAG functionality
├── requirements.txt     # Python dependencies
└── .env                # Environment variables
```

## MCP Implementation

This project implements the Model Context Protocol with the following components:

1. Context Management
   - Structured context storage
   - Context retrieval and updating
   - Context persistence

2. Memory Handling
   - Short-term memory for current session
   - Long-term memory for persistent storage
   - Memory retrieval and updating

3. Protocol Compliance
   - Standardized context format
   - Proper context injection
   - Context validation

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## Usage

1. The chat interface will appear with a message input field at the bottom
2. Type your question and press Enter or click the Send button
3. The chatbot will respond using:
   - MCP-compliant context management
   - Local content (RAG)
   - Public GitHub repositories
   - User profile information

## API Endpoints

- `GET /`: Main chat interface
- `POST /chat`: Send chat messages
- `WebSocket /ws`: Real-time chat communication
- `POST /context`: Update context
- `GET /context`: Retrieve current context

## Dependencies

- FastAPI: Web framework
- Uvicorn: ASGI server
- Groq: LLM integration
- Python-dotenv: Environment variable management
- Requests: HTTP client
- Markdown: Text formatting
- Jinja2: Template engine

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Groq for providing the LLM API
- GitHub for repository access
- FastAPI for the web framework
- Model Context Protocol specification

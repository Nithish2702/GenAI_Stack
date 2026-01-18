# Workflow Builder Backend

FastAPI backend for the No-Code/Low-Code workflow builder application.

## Features

- **Document Management**: Upload, process, and manage documents (PDF, TXT)
- **Vector Search**: ChromaDB integration for semantic search
- **LLM Integration**: OpenAI GPT and Google Gemini support
- **Web Search**: SerpAPI integration for real-time information
- **Workflow Engine**: Execute custom workflows with drag-and-drop components
- **Chat Interface**: Persistent chat sessions with message history

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- Docker (optional)

### Local Development

1. **Clone and navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and database URL
```

5. **Set up PostgreSQL database**
```bash
# Create database
createdb workflow_db

# Or use Docker
docker run --name postgres -e POSTGRES_DB=workflow_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15
```

6. **Run the application**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Setup

1. **Create .env file with your API keys**
```bash
cp .env.example .env
# Edit .env with your API keys
```

2. **Run with Docker Compose**
```bash
docker-compose up --build
```

## API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `POST /api/v1/documents/{id}/process` - Process document (extract text, create embeddings)
- `GET /api/v1/documents/` - List documents
- `GET /api/v1/documents/{id}` - Get document
- `DELETE /api/v1/documents/{id}` - Delete document

### Workflows
- `POST /api/v1/workflows/` - Create workflow
- `GET /api/v1/workflows/` - List workflows
- `GET /api/v1/workflows/{id}` - Get workflow
- `PUT /api/v1/workflows/{id}` - Update workflow
- `DELETE /api/v1/workflows/{id}` - Delete workflow
- `POST /api/v1/workflows/{id}/validate` - Validate workflow
- `POST /api/v1/workflows/execute` - Execute workflow

### Chat
- `POST /api/v1/chat/sessions` - Create chat session
- `GET /api/v1/chat/sessions` - List chat sessions
- `GET /api/v1/chat/sessions/{id}` - Get chat session
- `GET /api/v1/chat/sessions/{id}/messages` - Get chat messages
- `DELETE /api/v1/chat/sessions/{id}` - Delete chat session

## Environment Variables

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/workflow_db
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
SERPAPI_KEY=your_serpapi_key_here
SECRET_KEY=your_secret_key_here
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

## Architecture

### Core Components

1. **User Query Component**: Entry point for user queries
2. **Knowledge Base Component**: Document processing and semantic search
3. **LLM Engine Component**: AI response generation with multiple providers
4. **Output Component**: Response formatting and chat interface

### Services

- **DocumentService**: Handle file uploads, text extraction, and document management
- **VectorService**: ChromaDB integration for embeddings and semantic search
- **LLMService**: Multi-provider LLM integration (OpenAI, Gemini)
- **WorkflowService**: Workflow execution engine and validation

### Database Models

- **Document**: Store document metadata and extracted text
- **Workflow**: Store workflow definitions and component configurations
- **ChatSession**: Manage chat sessions for workflows
- **ChatMessage**: Store individual chat messages with metadata

## Development

### Adding New Components

1. Update the workflow validation logic in `WorkflowService`
2. Add component execution logic in `_execute_workflow_logic`
3. Update frontend component library

### Adding New LLM Providers

1. Extend `LLMService` with new provider methods
2. Update the `generate_response` method
3. Add provider-specific configuration options

## Testing

```bash
# Run tests (when implemented)
pytest

# Test API endpoints
curl -X GET http://localhost:8000/health
```

## Deployment

### Production Setup

1. Use production-grade PostgreSQL instance
2. Set up proper environment variables
3. Configure reverse proxy (nginx)
4. Set up SSL certificates
5. Configure monitoring and logging

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (when implemented).
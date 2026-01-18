# Workflow Builder - No-Code/Low-Code AI Application

A full-stack web application that enables users to visually create and interact with intelligent workflows using drag-and-drop components. Build custom AI workflows that handle user queries, extract knowledge from documents, interact with language models, and return answers through a chat interface.

## 🎯 Features

### Core Components
1. **User Query Component** - Entry point for user queries
2. **Knowledge Base Component** - Document processing and semantic search
3. **LLM Engine Component** - AI response generation with multiple providers
4. **Output Component** - Chat interface for displaying responses

### Key Capabilities
- 🎨 Visual workflow builder with drag-and-drop interface
- 📄 Document upload and processing (PDF, TXT)
- 🔍 Semantic search using vector embeddings
- 🤖 Multiple LLM providers (OpenAI GPT, Google Gemini)
- 🌐 Web search integration (SerpAPI)
- 💬 Interactive chat interface
- ✅ Workflow validation
- 💾 Persistent chat history
- 🐳 Docker containerization

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │   Workflow   │  │     Chat     │      │
│  │              │  │   Builder    │  │  Interface   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Document    │  │   Workflow   │  │     Chat     │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Vector    │  │     LLM      │  │   SerpAPI    │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
        ┌──────────────┐        ┌──────────────┐
        │  PostgreSQL  │        │   ChromaDB   │
        │   Database   │        │ Vector Store │
        └──────────────┘        └──────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- API Keys:
  - OpenAI API Key
  - Google API Key (optional)
  - SerpAPI Key (optional)

### Using Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd workflow-builder
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start all services**
```bash
docker-compose up --build
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start PostgreSQL (using Docker)
docker run --name postgres -e POSTGRES_DB=workflow_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15

# Run the backend
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📖 Usage Guide

### 1. Upload Documents
- Navigate to **Documents** page
- Click **Upload Document**
- Select PDF or TXT files
- Documents are automatically processed and embedded

### 2. Build a Workflow
- Go to **Workflows** page
- Click **New Workflow**
- Drag components from the left panel onto the canvas:
  - **User Query** - Entry point
  - **Knowledge Base** - Document retrieval
  - **LLM Engine** - AI processing
  - **Output** - Response display
- Connect components by dragging from one to another
- Click on components to configure them
- Click **Build Stack** to validate
- Click **Save** to save the workflow

### 3. Configure Components

#### User Query Component
- Set placeholder text for the input field

#### Knowledge Base Component
- Set number of results to retrieve
- Toggle context passing to LLM

#### LLM Engine Component
- Choose model provider (OpenAI/Gemini)
- Select specific model
- Add custom system prompt
- Enable web search
- Adjust temperature

#### Output Component
- Choose response format
- Toggle source display

### 4. Chat with Your Workflow
- Click **Chat with Stack** from workflow builder
- Or select a workflow from the Chat page
- Type your question and press Enter
- View AI-generated responses with sources

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI framework
- **React Router** - Navigation
- **ReactFlow** - Workflow visualization
- **Axios** - HTTP client
- **Vite** - Build tool
- **Lucide React** - Icons

### Backend
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **ChromaDB** - Vector store
- **OpenAI** - Embeddings & LLM
- **Google Gemini** - Alternative LLM
- **PyMuPDF** - PDF text extraction
- **SerpAPI** - Web search

## 📁 Project Structure

```
workflow-builder/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── chat.py
│   │   │   │   ├── documents.py
│   │   │   │   └── workflows.py
│   │   │   └── routes.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── database/
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   ├── schemas/
│   │   │   ├── chat.py
│   │   │   ├── document.py
│   │   │   └── workflow.py
│   │   ├── services/
│   │   │   ├── document_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── vector_service.py
│   │   │   └── workflow_service.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.js
│   │   │   ├── chat.js
│   │   │   ├── documents.js
│   │   │   └── workflows.js
│   │   ├── components/
│   │   │   ├── Layout.jsx
│   │   │   ├── ComponentPanel.jsx
│   │   │   └── ConfigPanel.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Documents.jsx
│   │   │   ├── Workflows.jsx
│   │   │   ├── WorkflowBuilder.jsx
│   │   │   └── Chat.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 API Endpoints

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `POST /api/v1/documents/{id}/process` - Process document
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
- `GET /api/v1/chat/sessions/{id}/messages` - Get messages
- `DELETE /api/v1/chat/sessions/{id}` - Delete session

## 🔐 Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/workflow_db

# Optional
GOOGLE_API_KEY=your_google_api_key_here
SERPAPI_KEY=your_serpapi_key_here
SECRET_KEY=your_secret_key_here
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

## 🐳 Docker Deployment

### Build and Run
```bash
docker-compose up --build
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🧪 Testing

### Test Document Upload
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.pdf"
```

### Test Workflow Execution
```bash
curl -X POST "http://localhost:8000/api/v1/workflows/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": 1,
    "query": "What is machine learning?"
  }'
```

## 📊 Database Schema

### Documents
- id, filename, original_filename, file_path, file_size, content_type, extracted_text, is_processed, created_at, updated_at

### Workflows
- id, name, description, components (JSON), connections (JSON), created_at, updated_at

### ChatSessions
- id, workflow_id, session_name, created_at, updated_at

### ChatMessages
- id, session_id, message_type, content, message_metadata (JSON), created_at

## 🎨 UI Components

### Dashboard
- Statistics cards for documents, workflows, and chat sessions
- Quick action buttons
- Recent activity

### Workflow Builder
- Component library panel
- Visual canvas with ReactFlow
- Configuration panel
- Validation feedback
- Save and execute controls

### Chat Interface
- Message history
- Input field
- Source citations
- Real-time responses

## 🚧 Future Enhancements

- [ ] User authentication and authorization
- [ ] Workflow templates
- [ ] Advanced analytics
- [ ] Workflow versioning
- [ ] Collaborative editing
- [ ] More component types
- [ ] Custom component creation
- [ ] Kubernetes deployment manifests
- [ ] Monitoring with Prometheus/Grafana
- [ ] Logging with ELK Stack

## 📝 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

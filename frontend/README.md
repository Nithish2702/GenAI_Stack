# Workflow Builder Frontend

React frontend for the No-Code/Low-Code workflow builder application.

## Features

- **Dashboard**: Overview of documents, workflows, and chat sessions
- **Document Management**: Upload and manage documents with processing status
- **Workflow Builder**: Drag-and-drop interface for building workflows
- **Chat Interface**: Interactive chat with workflow execution
- **Responsive Design**: Clean, modern UI with smooth interactions

## Tech Stack

- React 18
- React Router for navigation
- ReactFlow for workflow visualization
- Axios for API calls
- Vite for fast development
- Lucide React for icons

## Setup

### Prerequisites

- Node.js 18+
- Backend API running on `http://localhost:8000`

### Installation

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Create environment file**
```bash
cp .env.example .env
```

4. **Start development server**
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API client and endpoints
│   │   ├── client.js     # Axios instance
│   │   ├── workflows.js  # Workflow API
│   │   ├── documents.js  # Document API
│   │   └── chat.js       # Chat API
│   ├── components/       # Reusable components
│   │   ├── Layout.jsx    # Main layout with sidebar
│   │   └── ComponentPanel.jsx  # Workflow components
│   ├── pages/            # Page components
│   │   ├── Dashboard.jsx
│   │   ├── Documents.jsx
│   │   ├── Workflows.jsx
│   │   ├── WorkflowBuilder.jsx
│   │   └── Chat.jsx
│   ├── App.jsx           # Main app component
│   ├── main.jsx          # Entry point
│   └── index.css         # Global styles
├── index.html
├── vite.config.js
└── package.json
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Features Overview

### Dashboard
- Quick stats for documents, workflows, and chat sessions
- Quick action cards for common tasks
- Navigation to all main sections

### Documents
- Upload PDF and TXT files
- Automatic processing for embeddings
- View processing status
- Delete documents

### Workflows
- Create and edit workflows
- Drag-and-drop workflow builder
- Visual workflow representation
- Save and validate workflows
- Test workflows directly

### Chat
- Interactive chat interface
- Execute workflows with queries
- View response sources
- Persistent chat sessions

## API Integration

The frontend connects to the backend API at `http://localhost:8000` by default. Configure this in `.env`:

```
VITE_API_URL=http://localhost:8000
```

## Development

### Adding New Components

1. Create component in `src/components/`
2. Add corresponding CSS file
3. Import and use in pages

### Adding New Pages

1. Create page in `src/pages/`
2. Add route in `src/App.jsx`
3. Add navigation link in `src/components/Layout.jsx`

### Styling

- Global styles in `src/index.css`
- Component-specific styles in separate CSS files
- CSS variables for consistent theming

## Building for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

## Deployment

### Static Hosting

Deploy the `dist/` folder to any static hosting service:
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Environment Variables

- `VITE_API_URL` - Backend API URL (default: http://localhost:8000)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

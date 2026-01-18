import React from 'react'
import { MessageSquare, Sparkles, Database, Globe, FileOutput, Menu } from 'lucide-react'
import './StackSidebar.css'

const components = [
  { type: 'user_query', label: 'User Input', icon: MessageSquare, description: 'Enter point for querys' },
  { type: 'llm_engine', label: 'LLM (Gemini)', icon: Sparkles, description: 'Run a query with Google Gemini LLM' },
  { type: 'knowledge_base', label: 'Knowledge Base', icon: Database, description: 'Let LLM search info in your file' },
  { type: 'web_search', label: 'Web Search', icon: Globe, description: 'Search the web for information' },
  { type: 'output', label: 'Output', icon: FileOutput, description: 'Output of the result nodes as text' }
]

const StackSidebar = ({ stackName }) => {
  const onDragStart = (event, type, label) => {
    event.dataTransfer.setData('application/reactflow', type)
    event.dataTransfer.setData('label', label)
    event.dataTransfer.effectAllowed = 'move'
  }

  return (
    <div className="stack-sidebar">
      <div className="sidebar-header">
        <h2>{stackName}</h2>
        <button className="sidebar-menu-btn">
          <Menu size={20} />
        </button>
      </div>

      <div className="sidebar-section">
        <h3>Components</h3>
        <div className="components-list">
          {components.map(({ type, label, icon: Icon, description }) => (
            <div
              key={type}
              className="component-item"
              draggable
              onDragStart={(e) => onDragStart(e, type, label)}
            >
              <div className="component-icon">
                <Icon size={18} />
              </div>
              <div className="component-info">
                <div className="component-label">{label}</div>
                <div className="component-desc">{description}</div>
              </div>
              <div className="component-drag-handle">
                <Menu size={16} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default StackSidebar

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, ExternalLink, Trash2, MessageSquare } from 'lucide-react'
import { workflowsAPI } from '../api/workflows'
import CreateStackModal from '../components/CreateStackModal'
import ChatModal from '../components/ChatModal'
import './StacksList.css'

const StacksList = () => {
  const navigate = useNavigate()
  const [stacks, setStacks] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [showChat, setShowChat] = useState(false)
  const [selectedStack, setSelectedStack] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStacks()
  }, [])

  const loadStacks = async () => {
    try {
      const data = await workflowsAPI.getAll()
      setStacks(data)
    } catch (error) {
      console.error('Failed to load stacks:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateStack = async (name, description) => {
    try {
      const newStack = await workflowsAPI.create({
        name,
        description,
        components: [],
        connections: []
      })
      navigate(`/stacks/${newStack.id}`)
    } catch (error) {
      console.error('Failed to create stack:', error)
      alert('Failed to create stack')
    }
  }

  const handleDeleteStack = async (stackId, stackName, e) => {
    e.stopPropagation() // Prevent card click
    
    if (!confirm(`Are you sure you want to delete "${stackName}"? This will also delete all associated documents and chat history.`)) {
      return
    }

    try {
      await workflowsAPI.delete(stackId)
      setStacks(stacks.filter(s => s.id !== stackId))
    } catch (error) {
      console.error('Failed to delete stack:', error)
      alert('Failed to delete stack')
    }
  }

  const handleOpenChat = (stack, e) => {
    e.stopPropagation() // Prevent card click
    setSelectedStack(stack)
    setShowChat(true)
  }

  const handleCloseChat = () => {
    setShowChat(false)
    setSelectedStack(null)
  }

  return (
    <div className="stacks-page">
      <header className="stacks-header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">🤖</div>
            <span>GenAI Stack</span>
          </div>
          <div className="user-avatar">👤</div>
        </div>
      </header>

      <main className="stacks-main">
        <div className="stacks-title-bar">
          <h1>My Stacks</h1>
          <button className="btn-new-stack" onClick={() => setShowModal(true)}>
            <Plus size={18} />
            New Stack
          </button>
        </div>

        {stacks.length === 0 && !loading ? (
          <div className="empty-state">
            <div className="empty-card">
              <h2>Create New Stack</h2>
              <p>Start building your generative AI apps with our essential tools and frameworks</p>
              <button className="btn-new-stack" onClick={() => setShowModal(true)}>
                <Plus size={18} />
                New Stack
              </button>
            </div>
          </div>
        ) : (
          <div className="stacks-grid">
            {stacks.map(stack => (
              <div key={stack.id} className="stack-card">
                <div className="stack-card-content">
                  <h3>{stack.name}</h3>
                  <p>{stack.description || 'No description'}</p>
                </div>
                <div className="stack-card-actions">
                  <button 
                    className="stack-action-btn stack-chat-btn"
                    onClick={(e) => handleOpenChat(stack, e)}
                    title="Chat with stack"
                  >
                    <MessageSquare size={16} />
                    <span>Chat</span>
                  </button>
                  <button 
                    className="stack-action-btn stack-edit-btn"
                    onClick={() => navigate(`/stacks/${stack.id}`)}
                    title="Edit stack"
                  >
                    <ExternalLink size={16} />
                    <span>Edit</span>
                  </button>
                  <button 
                    className="stack-delete-btn"
                    onClick={(e) => handleDeleteStack(stack.id, stack.name, e)}
                    title="Delete stack"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {showModal && (
        <CreateStackModal
          onClose={() => setShowModal(false)}
          onCreate={handleCreateStack}
        />
      )}

      {showChat && selectedStack && (
        <ChatModal
          workflowId={selectedStack.id}
          workflowName={selectedStack.name}
          onClose={handleCloseChat}
        />
      )}
    </div>
  )
}

export default StacksList

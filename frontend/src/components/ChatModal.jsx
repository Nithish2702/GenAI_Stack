import React, { useState, useEffect, useRef } from 'react'
import { X, Send, History, Plus, Trash2 } from 'lucide-react'
import { workflowsAPI } from '../api/workflows'
import { chatAPI } from '../api/chat'
import './ChatModal.css'

const ChatModal = ({ workflowId, workflowName, onClose }) => {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [sessions, setSessions] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    loadSessions()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadSessions = async () => {
    try {
      const allSessions = await chatAPI.getSessions(parseInt(workflowId))
      setSessions(allSessions)
      
      // If there are existing sessions, load the most recent one
      if (allSessions.length > 0) {
        await loadSession(allSessions[0].id)
      } else {
        // Create new session if none exist
        await createNewSession()
      }
    } catch (error) {
      console.error('Failed to load sessions:', error)
      await createNewSession()
    }
  }

  const createNewSession = async () => {
    try {
      const session = await chatAPI.createSession(
        parseInt(workflowId),
        `Chat ${new Date().toLocaleString()}`
      )
      setSessionId(session.id)
      setMessages([])
      setSessions(prev => [session, ...prev])
    } catch (error) {
      console.error('Failed to create session:', error)
    }
  }

  const loadSession = async (id) => {
    try {
      const session = await chatAPI.getSession(id)
      setSessionId(id)
      
      // Convert database messages to UI format
      const formattedMessages = session.messages.map(msg => ({
        role: msg.message_type,
        content: msg.content,
        sources: msg.message_metadata?.sources || []
      }))
      
      setMessages(formattedMessages)
      setShowHistory(false)
    } catch (error) {
      console.error('Failed to load session:', error)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input }
    setMessages([...messages, userMessage])
    setInput('')
    setLoading(true)

    try {
      const result = await workflowsAPI.execute(
        parseInt(workflowId),
        input,
        sessionId
      )

      const assistantMessage = {
        role: 'assistant',
        content: result.response,
        sources: result.sources || []
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Execution failed:', error)
      
      // Extract error message from response
      let errorMsg = 'Sorry, something went wrong. Please try again.'
      if (error.response?.data?.detail) {
        errorMsg = `Error: ${error.response.data.detail}`
      } else if (error.message) {
        errorMsg = `Error: ${error.message}`
      }
      
      const errorMessage = {
        role: 'assistant',
        content: errorMsg,
        error: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleNewChat = () => {
    createNewSession()
    setShowHistory(false)
  }

  const handleDeleteSession = async (sessionIdToDelete, e) => {
    e.stopPropagation() // Prevent loading the session when clicking delete
    
    if (!confirm('Are you sure you want to delete this chat session?')) {
      return
    }

    try {
      await chatAPI.deleteSession(sessionIdToDelete)
      
      // Remove from sessions list
      setSessions(prev => prev.filter(s => s.id !== sessionIdToDelete))
      
      // If we deleted the current session, create a new one
      if (sessionIdToDelete === sessionId) {
        await createNewSession()
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
      alert('Failed to delete chat session')
    }
  }

  return (
    <div className="chat-modal-overlay" onClick={onClose}>
      <div className="chat-modal" onClick={(e) => e.stopPropagation()}>
        <div className="chat-modal-header">
          <div className="chat-modal-title">
            <div className="logo-icon">🤖</div>
            <span>GenAI Stack Chat</span>
          </div>
          <div className="chat-header-actions">
            <button 
              className="chat-history-btn" 
              onClick={() => setShowHistory(!showHistory)}
              title="Chat History"
            >
              <History size={20} />
            </button>
            <button 
              className="chat-new-btn" 
              onClick={handleNewChat}
              title="New Chat"
            >
              <Plus size={20} />
            </button>
            <button className="chat-modal-close" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="chat-modal-content">
          {showHistory && (
            <div className="chat-history-sidebar">
              <h3>Chat History</h3>
              <div className="chat-sessions-list">
                {sessions.map((session) => (
                  <div
                    key={session.id}
                    className={`chat-session-item ${session.id === sessionId ? 'active' : ''}`}
                    onClick={() => loadSession(session.id)}
                  >
                    <div className="session-info">
                      <div className="session-name">
                        {session.session_name || `Session ${session.id}`}
                      </div>
                      <div className="session-date">
                        {new Date(session.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <button
                      className="session-delete-btn"
                      onClick={(e) => handleDeleteSession(session.id, e)}
                      title="Delete session"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
                {sessions.length === 0 && (
                  <div className="no-sessions">No previous chats</div>
                )}
              </div>
            </div>
          )}

          <div className="chat-modal-body">
            {messages.length === 0 ? (
              <div className="chat-empty">
                <div className="logo-icon-large">🤖</div>
                <h3>GenAI Stack Chat</h3>
                <p>Start a conversation to test your stack</p>
              </div>
            ) : (
              <div className="chat-messages">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`chat-message ${msg.role}`}>
                    <div className="message-avatar">
                      {msg.role === 'user' ? '👤' : '🤖'}
                    </div>
                    <div className="message-content">
                      {msg.content}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="chat-message assistant">
                    <div className="message-avatar">🤖</div>
                    <div className="message-content">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        <div className="chat-modal-footer">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Send a message"
            disabled={loading}
          />
          <button 
            className="chat-send-btn" 
            onClick={handleSend}
            disabled={!input.trim() || loading}
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatModal

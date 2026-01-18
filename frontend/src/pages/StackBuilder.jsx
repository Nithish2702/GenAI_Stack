import React, { useState, useCallback, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import ReactFlow, { 
  Background, 
  Controls, 
  addEdge, 
  useNodesState, 
  useEdgesState,
  MarkerType
} from 'reactflow'
import 'reactflow/dist/style.css'
import { Save, Play, MessageSquare } from 'lucide-react'
import { workflowsAPI } from '../api/workflows'
import StackSidebar from '../components/StackSidebar'
import ChatModal from '../components/ChatModal'
import { nodeTypes } from '../components/CustomNodes'
import './StackBuilder.css'

const StackBuilder = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [stackName, setStackName] = useState('New Stack')
  const [saving, setSaving] = useState(false)
  const [showChat, setShowChat] = useState(false)

  useEffect(() => {
    if (id && id !== 'new') {
      loadStack()
    }
  }, [id])

  const getNodeType = (type) => {
    const typeMap = {
      'user_query': 'userQuery',
      'knowledge_base': 'knowledgeBase',
      'llm_engine': 'llmEngine',
      'output': 'output'
    }
    return typeMap[type] || 'default'
  }

  const loadStack = async () => {
    try {
      const stack = await workflowsAPI.getById(id)
      setStackName(stack.name)
      
      if (stack.components && stack.components.length > 0) {
        const flowNodes = stack.components.map(comp => ({
          id: comp.id,
          type: getNodeType(comp.type),
          position: comp.position || { x: 250, y: 250 },
          data: { 
            label: getComponentLabel(comp.type),
            type: comp.type, 
            config: comp.data || {},
            workflowId: id,  // Pass workflow ID to nodes
            onConfigChange: updateNodeConfig
          }
        }))
        setNodes(flowNodes)
      }
      
      if (stack.connections && stack.connections.length > 0) {
        const flowEdges = stack.connections.map((conn, idx) => ({
          id: conn.id || `e${idx}`,
          source: conn.source_id || conn.source,
          target: conn.target_id || conn.target,
          markerEnd: { type: MarkerType.ArrowClosed }
        }))
        setEdges(flowEdges)
      }
    } catch (error) {
      console.error('Failed to load stack:', error)
    }
  }

  const getComponentLabel = (type) => {
    const labels = {
      'user_query': 'User Input',
      'knowledge_base': 'Knowledge Base',
      'llm_engine': 'LLM (OpenAI)',
      'web_search': 'Web Search',
      'output': 'Output'
    }
    return labels[type] || type
  }

  const onConnect = useCallback((params) => {
    setEdges((eds) => addEdge({
      ...params,
      markerEnd: { type: MarkerType.ArrowClosed }
    }, eds))
  }, [])

  const onDrop = useCallback((event) => {
    event.preventDefault()
    const type = event.dataTransfer.getData('application/reactflow')
    const label = event.dataTransfer.getData('label')
    
    const reactFlowBounds = event.currentTarget.getBoundingClientRect()
    const position = {
      x: event.clientX - reactFlowBounds.left - 140,
      y: event.clientY - reactFlowBounds.top - 100
    }
    
    const newNode = {
      id: `${type}-${Date.now()}`,
      type: getNodeType(type),
      position,
      data: { 
        label, 
        type, 
        config: {},
        workflowId: id,  // Pass workflow ID to new nodes
        onConfigChange: updateNodeConfig
      }
    }
    
    setNodes((nds) => nds.concat(newNode))
  }, [id])

  const onDragOver = useCallback((event) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      const components = nodes.map(node => ({
        id: node.id,
        type: node.data.type,
        position: node.position,
        data: node.data.config || {}
      }))

      const connections = edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target
      }))

      const stackData = {
        name: stackName,
        description: '',
        components,
        connections
      }

      if (id && id !== 'new') {
        await workflowsAPI.update(id, stackData)
        alert('Stack saved successfully!')
      } else {
        const created = await workflowsAPI.create(stackData)
        navigate(`/stacks/${created.id}`, { replace: true })
        alert('Stack created successfully!')
      }
    } catch (error) {
      console.error('Save failed:', error)
      alert('Failed to save stack')
    } finally {
      setSaving(false)
    }
  }

  const updateNodeConfig = (nodeId, config) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, config } }
          : node
      )
    )
  }

  return (
    <div className="stack-builder">
      <header className="builder-header">
        <div className="header-left">
          <div className="logo" onClick={() => navigate('/stacks')}>
            <div className="logo-icon">🤖</div>
            <span>GenAI Stack</span>
          </div>
        </div>
        <div className="header-right">
          <button className="btn-save" onClick={handleSave} disabled={saving}>
            <Save size={18} />
            Save
          </button>
          <div className="user-avatar">👤</div>
        </div>
      </header>

      <div className="builder-content">
        <StackSidebar stackName={stackName} />
        
        <div className="flow-area">
          <div className="flow-container" onDrop={onDrop} onDragOver={onDragOver}>
            {nodes.length === 0 ? (
              <div className="flow-empty-state">
                <div className="empty-icon">📦</div>
                <p>Drag & drop to get started</p>
              </div>
            ) : null}
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              nodeTypes={nodeTypes}
              fitView
            >
              <Background color="#ddd" gap={16} />
              <Controls />
            </ReactFlow>
          </div>
          
          <div className="flow-actions">
            <button className="btn-build-stack" onClick={handleSave}>
              <Play size={20} />
              Build Stack
            </button>
            <button 
              className="btn-chat" 
              onClick={() => setShowChat(true)}
              disabled={!id || id === 'new'}
            >
              <MessageSquare size={20} />
            </button>
          </div>
        </div>
      </div>

      {showChat && (
        <ChatModal
          workflowId={id}
          workflowName={stackName}
          onClose={() => setShowChat(false)}
        />
      )}
    </div>
  )
}

export default StackBuilder

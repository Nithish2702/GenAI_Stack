import React, { memo } from 'react'
import { Handle, Position, useReactFlow } from 'reactflow'
import { Settings, Upload, Trash2, X } from 'lucide-react'
import { documentsAPI } from '../api/documents'
import './CustomNodes.css'

export const UserQueryNode = memo(({ data, id }) => {
  const { deleteElements } = useReactFlow()
  
  const handleChange = (key, value) => {
    if (data.onConfigChange) {
      data.onConfigChange(id, { ...data.config, [key]: value })
    }
  }

  const handleDelete = () => {
    deleteElements({ nodes: [{ id }] })
  }

  return (
    <div className="custom-node user-query-node">
      <div className="node-header">
        <Settings size={14} />
        <span>User Input</span>
        <button className="node-delete-btn" onClick={handleDelete} title="Delete node">
          <X size={14} />
        </button>
      </div>
      <div className="node-body">
        <div className="node-field">
          <label>Query</label>
          <input
            type="text"
            placeholder="Write your query here"
            value={data.config?.query || ''}
            onChange={(e) => handleChange('query', e.target.value)}
          />
        </div>
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  )
})

export const KnowledgeBaseNode = memo(({ data, id }) => {
  const { deleteElements } = useReactFlow()
  const [uploading, setUploading] = React.useState(false)

  const handleChange = (key, value) => {
    if (data.onConfigChange) {
      data.onConfigChange(id, { ...data.config, [key]: value })
    }
  }

  const handleDelete = () => {
    deleteElements({ nodes: [{ id }] })
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    try {
      // Upload with workflow ID to link document to this stack
      const doc = await documentsAPI.upload(file, data.workflowId)
      await documentsAPI.process(doc.id)
      
      const uploadedFiles = data.config?.uploaded_files || []
      uploadedFiles.push({
        id: doc.id,
        name: doc.original_filename,
        filename: doc.filename
      })
      
      handleChange('uploaded_files', uploadedFiles)
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Failed to upload file')
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  const handleRemoveFile = (index) => {
    const uploadedFiles = [...(data.config?.uploaded_files || [])]
    uploadedFiles.splice(index, 1)
    handleChange('uploaded_files', uploadedFiles)
  }

  return (
    <div className="custom-node knowledge-base-node">
      <Handle type="target" position={Position.Left} />
      <div className="node-header">
        <Settings size={14} />
        <span>Knowledge Base</span>
        <button className="node-delete-btn" onClick={handleDelete} title="Delete node">
          <X size={14} />
        </button>
      </div>
      <div className="node-body">
        <div className="node-field">
          <label>Let LLM search info in your file</label>
        </div>
        <div className="node-field">
          <label>File for Knowledge Base</label>
          <input
            type="file"
            id={`kb-upload-${id}`}
            accept=".pdf,.txt"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
          <label htmlFor={`kb-upload-${id}`} className="upload-btn">
            <Upload size={14} />
            {uploading ? 'Uploading...' : 'Upload File'}
          </label>
          {data.config?.uploaded_files?.map((file, idx) => (
            <div key={idx} className="uploaded-file">
              <span>📄 {file.name}</span>
              <button onClick={() => handleRemoveFile(idx)}>
                <Trash2 size={12} />
              </button>
            </div>
          ))}
        </div>
        <div className="node-field">
          <label>Embedding Model</label>
          <select
            value={data.config?.embedding_model || 'models/embedding-001'}
            onChange={(e) => handleChange('embedding_model', e.target.value)}
          >
            <option value="models/embedding-001">Gemini Embedding 001</option>
          </select>
        </div>
        <div className="node-field">
          <div className="connection-point">Context</div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  )
})

export const LLMEngineNode = memo(({ data, id }) => {
  const { deleteElements } = useReactFlow()
  
  const handleChange = (key, value) => {
    if (data.onConfigChange) {
      data.onConfigChange(id, { ...data.config, [key]: value })
    }
  }

  const handleDelete = () => {
    deleteElements({ nodes: [{ id }] })
  }

  return (
    <div className="custom-node llm-engine-node">
      <Handle type="target" position={Position.Left} />
      <div className="node-header">
        <Settings size={14} />
        <span>LLM (Gemini)</span>
        <button className="node-delete-btn" onClick={handleDelete} title="Delete node">
          <X size={14} />
        </button>
      </div>
      <div className="node-body">
        <div className="node-field">
          <label>Run a query with Google Gemini LLM</label>
        </div>
        <div className="node-field">
          <label>Model</label>
          <select
            value={data.config?.model_name || 'models/gemini-2.5-flash'}
            onChange={(e) => handleChange('model_name', e.target.value)}
          >
            <option value="models/gemini-2.5-flash">Gemini 2.5 Flash (Fastest)</option>
            <option value="models/gemini-2.5-pro">Gemini 2.5 Pro (Most Capable)</option>
            <option value="models/gemini-2.0-flash">Gemini 2.0 Flash</option>
          </select>
        </div>
        <div className="node-field">
          <label>Prompt</label>
          <textarea
            rows="3"
            placeholder="You are a helpful PDF assistant. Use web search if the PDF lacks content"
            value={data.config?.custom_prompt || ''}
            onChange={(e) => handleChange('custom_prompt', e.target.value)}
          />
          <div className="prompt-tags">
            <span>CONTEXT (context)</span>
            <span>User Query (query)</span>
          </div>
        </div>
        <div className="node-field">
          <label>Temperature</label>
          <input
            type="number"
            step="0.1"
            min="0"
            max="1"
            value={data.config?.temperature || 0.75}
            onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
          />
        </div>
        {/* Web Search is disabled by default (SerpAPI not configured) */}
        {/* Uncomment to enable web search feature:
        <div className="node-field checkbox-field">
          <label>
            <input
              type="checkbox"
              checked={data.config?.use_web_search || false}
              onChange={(e) => handleChange('use_web_search', e.target.checked)}
            />
            <span>Websearch Tool</span>
          </label>
        </div>
        */}
        <div className="node-field">
          <div className="connection-point">Output</div>
        </div>
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  )
})

export const OutputNode = memo(({ data, id }) => {
  const { deleteElements } = useReactFlow()
  
  const handleDelete = () => {
    deleteElements({ nodes: [{ id }] })
  }

  return (
    <div className="custom-node output-node">
      <Handle type="target" position={Position.Left} />
      <div className="node-header">
        <Settings size={14} />
        <span>Output</span>
        <button className="node-delete-btn" onClick={handleDelete} title="Delete node">
          <X size={14} />
        </button>
      </div>
      <div className="node-body">
        <div className="node-field">
          <label>Output of the result nodes as text</label>
        </div>
        <div className="node-field">
          <label>Output Text</label>
          <textarea
            rows="2"
            placeholder="Output will be generated based on query"
            value={data.config?.output_text || ''}
            readOnly
          />
        </div>
        <div className="node-field">
          <div className="connection-point output-point">Output</div>
        </div>
      </div>
    </div>
  )
})

export const nodeTypes = {
  userQuery: UserQueryNode,
  knowledgeBase: KnowledgeBaseNode,
  llmEngine: LLMEngineNode,
  output: OutputNode
}

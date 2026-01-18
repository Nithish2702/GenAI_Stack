import React, { useState } from 'react'
import { X } from 'lucide-react'
import './CreateStackModal.css'

const CreateStackModal = ({ onClose, onCreate }) => {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (name.trim()) {
      onCreate(name, description)
      onClose()
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Stack</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Chat With PDF"
                autoFocus
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g., Chat with your pdf docs"
                rows={4}
              />
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-create" disabled={!name.trim()}>
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateStackModal

import client from './client'

export const documentsAPI = {
  upload: async (file, workflowId = null) => {
    const formData = new FormData()
    formData.append('file', file)
    
    // Add workflow_id as query parameter if provided
    const url = workflowId 
      ? `/api/v1/documents/upload?workflow_id=${workflowId}`
      : '/api/v1/documents/upload'
    
    const { data } = await client.post(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return data
  },

  process: async (documentId) => {
    const { data } = await client.post(`/api/v1/documents/${documentId}/process`)
    return data
  },

  getAll: async () => {
    const { data } = await client.get('/api/v1/documents/')
    return data
  },

  getById: async (id) => {
    const { data } = await client.get(`/api/v1/documents/${id}`)
    return data
  },

  delete: async (id) => {
    const { data } = await client.delete(`/api/v1/documents/${id}`)
    return data
  }
}

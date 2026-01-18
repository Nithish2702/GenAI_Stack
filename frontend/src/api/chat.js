import client from './client'

export const chatAPI = {
  createSession: async (workflowId, sessionName) => {
    const { data } = await client.post('/api/v1/chat/sessions', {
      workflow_id: workflowId,
      session_name: sessionName
    })
    return data
  },

  getSessions: async (workflowId = null) => {
    const params = workflowId ? { workflow_id: workflowId } : {}
    const { data } = await client.get('/api/v1/chat/sessions', { params })
    return data
  },

  getSession: async (sessionId) => {
    const { data } = await client.get(`/api/v1/chat/sessions/${sessionId}`)
    return data
  },

  getMessages: async (sessionId) => {
    const { data } = await client.get(`/api/v1/chat/sessions/${sessionId}/messages`)
    return data
  },

  deleteSession: async (sessionId) => {
    const { data } = await client.delete(`/api/v1/chat/sessions/${sessionId}`)
    return data
  }
}

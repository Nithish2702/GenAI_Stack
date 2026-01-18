import client from './client'

export const workflowsAPI = {
  create: async (workflow) => {
    const { data } = await client.post('/api/v1/workflows/', workflow)
    return data
  },

  getAll: async () => {
    const { data } = await client.get('/api/v1/workflows/')
    return data
  },

  getById: async (id) => {
    const { data } = await client.get(`/api/v1/workflows/${id}`)
    return data
  },

  update: async (id, workflow) => {
    const { data } = await client.put(`/api/v1/workflows/${id}`, workflow)
    return data
  },

  delete: async (id) => {
    const { data } = await client.delete(`/api/v1/workflows/${id}`)
    return data
  },

  validate: async (id) => {
    const { data } = await client.post(`/api/v1/workflows/${id}/validate`)
    return data
  },

  execute: async (workflowId, query, sessionId = null) => {
    const { data } = await client.post('/api/v1/workflows/execute', {
      workflow_id: workflowId,
      query,
      session_id: sessionId
    })
    return data
  }
}

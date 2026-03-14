import client from './client'

export const experiments = {
  list: (state) =>
    client.get('/experiments/', { params: state ? { state } : {} }).then((r) => r.data),

  get: (id) =>
    client.get(`/experiments/${id}`).then((r) => r.data),

  create: (payload) =>
    client.post('/experiments/', payload).then((r) => r.data),

  transition: (id, state) =>
    client.patch(`/experiments/${id}/state`, { state }).then((r) => r.data),

  setVerdict: (id, verdict, verdict_reason) =>
    client.post(`/experiments/${id}/verdict`, { verdict, verdict_reason }).then((r) => r.data),

  delete: (id) =>
    client.delete(`/experiments/${id}`).then((r) => r.data),
}

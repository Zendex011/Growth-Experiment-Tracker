import client from './client'

export const results = {
  add: (experimentId, payload) =>
    client.post(`/experiments/${experimentId}/results`, payload).then((r) => r.data),

  list: (experimentId) =>
    client.get(`/experiments/${experimentId}/results`).then((r) => r.data),
}

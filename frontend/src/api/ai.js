import client from './client'

export const ai = {
  improveHypothesis: (roughIdea) =>
    client.post('/ai/hypothesis', { rough_idea: roughIdea }).then((r) => r.data),

  suggestVerdict: (payload) =>
    client.post('/ai/suggest-verdict', payload).then((r) => r.data),

  summarize: (experimentId) =>
    client.post(`/ai/summarize/${experimentId}`).then((r) => r.data),
}

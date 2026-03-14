import { useState, useCallback } from 'react'
import { ai } from '../api/ai'

export function useAISuggestion() {
  const [suggestion, setSuggestion] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const reset = useCallback(() => {
    setSuggestion(null)
    setError(null)
  }, [])

  const improveHypothesis = useCallback(async (roughIdea) => {
    setLoading(true)
    setError(null)
    setSuggestion(null)
    try {
      const result = await ai.improveHypothesis(roughIdea)
      setSuggestion(result)
      return result
    } catch (err) {
      setError(err.message)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  const suggestVerdict = useCallback(async (payload) => {
    setLoading(true)
    setError(null)
    setSuggestion(null)
    try {
      const result = await ai.suggestVerdict(payload)
      setSuggestion(result)
      return result
    } catch (err) {
      setError(err.message)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  const summarize = useCallback(async (experimentId) => {
    setLoading(true)
    setError(null)
    setSuggestion(null)
    try {
      const result = await ai.summarize(experimentId)
      setSuggestion(result)
      return result
    } catch (err) {
      setError(err.message)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    suggestion, loading, error, reset,
    improveHypothesis, suggestVerdict, summarize,
  }
}

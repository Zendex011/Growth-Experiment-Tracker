import { useState, useEffect, useCallback } from 'react'
import { experiments as api } from '../api/experiments'
import { results as resultsApi } from '../api/results'

export function useExperiments() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(async (stateFilter) => {
    setLoading(true)
    setError(null)
    try {
      const result = await api.list(stateFilter)
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function useExperiment(id) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(async () => {
    if (!id) return
    setLoading(true)
    setError(null)
    try {
      const result = await api.get(id)
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => { fetch() }, [fetch])

  const transition = useCallback(async (toState) => {
    const updated = await api.transition(id, toState)
    setData((prev) => ({ ...prev, state: updated.state }))
    await fetch()
    return updated
  }, [id, fetch])

  const setVerdict = useCallback(async (verdict, reason) => {
    const updated = await api.setVerdict(id, verdict, reason)
    setData(updated)
    return updated
  }, [id])

  const addResult = useCallback(async (payload) => {
    const result = await resultsApi.add(id, payload)
    await fetch()
    return result
  }, [id, fetch])

  return { data, loading, error, refetch: fetch, transition, setVerdict, addResult }
}

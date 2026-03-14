import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { experiments as api } from '../api/experiments'
import { useAISuggestion } from '../hooks/useAISuggestion'
import AISuggestion from '../components/AISuggestion'

const EMPTY = {
  title: '',
  hypothesis: '',
  metric_name: '',
  metric_baseline: '',
}

export default function NewExperiment() {
  const navigate = useNavigate()
  const [form, setForm] = useState(EMPTY)
  const [roughIdea, setRoughIdea] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const { suggestion, loading: aiLoading, improveHypothesis, reset: resetAI } = useAISuggestion()

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))

  const handleAIImprove = async () => {
    if (!roughIdea.trim()) return
    await improveHypothesis(roughIdea)
  }

  const handleAcceptHypothesis = (text) => {
    setForm((f) => ({ ...f, hypothesis: text }))
    resetAI()
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const exp = await api.create({
        title: form.title,
        hypothesis: form.hypothesis,
        metric_name: form.metric_name,
        metric_baseline: parseFloat(form.metric_baseline),
      })
      navigate(`/experiments/${exp.id}`)
    } catch (err) {
      setError(err.message || 'Failed to create experiment.')
      setLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-8 animate-fade-up">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-1.5 text-xs text-slate-mid hover:text-slate-white font-body mb-4 transition-colors"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Dashboard
        </button>
        <h1 className="font-display font-800 text-2xl text-slate-white mb-1">
          New Experiment
        </h1>
        <p className="text-sm text-slate-mid font-body">
          Define your hypothesis before you start collecting data.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 animate-fade-up" style={{ animationDelay: '80ms' }}>

        {/* Title */}
        <div className="space-y-1.5">
          <label className="block text-xs font-body text-slate-soft">Experiment title</label>
          <input
            value={form.title}
            onChange={set('title')}
            required
            minLength={3}
            maxLength={200}
            placeholder="e.g. Green CTA Button Test"
            className="w-full bg-ink-muted border border-subtle rounded-xl px-4 py-3
              text-sm font-body text-slate-white placeholder-slate-edge
              focus:outline-none focus:border-signal-blue focus:ring-1 focus:ring-signal-blue transition-all"
          />
        </div>

        {/* AI Hypothesis Helper */}
        <div className="rounded-2xl border border-subtle p-4 space-y-3 bg-ink-soft">
          <p className="text-xs font-mono uppercase tracking-widest text-slate-mid">
            ✦ AI Hypothesis Builder
          </p>
          <div className="flex gap-2">
            <input
              value={roughIdea}
              onChange={(e) => setRoughIdea(e.target.value)}
              placeholder="Describe your rough idea…"
              className="flex-1 bg-ink border border-subtle rounded-xl px-3 py-2.5
                text-sm font-body text-slate-white placeholder-slate-edge
                focus:outline-none focus:border-signal-blue focus:ring-1 focus:ring-signal-blue transition-all"
            />
            <button
              type="button"
              onClick={handleAIImprove}
              disabled={!roughIdea.trim() || aiLoading}
              className="px-4 py-2.5 rounded-xl border border-signal-blue text-signal-blue
                bg-signal-blue-dim hover:bg-signal-blue hover:text-white
                text-sm font-body font-medium transition-all active:scale-95
                disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {aiLoading
                ? <span className="w-3.5 h-3.5 border border-current border-t-transparent rounded-full animate-spin" />
                : <span>✦</span>}
              Improve
            </button>
          </div>

          <AISuggestion
            suggestion={suggestion}
            loading={aiLoading}
            label="Improved Hypothesis"
            onAccept={handleAcceptHypothesis}
            acceptLabel="Use this hypothesis"
          />
        </div>

        {/* Hypothesis */}
        <div className="space-y-1.5">
          <label className="block text-xs font-body text-slate-soft">
            Hypothesis
            <span className="text-slate-edge ml-1">(or use AI above)</span>
          </label>
          <textarea
            value={form.hypothesis}
            onChange={set('hypothesis')}
            required
            minLength={10}
            rows={3}
            placeholder="We believe that [change] will [metric impact] because [reason]."
            className="w-full bg-ink-muted border border-subtle rounded-xl px-4 py-3
              text-sm font-body text-slate-white placeholder-slate-edge resize-none
              focus:outline-none focus:border-signal-blue focus:ring-1 focus:ring-signal-blue transition-all"
          />
        </div>

        {/* Metric */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="block text-xs font-body text-slate-soft">Metric name</label>
            <input
              value={form.metric_name}
              onChange={set('metric_name')}
              required
              placeholder="e.g. signup_rate"
              className="w-full bg-ink-muted border border-subtle rounded-xl px-4 py-3
                text-sm font-mono text-slate-white placeholder-slate-edge
                focus:outline-none focus:border-signal-blue focus:ring-1 focus:ring-signal-blue transition-all"
            />
          </div>
          <div className="space-y-1.5">
            <label className="block text-xs font-body text-slate-soft">Baseline value</label>
            <input
              type="number"
              step="any"
              min="0"
              value={form.metric_baseline}
              onChange={set('metric_baseline')}
              required
              placeholder="e.g. 3.2"
              className="w-full bg-ink-muted border border-subtle rounded-xl px-4 py-3
                text-sm font-mono text-slate-white placeholder-slate-edge
                focus:outline-none focus:border-signal-blue focus:ring-1 focus:ring-signal-blue transition-all"
            />
          </div>
        </div>

        {error && (
          <p className="text-sm text-signal-red font-body">{error}</p>
        )}

        <div className="flex gap-3 pt-2">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-5 py-2.5 rounded-xl border border-subtle text-slate-soft
              hover:text-slate-white hover:border-slate-edge text-sm font-body transition-all"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 py-2.5 rounded-xl bg-signal-blue hover:bg-blue-500 text-white
              text-sm font-body font-medium transition-all active:scale-95 disabled:opacity-50"
          >
            {loading ? 'Creating…' : 'Create Experiment'}
          </button>
        </div>
      </form>
    </div>
  )
}

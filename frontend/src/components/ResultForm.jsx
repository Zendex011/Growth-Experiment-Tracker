import { useState } from 'react'
import { useAISuggestion } from '../hooks/useAISuggestion'

const EMPTY = {
  control_value: '',
  variant_value: '',
  sample_size_control: '',
  sample_size_variant: '',
  duration_days: '',
}

export default function ResultForm({ experiment, onSubmit }) {
  const [form, setForm] = useState(EMPTY)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const { suggestion, loading: aiLoading, suggestVerdict } = useAISuggestion()

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const payload = {
        control_value: parseFloat(form.control_value),
        variant_value: parseFloat(form.variant_value),
        sample_size_control: parseInt(form.sample_size_control),
        sample_size_variant: parseInt(form.sample_size_variant),
        duration_days: parseInt(form.duration_days),
      }
      await onSubmit(payload)
      setForm(EMPTY)
    } catch (err) {
      setError(err.message || 'Failed to log result.')
    } finally {
      setLoading(false)
    }
  }

  const handleAISuggest = () => {
    if (!form.control_value || !form.variant_value) return
    suggestVerdict({
      metric_name: experiment.metric_name,
      control_value: parseFloat(form.control_value),
      variant_value: parseFloat(form.variant_value),
      sample_size_control: parseInt(form.sample_size_control) || 100,
      sample_size_variant: parseInt(form.sample_size_variant) || 100,
      duration_days: parseInt(form.duration_days) || 7,
    })
  }

  const lift = form.control_value && form.variant_value && parseFloat(form.control_value) !== 0
    ? ((parseFloat(form.variant_value) - parseFloat(form.control_value)) / parseFloat(form.control_value) * 100)
    : null

  return (
    <div className="space-y-5">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Value inputs */}
        <div className="grid grid-cols-2 gap-3">
          <Field
            label={`Control (${experiment.metric_name})`}
            type="number" step="any"
            value={form.control_value}
            onChange={set('control_value')}
            placeholder={String(experiment.metric_baseline)}
            required
          />
          <Field
            label={`Variant (${experiment.metric_name})`}
            type="number" step="any"
            value={form.variant_value}
            onChange={set('variant_value')}
            placeholder="e.g. 4.1"
            required
          />
        </div>

        {/* Live lift preview */}
        {lift !== null && (
          <div className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-mono
            ${lift >= 0 ? 'bg-signal-green-dim text-signal-green' : 'bg-signal-red-dim text-signal-red'}`}>
            <span className="font-medium">{lift >= 0 ? '+' : ''}{lift.toFixed(1)}%</span>
            <span className="text-xs opacity-70">relative lift</span>
          </div>
        )}

        {/* Sample sizes */}
        <div className="grid grid-cols-2 gap-3">
          <Field
            label="Control sample size"
            type="number"
            value={form.sample_size_control}
            onChange={set('sample_size_control')}
            placeholder="e.g. 1400"
            required
          />
          <Field
            label="Variant sample size"
            type="number"
            value={form.sample_size_variant}
            onChange={set('sample_size_variant')}
            placeholder="e.g. 1380"
            required
          />
        </div>

        <Field
          label="Duration (days)"
          type="number"
          value={form.duration_days}
          onChange={set('duration_days')}
          placeholder="e.g. 14"
          required
        />

        {error && (
          <p className="text-xs text-signal-red font-body">{error}</p>
        )}

        <div className="flex gap-2 pt-1">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 py-2.5 rounded-xl bg-signal-blue hover:bg-blue-500 text-white
              text-sm font-body font-medium transition-all active:scale-95 disabled:opacity-50"
          >
            {loading ? 'Saving…' : 'Log Result'}
          </button>

          {form.control_value && form.variant_value && (
            <button
              type="button"
              onClick={handleAISuggest}
              disabled={aiLoading}
              className="px-4 py-2.5 rounded-xl border border-signal-purple text-signal-purple
                bg-signal-purple-dim hover:bg-signal-purple hover:text-white
                text-sm font-body font-medium transition-all active:scale-95 disabled:opacity-50 flex items-center gap-2"
            >
              {aiLoading
                ? <span className="w-3.5 h-3.5 border border-current border-t-transparent rounded-full animate-spin" />
                : <span>✦</span>
              }
              AI Analyse
            </button>
          )}
        </div>
      </form>

      {/* AI Verdict Suggestion */}
      {suggestion && !aiLoading && (
        <div className={`rounded-xl p-4 border space-y-2 animate-fade-up
          ${suggestion.degraded
            ? 'border-slate-edge bg-ink-muted'
            : 'border-signal-purple bg-signal-purple-dim border-opacity-50'}`}>
          <p className="text-xs font-mono uppercase tracking-widest text-signal-purple opacity-70">
            AI Analysis
          </p>
          {suggestion.degraded ? (
            <p className="text-sm text-slate-soft">{suggestion.reason}</p>
          ) : (
            <>
              {suggestion.verdict && (
                <p className="text-sm font-medium text-slate-white">
                  Suggested verdict: <span className="text-signal-purple capitalize">{suggestion.verdict}</span>
                </p>
              )}
              {suggestion.interpretation && (
                <p className="text-sm text-slate-soft leading-relaxed">{suggestion.interpretation}</p>
              )}
              {suggestion.suggested_reason && (
                <p className="text-xs text-slate-mid italic">{suggestion.suggested_reason}</p>
              )}
              <p className="text-xs text-slate-edge mt-1">This is a suggestion — you decide the final verdict.</p>
            </>
          )}
        </div>
      )}
    </div>
  )
}

function Field({ label, ...props }) {
  return (
    <div className="space-y-1.5">
      <label className="block text-xs font-body text-slate-soft">{label}</label>
      <input
        {...props}
        className="w-full bg-ink-muted border border-subtle rounded-xl px-3 py-2.5
          text-sm font-mono text-slate-white placeholder-slate-edge
          focus:outline-none focus:border-signal-blue focus:ring-1 focus:ring-signal-blue
          transition-all"
      />
    </div>
  )
}

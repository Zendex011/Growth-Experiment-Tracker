import { useState } from 'react'
import { VERDICT_META } from '../utils/states'

export default function VerdictForm({ onSubmit }) {
  const [verdict, setVerdict] = useState('')
  const [reason, setReason] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!verdict) return
    setLoading(true)
    setError(null)
    try {
      await onSubmit(verdict, reason)
    } catch (err) {
      setError(err.message || 'Failed to set verdict.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Verdict options */}
      <div className="grid grid-cols-3 gap-2">
        {Object.entries(VERDICT_META).map(([key, meta]) => (
          <button
            key={key}
            type="button"
            onClick={() => setVerdict(key)}
            className={`flex flex-col items-center gap-1.5 px-3 py-3 rounded-xl border text-sm
              font-body transition-all active:scale-95
              ${verdict === key
                ? `${meta.bg} ${meta.border} ${meta.color} ring-1 ring-current`
                : 'border-subtle text-slate-soft hover:border-slate-edge hover:text-slate-white'
              }`}
          >
            <span className="text-lg">{meta.icon}</span>
            <span className="text-xs font-medium">{meta.label}</span>
          </button>
        ))}
      </div>

      {/* Reason */}
      <div className="space-y-1.5">
        <label className="block text-xs font-body text-slate-soft">
          Reason <span className="text-slate-edge">(optional)</span>
        </label>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          rows={2}
          placeholder="Why this verdict?"
          className="w-full bg-ink-muted border border-subtle rounded-xl px-3 py-2.5
            text-sm font-body text-slate-white placeholder-slate-edge resize-none
            focus:outline-none focus:border-signal-blue focus:ring-1 focus:ring-signal-blue transition-all"
        />
      </div>

      {error && <p className="text-xs text-signal-red">{error}</p>}

      <button
        type="submit"
        disabled={!verdict || loading}
        className="w-full py-2.5 rounded-xl bg-signal-blue hover:bg-blue-500 text-white
          text-sm font-body font-medium transition-all active:scale-95
          disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {loading ? 'Locking verdict…' : 'Lock Verdict'}
      </button>

      <p className="text-xs text-slate-edge text-center">
        Verdict cannot be changed once set
      </p>
    </form>
  )
}

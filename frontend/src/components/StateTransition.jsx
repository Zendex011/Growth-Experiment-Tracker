import { useState } from 'react'
import { allowedTransitions, TRANSITION_LABELS } from '../utils/states'

const BUTTON_STYLES = {
  running:   'bg-signal-green-dim border-signal-green text-signal-green hover:bg-signal-green hover:text-ink',
  paused:    'bg-signal-amber-dim border-signal-amber text-signal-amber hover:bg-signal-amber hover:text-ink',
  completed: 'bg-signal-blue-dim border-signal-blue text-signal-blue hover:bg-signal-blue hover:text-ink',
}

export default function StateTransition({ state, hasResults, onTransition }) {
  const [loading, setLoading] = useState(null)
  const [error, setError] = useState(null)

  const next = allowedTransitions(state)

  if (next.length === 0) return null

  const handleClick = async (toState) => {
    if (toState === 'completed' && !hasResults) {
      setError('Log at least one result before completing.')
      return
    }
    setLoading(toState)
    setError(null)
    try {
      await onTransition(toState)
    } catch (err) {
      setError(err.message || 'Transition failed.')
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {next.map((toState) => (
          <button
            key={toState}
            onClick={() => handleClick(toState)}
            disabled={loading !== null}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl border text-sm font-body font-medium
              transition-all duration-150 active:scale-95 disabled:opacity-50
              ${BUTTON_STYLES[toState] || 'bg-ink-muted border-slate-edge text-slate-soft'}`}
          >
            {loading === toState ? (
              <span className="w-3.5 h-3.5 border border-current border-t-transparent rounded-full animate-spin" />
            ) : null}
            {TRANSITION_LABELS[toState] ?? toState}
          </button>
        ))}
      </div>
      {error && (
        <p className="text-xs text-signal-red font-body">{error}</p>
      )}
    </div>
  )
}

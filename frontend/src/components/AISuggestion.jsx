import { useState } from 'react'

export default function AISuggestion({ suggestion, loading, label, onAccept, acceptLabel = 'Accept' }) {
  const [editing, setEditing] = useState(false)
  const [editedText, setEditedText] = useState('')

  if (loading) {
    return (
      <div className="rounded-xl border border-subtle p-4 space-y-2 animate-pulse">
        <div className="shimmer-bg h-3 w-24 rounded" />
        <div className="shimmer-bg h-4 w-full rounded" />
        <div className="shimmer-bg h-4 w-3/4 rounded" />
      </div>
    )
  }

  if (!suggestion) return null

  if (suggestion.degraded) {
    return (
      <div className="rounded-xl border border-slate-edge bg-ink-muted p-4">
        <p className="text-xs font-mono uppercase tracking-widest text-slate-mid mb-1">AI Unavailable</p>
        <p className="text-sm text-slate-soft">{suggestion.reason || 'AI suggestion unavailable. Please write this manually.'}</p>
      </div>
    )
  }

  const displayText = suggestion.hypothesis || suggestion.summary || suggestion.interpretation || ''

  const handleAccept = () => {
    if (onAccept) onAccept(editing ? editedText : displayText)
    setEditing(false)
  }

  const handleEdit = () => {
    setEditedText(displayText)
    setEditing(true)
  }

  return (
    <div className="rounded-xl border border-signal-blue border-opacity-40 bg-signal-blue-dim p-4 space-y-3 animate-fade-up">
      <div className="flex items-center gap-2">
        <span className="text-signal-blue text-sm">✦</span>
        <p className="text-xs font-mono uppercase tracking-widest text-signal-blue opacity-80">
          {label || 'AI Suggestion'}
        </p>
        {suggestion.confidence && (
          <span className="ml-auto text-xs font-mono text-slate-mid">
            confidence: {suggestion.confidence}
          </span>
        )}
      </div>

      {editing ? (
        <textarea
          value={editedText}
          onChange={(e) => setEditedText(e.target.value)}
          rows={3}
          className="w-full bg-ink border border-slate-edge rounded-xl px-3 py-2.5
            text-sm font-body text-slate-white resize-none
            focus:outline-none focus:border-signal-blue focus:ring-1 focus:ring-signal-blue"
        />
      ) : (
        <div className="max-h-48 overflow-y-auto pr-2 custom-scrollbar">
          <p className="text-sm text-slate-white leading-relaxed">{displayText}</p>
        </div>
      )}

      {onAccept && (
        <div className="flex items-center gap-2 pt-1">
          <button
            onClick={handleAccept}
            className="px-3 py-1.5 rounded-lg bg-signal-blue hover:bg-blue-500 text-white
              text-xs font-body font-medium transition-all active:scale-95"
          >
            {acceptLabel}
          </button>
          {!editing ? (
            <button
              onClick={handleEdit}
              className="px-3 py-1.5 rounded-lg border border-subtle text-slate-soft
                hover:text-slate-white hover:border-slate-edge text-xs font-body transition-all"
            >
              Edit first
            </button>
          ) : (
            <button
              onClick={() => setEditing(false)}
              className="px-3 py-1.5 rounded-lg border border-subtle text-slate-soft
                hover:text-slate-white text-xs font-body transition-all"
            >
              Cancel
            </button>
          )}
          <span className="text-xs text-slate-edge ml-auto">You're in control</span>
        </div>
      )}
    </div>
  )
}

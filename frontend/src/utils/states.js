// Mirrors backend VALID_TRANSITIONS — keep in sync with state_machine.py
export const VALID_TRANSITIONS = {
  draft:     ['running'],
  running:   ['paused', 'completed'],
  paused:    ['running', 'completed'],
  completed: [],
}

export const STATE_META = {
  draft: {
    label: 'Draft',
    color: 'text-slate-soft',
    bg: 'bg-ink-muted',
    border: 'border-slate-edge',
    dot: 'bg-slate-soft',
    description: 'Not yet started',
  },
  running: {
    label: 'Running',
    color: 'text-signal-green',
    bg: 'bg-signal-green-dim',
    border: 'border-signal-green',
    dot: 'bg-signal-green',
    description: 'Actively collecting data',
  },
  paused: {
    label: 'Paused',
    color: 'text-signal-amber',
    bg: 'bg-signal-amber-dim',
    border: 'border-signal-amber',
    dot: 'bg-signal-amber',
    description: 'Temporarily halted',
  },
  completed: {
    label: 'Completed',
    color: 'text-signal-blue',
    bg: 'bg-signal-blue-dim',
    border: 'border-signal-blue',
    dot: 'bg-signal-blue',
    description: 'Experiment finished',
  },
}

export const VERDICT_META = {
  ship: {
    label: 'Ship it',
    color: 'text-signal-green',
    bg: 'bg-signal-green-dim',
    border: 'border-signal-green',
    icon: '🚀',
  },
  rollback: {
    label: 'Rollback',
    color: 'text-signal-red',
    bg: 'bg-signal-red-dim',
    border: 'border-signal-red',
    icon: '↩️',
  },
  iterate: {
    label: 'Iterate',
    color: 'text-signal-purple',
    bg: 'bg-signal-purple-dim',
    border: 'border-signal-purple',
    icon: '🔄',
  },
}

export const TRANSITION_LABELS = {
  running:   'Start Experiment',
  paused:    'Pause',
  completed: 'Mark Complete',
}

export const allowedTransitions = (state) => VALID_TRANSITIONS[state] ?? []

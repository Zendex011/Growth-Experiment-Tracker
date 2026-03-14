import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, message: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, message: error.message }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-ink flex items-center justify-center p-8">
          <div className="max-w-md w-full border border-signal-red border-opacity-40 rounded-2xl p-8 bg-signal-red-dim bg-opacity-30">
            <p className="font-mono text-xs text-signal-red uppercase tracking-widest mb-3">
              Render Error
            </p>
            <h2 className="font-display text-xl text-slate-white mb-2">Something broke</h2>
            <p className="text-sm text-slate-soft font-body mb-6">
              {this.state.message || 'An unexpected error occurred.'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 rounded-lg bg-ink-muted hover:bg-ink-soft text-slate-white text-sm font-body transition-all"
            >
              Reload page
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

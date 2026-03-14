import { formatDistanceToNow, format } from 'date-fns'

export const relativeTime = (iso) => {
  if (!iso) return '—'
  return formatDistanceToNow(new Date(iso), { addSuffix: true })
}

export const absoluteTime = (iso) => {
  if (!iso) return '—'
  return format(new Date(iso), 'MMM d, yyyy · HH:mm')
}

export const pct = (value, decimals = 1) => {
  if (value == null) return '—'
  return `${Number(value).toFixed(decimals)}%`
}

export const relativeLift = (control, variant) => {
  if (!control || control === 0) return null
  return ((variant - control) / control) * 100
}

export const liftLabel = (control, variant) => {
  const lift = relativeLift(control, variant)
  if (lift == null) return '—'
  const sign = lift >= 0 ? '+' : ''
  return `${sign}${lift.toFixed(1)}%`
}

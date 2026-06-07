export default function LoadingSpinner({ label = 'Solving...' }) {
  return (
    <div className="loading-wrap" role="status" aria-live="polite">
      <div className="spinner" />
      <span>{label}</span>
    </div>
  )
}

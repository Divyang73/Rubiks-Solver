export default function LoadingSkeleton({ lines = 4, compact = false }) {
  return (
    <div className={`skeleton-card ${compact ? 'compact' : ''}`} aria-hidden="true">
      {Array.from({ length: lines }).map((_, idx) => (
        <div key={idx} className="skeleton-line" />
      ))}
    </div>
  )
}

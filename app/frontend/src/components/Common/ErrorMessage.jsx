import Button from './Button'

export default function ErrorMessage({ message, detail, onRetry, retryDisabled = false }) {
  if (!message) return null
  return (
    <div className="error-banner" role="alert">
      <p className="error-title">{message}</p>
      {detail && <p className="error-detail">{detail}</p>}
      {onRetry && (
        <div className="error-actions">
          <Button variant="secondary" onClick={onRetry} disabled={retryDisabled}>
            Retry
          </Button>
        </div>
      )}
    </div>
  )
}

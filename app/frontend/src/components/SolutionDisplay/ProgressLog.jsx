import { useEffect, useRef } from 'react'

export default function ProgressLog({ logs }) {
  const endRef = useRef(null)

  useEffect(() => {
    // Auto-scroll to the bottom when new logs arrive
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs])

  if (!logs || logs.length === 0) return null

  return (
    <div className="progress-log-container">
      <div className="progress-log-header">
        <span className="pulse-dot"></span>
        <span>Live Progress</span>
      </div>
      <div className="progress-log-content">
        {logs.map((log) => (
          <div key={log.id} className="progress-log-entry slide-in">
            {log.message}
          </div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  )
}

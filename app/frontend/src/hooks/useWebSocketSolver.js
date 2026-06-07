import { useCallback, useEffect, useRef, useState } from 'react'
import { toast } from 'react-hot-toast'

export default function useWebSocketSolver() {
  const [status, setStatus] = useState('idle') // idle | connecting | solving | done | error
  const [progressLog, setProgressLog] = useState([])
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const wsRef = useRef(null)

  const cleanup = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  // Ensure connection is closed if component unmounts
  useEffect(() => {
    return cleanup
  }, [cleanup])

  const solve = useCallback(
    (cubeState, algorithm, includeStats = true) => {
      cleanup()
      setStatus('connecting')
      setProgressLog([])
      setResult(null)
      setError(null)

      // Determine WebSocket URL
      let wsUrl = import.meta.env.VITE_WS_URL
      if (!wsUrl) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        wsUrl = `${protocol}//${window.location.host}/ws/solve`
      }

      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setStatus('solving')
        ws.send(
          JSON.stringify({
            cube_state: cubeState,
            algorithm: algorithm,
            include_stats: includeStats
          })
        )
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.type === 'progress') {
            setProgressLog((prev) => [
              ...prev,
              { id: Date.now() + Math.random(), message: data.message }
            ])
          } else if (data.type === 'result') {
            if (data.success) {
              setResult(data)
              setStatus('done')
              toast.success('Cube solved successfully!')
            } else {
              setError(data.error || 'Unknown solver error')
              setStatus('error')
              toast.error(data.error || 'Solver failed')
            }
            cleanup()
          } else if (data.type === 'error') {
            setError(data.message)
            setStatus('error')
            toast.error(data.message || 'Error from server')
            cleanup()
          }
        } catch (err) {
          console.error('Failed to parse WS message:', err)
        }
      }

      ws.onerror = (err) => {
        console.error('WebSocket error:', err)
        setError('WebSocket connection error')
        setStatus('error')
        toast.error('WebSocket connection error')
      }

      ws.onclose = (event) => {
        if (status === 'solving' || status === 'connecting') {
          // Closed unexpectedly before result
          if (!event.wasClean) {
             setError('Connection lost during solve')
             setStatus('error')
             toast.error('Connection lost during solve')
          }
        }
        wsRef.current = null
      }
    },
    [cleanup, status]
  )

  const cancel = useCallback(() => {
    if (status === 'solving' || status === 'connecting') {
      cleanup()
      setStatus('idle')
      toast('Solve cancelled')
    }
  }, [status, cleanup])

  return { solve, cancel, status, progressLog, result, error }
}

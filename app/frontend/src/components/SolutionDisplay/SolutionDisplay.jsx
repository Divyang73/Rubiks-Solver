import { useMemo } from 'react'
import LoadingSpinner from '../Common/LoadingSpinner'
import ErrorMessage from '../Common/ErrorMessage'
import MoveList from './MoveList'
import Statistics from './Statistics'
import ProgressLog from './ProgressLog'

export default function SolutionDisplay({ result, isLoading, error, progressLog }) {
  const moveCount = useMemo(() => {
    if (!result?.solution) return 0
    return result.solution.trim() ? result.solution.trim().split(/\s+/).length : 0
  }, [result])

  return (
    <section className="solution-card">
      <h3>Solution</h3>
      {isLoading && <LoadingSpinner label="Solving cube..." />}
      
      {/* Show progress logs during solve */}
      {isLoading && progressLog && progressLog.length > 0 && (
        <ProgressLog logs={progressLog} />
      )}

      <ErrorMessage message={error} />
      {!isLoading && !error && result && (
        <>
          <p className="solution-headline">{moveCount} moves</p>
          <MoveList solution={result.solution} />
          <Statistics
            stats={result.statistics}
            moves={result.moves}
            timeMs={result.time_ms}
            algorithm={result.algorithm}
          />
        </>
      )}
    </section>
  )
}

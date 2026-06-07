export default function Statistics({ stats, moves, timeMs, algorithm }) {
  if (!stats) return null
  return (
    <div className="stats-grid">
      <div><strong>Moves:</strong> {moves}</div>
      <div><strong>Computation:</strong> {timeMs} ms</div>
      <div><strong>Nodes:</strong> {stats.nodes_explored ?? 'N/A'}</div>
      <div><strong>Algorithm:</strong> {algorithm}</div>
      <div><strong>Backend:</strong> {stats.solver_backend ?? 'N/A'}</div>
      <div><strong>Optimal:</strong> {stats.optimal ? 'Yes' : 'No'}</div>
    </div>
  )
}

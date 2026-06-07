const ALGORITHMS = [
  {
    key: 'bfs',
    label: 'BFS - Breadth-First Search'
  },
  {
    key: 'dfs',
    label: 'DFS - Depth-First Search'
  },
  {
    key: 'iddfs',
    label: 'IDDFS - Iterative Deepening DFS'
  },
  {
    key: 'idastar',
    label: 'IDA* - Iterative Deepening A* (Recommended)'
  }
]

export default function AlgorithmDropdown({ selectedAlgorithm, onSelect, disabled }) {
  return (
    <div className="algorithm-select-wrap">
      <label htmlFor="algorithm-select">Select Algorithm</label>
      <select
        id="algorithm-select"
        value={selectedAlgorithm}
        onChange={(e) => onSelect(e.target.value)}
        disabled={disabled}
        data-testid="algorithm-select"
      >
        {ALGORITHMS.map((algo) => (
          <option key={algo.key} value={algo.key}>
            {algo.label}
          </option>
        ))}
      </select>
    </div>
  )
}

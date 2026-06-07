import Button from '../Common/Button'

const DIFFICULTIES = [
  { key: 'easy', label: 'Easy (3-4)' },
  { key: 'medium', label: 'Medium (6-8)' },
  { key: 'hard', label: 'Hard (9-10)' }
]

export default function DifficultySelector({ onSelect, disabled }) {
  return (
    <div className="difficulty-wrap" aria-label="Difficulty scramble controls">
      <p className="muted difficulty-title">Difficulty Tiers</p>
      <div className="difficulty-row">
        {DIFFICULTIES.map((difficulty) => (
          <Button
            key={difficulty.key}
            variant="secondary"
            onClick={() => onSelect(difficulty.key)}
            disabled={disabled}
          >
            {difficulty.label}
          </Button>
        ))}
      </div>
      <p className="muted" style={{ fontSize: '0.8rem', marginTop: '0.5rem', lineHeight: '1.2' }}>
        *Hard scrambles may take up to 30 seconds to stream optimal path.
      </p>
    </div>
  )
}

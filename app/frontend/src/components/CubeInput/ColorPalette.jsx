import { COLOR_LABELS } from '../../utils/cubeStateManager'

const COLOR_HEX = {
  W: '#FFFFFF',
  Y: '#FFD500',
  R: '#C41E3A',
  O: '#FF5800',
  B: '#0051BA',
  G: '#009E60'
}

export default function ColorPalette({ activeColor, onColorSelect }) {
  return (
    <div className="palette">
      {Object.keys(COLOR_LABELS).map((color) => (
        <button
          key={color}
          className={`palette-item ${activeColor === color ? 'active' : ''}`}
          onClick={() => onColorSelect(color)}
          title={COLOR_LABELS[color]}
        >
          <span className="swatch" style={{ backgroundColor: COLOR_HEX[color] }} />
          <span>{COLOR_LABELS[color]}</span>
        </button>
      ))}
    </div>
  )
}

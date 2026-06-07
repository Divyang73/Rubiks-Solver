import { FACE_COLORS } from '../../utils/cubeStateManager'

const FACE_LAYOUT = [
  ['.', 'U', '.', '.'],
  ['L', 'F', 'R', 'B'],
  ['.', 'D', '.', '.']
]

const COLOR_HEX = {
  W: '#FFFFFF',
  Y: '#FFD500',
  R: '#C41E3A',
  O: '#FF5800',
  B: '#0051BA',
  G: '#009E60'
}

export default function UnfoldedCube({ cubeState, onStickerClick, activeColor, isLocked }) {
  return (
    <div className="cube-grid-layout">
      {FACE_LAYOUT.map((row, rowIndex) =>
        row.map((face, colIndex) => {
          if (face === '.') {
            return <div className="cube-face-placeholder" key={`${rowIndex}-${colIndex}`} />
          }

          return (
            <div className="cube-face" key={`${rowIndex}-${colIndex}`}>
              <div className="cube-face-label">{face}</div>
              <div className="stickers-grid">
                {cubeState[face].map((color, idx) => {
                  const isCenter = idx === 4
                  const expectedCenter = FACE_COLORS[face]
                  return (
                    <button
                      key={`${face}-${idx}`}
                      className={`sticker ${isCenter ? 'center' : ''}`}
                      style={{ backgroundColor: COLOR_HEX[color] }}
                      onClick={() => onStickerClick(face, idx)}
                      disabled={isLocked || isCenter}
                      title={isCenter ? `${face} center (${expectedCenter})` : `Paint with ${activeColor}`}
                      data-testid={`sticker-${face}-${idx}`}
                    />
                  )
                })}
              </div>
            </div>
          )
        })
      )}
    </div>
  )
}

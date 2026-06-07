export const FACE_ORDER = ['U', 'R', 'F', 'D', 'L', 'B']

export const FACE_COLORS = {
  U: 'W',
  R: 'R',
  F: 'B',
  D: 'Y',
  L: 'O',
  B: 'G'
}

export const COLOR_LABELS = {
  W: 'White',
  Y: 'Yellow',
  R: 'Red',
  O: 'Orange',
  B: 'Blue',
  G: 'Green'
}

export const SOLVED_STATE = {
  U: Array(9).fill('W'),
  R: Array(9).fill('R'),
  F: Array(9).fill('B'),
  D: Array(9).fill('Y'),
  L: Array(9).fill('O'),
  B: Array(9).fill('G')
}

export const CLEAR_STATE = {
  U: Array(9).fill('W'),
  R: Array(9).fill('W'),
  F: Array(9).fill('W'),
  D: Array(9).fill('W'),
  L: Array(9).fill('W'),
  B: Array(9).fill('W')
}

export function cloneCubeState(state) {
  return {
    U: [...state.U],
    R: [...state.R],
    F: [...state.F],
    D: [...state.D],
    L: [...state.L],
    B: [...state.B]
  }
}

export function cubeStateToString(state) {
  return FACE_ORDER.map((face) => state[face].join('')).join('')
}

export function stringToCubeState(value) {
  if (!value || value.length !== 54) return cloneCubeState(SOLVED_STATE)
  return {
    U: value.slice(0, 9).split(''),
    R: value.slice(9, 18).split(''),
    F: value.slice(18, 27).split(''),
    D: value.slice(27, 36).split(''),
    L: value.slice(36, 45).split(''),
    B: value.slice(45, 54).split('')
  }
}

import { cloneCubeState } from './cubeStateManager'

const FACE_ORDER = ['U', 'R', 'F', 'D', 'L', 'B']

function toGlobal(face, index) {
  return FACE_ORDER.indexOf(face) * 9 + index
}

function keyFor(sticker) {
  return `${sticker.pos.x},${sticker.pos.y},${sticker.pos.z}|${sticker.normal.x},${sticker.normal.y},${sticker.normal.z}`
}

// Convert a face-local index into a 3D cubie position + outward normal.
function faceToSticker(face, index) {
  const r = Math.floor(index / 3)
  const c = index % 3

  if (face === 'U') {
    return { pos: { x: c - 1, y: 1, z: r - 1 }, normal: { x: 0, y: 1, z: 0 } }
  }
  if (face === 'D') {
    return { pos: { x: c - 1, y: -1, z: 1 - r }, normal: { x: 0, y: -1, z: 0 } }
  }
  if (face === 'F') {
    return { pos: { x: c - 1, y: 1 - r, z: 1 }, normal: { x: 0, y: 0, z: 1 } }
  }
  if (face === 'B') {
    return { pos: { x: 1 - c, y: 1 - r, z: -1 }, normal: { x: 0, y: 0, z: -1 } }
  }
  if (face === 'R') {
    return { pos: { x: 1, y: 1 - r, z: 1 - c }, normal: { x: 1, y: 0, z: 0 } }
  }
  return { pos: { x: -1, y: 1 - r, z: c - 1 }, normal: { x: -1, y: 0, z: 0 } }
}

const GLOBAL_STICKERS = []
const LOOKUP = new Map()
for (const face of FACE_ORDER) {
  for (let i = 0; i < 9; i += 1) {
    const sticker = faceToSticker(face, i)
    GLOBAL_STICKERS.push(sticker)
    LOOKUP.set(keyFor(sticker), toGlobal(face, i))
  }
}

// Quarter-turn rotation in right-handed 3D space.
function rotateCoord(v, axis, turns) {
  const t = ((turns % 4) + 4) % 4
  if (t === 0) return { ...v }

  let out = { ...v }
  for (let i = 0; i < t; i += 1) {
    if (axis === 'x') out = { x: out.x, y: -out.z, z: out.y }
    if (axis === 'y') out = { x: out.z, y: out.y, z: -out.x }
    if (axis === 'z') out = { x: -out.y, y: out.x, z: out.z }
  }
  return out
}

const MOVE_CONFIG = {
  U: { axis: 'y', layer: 1, cwTurns: 3 },
  D: { axis: 'y', layer: -1, cwTurns: 1 },
  R: { axis: 'x', layer: 1, cwTurns: 3 },
  L: { axis: 'x', layer: -1, cwTurns: 1 },
  F: { axis: 'z', layer: 1, cwTurns: 3 },
  B: { axis: 'z', layer: -1, cwTurns: 1 }
}

function layerValue(pos, axis) {
  if (axis === 'x') return pos.x
  if (axis === 'y') return pos.y
  return pos.z
}

// Apply one clockwise quarter turn for a face token (U, R, F, ...).
function applyQuarterMoveString(cubeString, face) {
  const config = MOVE_CONFIG[face]
  if (!config) return cubeString

  const chars = cubeString.split('')
  const out = [...chars]

  for (let from = 0; from < 54; from += 1) {
    const sticker = GLOBAL_STICKERS[from]
    if (layerValue(sticker.pos, config.axis) !== config.layer) {
      out[from] = chars[from]
      continue
    }

    const rotated = {
      pos: rotateCoord(sticker.pos, config.axis, config.cwTurns),
      normal: rotateCoord(sticker.normal, config.axis, config.cwTurns)
    }

    const to = LOOKUP.get(keyFor(rotated))
    out[to] = chars[from]
  }

  return out.join('')
}

export function applyMoveToCubeString(cubeString, move) {
  if (!move || !move.trim()) return cubeString
  const token = move.trim()
  const face = token[0]
  let turns = 1
  if (token.endsWith("'")) turns = 3
  if (token.endsWith('2')) turns = 2

  let next = cubeString
  for (let i = 0; i < turns; i += 1) {
    next = applyQuarterMoveString(next, face)
  }
  return next
}

export function applyMovesToState(state, notation) {
  const tokens = notation
    .trim()
    .split(/\s+/)
    .filter(Boolean)

  let cubeString = FACE_ORDER.map((face) => state[face].join('')).join('')
  for (const token of tokens) {
    cubeString = applyMoveToCubeString(cubeString, token)
  }

  return {
    U: cubeString.slice(0, 9).split(''),
    R: cubeString.slice(9, 18).split(''),
    F: cubeString.slice(18, 27).split(''),
    D: cubeString.slice(27, 36).split(''),
    L: cubeString.slice(36, 45).split(''),
    B: cubeString.slice(45, 54).split('')
  }
}

export function applySingleMove(state, move) {
  const cloned = cloneCubeState(state)
  return applyMovesToState(cloned, move)
}

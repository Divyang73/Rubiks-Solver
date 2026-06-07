from __future__ import annotations

import random
from dataclasses import dataclass

import pycuber as pc

SOLVED_CUBE_STATE = "WWWWWWWWWRRRRRRRRRBBBBBBBBBYYYYYYYYYOOOOOOOOOGGGGGGGGG"

_FACE_ORDER = ["U", "R", "F", "D", "L", "B"]
_COLOR_NAME_TO_CHAR = {
    # PyCuber solved centers are U=yellow, R=orange, F=green, D=white, L=red, B=blue.
    # We remap to project convention: U=W, R=R, F=B, D=Y, L=O, B=G.
    "white": "Y",
    "yellow": "W",
    "red": "O",
    "orange": "R",
    "blue": "G",
    "green": "B",
}
_COLOR_CHAR_TO_FACE_CHAR = {
    "W": "U",
    "R": "R",
    "B": "F",
    "Y": "D",
    "O": "L",
    "G": "B",
}


@dataclass
class ScrambleResult:
    scramble: str
    cube_state: str


def cube_state_to_kociemba(cube_state: str) -> str:
    # Map project color-ordered string into kociemba's face-letter format.
    return "".join(_COLOR_CHAR_TO_FACE_CHAR[ch] for ch in cube_state)


def pycuber_cube_to_state(cube: pc.Cube) -> str:
    # Serialize in fixed U R F D L B order to match frontend/backend contracts.
    out: list[str] = []
    for face in _FACE_ORDER:
        f = cube.get_face(face)
        for row in range(3):
            for col in range(3):
                color_name = f[row][col].colour
                out.append(_COLOR_NAME_TO_CHAR[color_name])
    return "".join(out)


def random_scramble(depth: int = 10, seed: int | None = None) -> ScrambleResult:
    rng = random.Random(seed)
    base_faces = ["R", "L", "U", "D", "F", "B"]
    suffixes = ["", "'", "2"]

    moves: list[str] = []
    last_face: str | None = None

    while len(moves) < depth:
        face = rng.choice(base_faces)
        # Avoid immediate same-face repeats to generate cleaner training scrambles.
        if face == last_face:
            continue
        move = f"{face}{rng.choice(suffixes)}"
        moves.append(move)
        last_face = face

    scramble = " ".join(moves)
    cube = pc.Cube()
    cube(scramble)

    return ScrambleResult(scramble=scramble, cube_state=pycuber_cube_to_state(cube))

from __future__ import annotations

from dataclasses import dataclass

import kociemba

from utils.cube_utils import SOLVED_CUBE_STATE, cube_state_to_kociemba


@dataclass
class ValidationResult:
    valid: bool
    message: str
    errors: list[str]


class CubeValidator:
    ALLOWED_COLORS = set("WYROBG")
    EXPECTED_CENTERS = {
        4: "W",
        13: "R",
        22: "B",
        31: "Y",
        40: "O",
        49: "G",
    }

    @classmethod
    def validate(cls, cube_state: str) -> ValidationResult:
        errors: list[str] = []

        if len(cube_state) != 54:
            errors.append("Invalid cube string length (expected 54)")
            return ValidationResult(False, "Invalid cube configuration", errors)

        if any(ch not in cls.ALLOWED_COLORS for ch in cube_state):
            errors.append("Cube contains invalid colors. Allowed: W,Y,R,O,B,G")

        for color in sorted(cls.ALLOWED_COLORS):
            count = cube_state.count(color)
            if count != 9:
                errors.append(
                    f"Invalid color distribution: {color} appears {count} times (expected 9)"
                )

        for index, expected in cls.EXPECTED_CENTERS.items():
            if cube_state[index] != expected:
                errors.append(
                    f"Invalid center configuration at index {index}: expected {expected}"
                )

        if errors:
            return ValidationResult(False, "Invalid cube configuration", errors)

        # Solvability check through proven cube model constraints in kociemba.
        try:
            kociemba.solve(cube_state_to_kociemba(cube_state))
        except Exception as exc:  # pragma: no cover - library-specific errors
            errors.append(f"Unsolvable configuration: {exc}")
            return ValidationResult(False, "Cube configuration is unsolvable", errors)

        if cube_state == SOLVED_CUBE_STATE:
            return ValidationResult(True, "Cube configuration is valid (already solved)", [])

        return ValidationResult(True, "Cube configuration is valid", [])

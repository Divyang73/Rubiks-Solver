from enum import Enum

from pydantic import BaseModel, Field, field_validator


class AlgorithmChoice(str, Enum):
    BFS = "bfs"
    DFS = "dfs"
    IDDFS = "iddfs"
    IDASTAR = "idastar"


class SolveRequest(BaseModel):
    cube_state: str = Field(
        ...,
        min_length=54,
        max_length=54,
        description="54-character string representing cube state",
    )
    algorithm: AlgorithmChoice = Field(
        default=AlgorithmChoice.IDASTAR,
        description="Algorithm to use for solving",
    )
    include_stats: bool = Field(
        default=True,
        description="Include detailed statistics in response",
    )

    @field_validator("cube_state")
    @classmethod
    def validate_cube_state_chars(cls, value: str) -> str:
        allowed = set("WYROBG")
        if len(value) != 54 or any(ch not in allowed for ch in value):
            raise ValueError("Cube state must be 54 chars from set WYROBG")
        return value


class ValidateRequest(BaseModel):
    cube_state: str = Field(..., min_length=54, max_length=54)

    @field_validator("cube_state")
    @classmethod
    def validate_cube_state_chars(cls, value: str) -> str:
        allowed = set("WYROBG")
        if len(value) != 54 or any(ch not in allowed for ch in value):
            raise ValueError("Cube state must be 54 chars from set WYROBG")
        return value


class ScrambleRequest(BaseModel):
    depth: int = Field(default=10, ge=1, le=30)
    seed: int | None = None


class DifficultyScrambleRequest(BaseModel):
    difficulty: str = Field(..., description="easy, medium, or hard")
    seed: int | None = None

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in {"easy", "medium", "hard"}:
            raise ValueError("difficulty must be one of: easy, medium, hard")
        return normalized

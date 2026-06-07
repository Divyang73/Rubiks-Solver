from typing import Any

from pydantic import BaseModel


class SolveResponse(BaseModel):
    success: bool
    solution: str | None = None
    moves: int | None = None
    algorithm: str | None = None
    time_ms: int | None = None
    statistics: dict[str, Any] | None = None
    error: str | None = None
    details: str | None = None


class ValidateResponse(BaseModel):
    valid: bool
    message: str
    errors: list[str] | None = None


class ScrambleResponse(BaseModel):
    scramble: str
    moves: int
    cube_state: str

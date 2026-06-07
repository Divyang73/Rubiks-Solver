from __future__ import annotations

import asyncio
import json
import logging
import random
from pathlib import Path

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from models.solve_request import (
    AlgorithmChoice,
    DifficultyScrambleRequest,
    ScrambleRequest,
    SolveRequest,
    ValidateRequest,
)
from models.solve_response import ScrambleResponse, SolveResponse, ValidateResponse
from solvers.wrapper import AlgorithmType, CppSolverWrapper
from utils.cube_utils import random_scramble
from utils.cube_validator import CubeValidator

router = APIRouter(prefix="/api", tags=["rubiks-solver"])
SOLVER_EXECUTABLES_DIR = str(Path(__file__).resolve().parents[1] / "solvers" / "cpp_executables")
solver_wrapper = CppSolverWrapper(executables_dir=SOLVER_EXECUTABLES_DIR)
logger = logging.getLogger(__name__)


ALGORITHM_INFO = {
    "bfs": {
        "name": "BFS",
        "full_name": "Breadth-First Search",
        "description": "Finds shortest solution, high memory usage",
        "time_complexity": "O(b^d)",
        "space_complexity": "O(b^d)",
        "optimal": True,
        "typical_moves": "optimal",
        "expected_time": "<= 10s for shallow scrambles",
        "memory_usage": "High",
        "best_for": "<= 7 moves",
    },
    "dfs": {
        "name": "DFS",
        "full_name": "Depth-First Search",
        "description": "Fast exploration, non-optimal in general",
        "time_complexity": "O(b^d)",
        "space_complexity": "O(d)",
        "optimal": False,
        "typical_moves": "variable",
        "expected_time": "fast for first-found solutions",
        "memory_usage": "Low",
        "best_for": "quick demos",
    },
    "iddfs": {
        "name": "IDDFS",
        "full_name": "Iterative Deepening DFS",
        "description": "Optimal like BFS, memory efficient like DFS",
        "time_complexity": "O(b^d)",
        "space_complexity": "O(d)",
        "optimal": True,
        "typical_moves": "optimal",
        "expected_time": "<= 30s medium scrambles",
        "memory_usage": "Low",
        "best_for": "balanced search",
    },
    "idastar": {
        "name": "IDA*",
        "full_name": "Iterative Deepening A*",
        "description": "Heuristic search with strong practical performance",
        "time_complexity": "O(b^d)",
        "space_complexity": "O(d)",
        "optimal": True,
        "typical_moves": "near-optimal / optimal",
        "expected_time": "<= 60s",
        "memory_usage": "Low",
        "best_for": "production use",
    },
}


DIFFICULTY_RANGES = {
    "easy": (3, 4),
    "medium": (6, 8),
    "hard": (9, 10),
}


# ──────────────────────────────────────────────────────
#  REST endpoints (unchanged, backward-compatible)
# ──────────────────────────────────────────────────────


@router.get("/")
def health() -> dict[str, str]:
    return {
        "message": "Rubik's Cube Solver API",
        "version": "1.0.0",
        "status": "operational",
    }


@router.post("/validate", response_model=ValidateResponse)
def validate_cube(request: ValidateRequest) -> ValidateResponse:
    logger.info("validate request received")
    result = CubeValidator.validate(request.cube_state)
    if not result.valid:
        logger.warning("validate failed: %s", result.errors)
    else:
        logger.info("validate succeeded")
    return ValidateResponse(valid=result.valid, message=result.message, errors=result.errors or None)


@router.post("/scramble", response_model=ScrambleResponse)
def generate_scramble(request: ScrambleRequest) -> ScrambleResponse:
    logger.info("scramble request received depth=%s seed=%s", request.depth, request.seed)
    generated = random_scramble(depth=request.depth, seed=request.seed)
    logger.info("scramble generated moves=%s", len(generated.scramble.split()))
    return ScrambleResponse(
        scramble=generated.scramble,
        moves=len(generated.scramble.split()),
        cube_state=generated.cube_state,
    )


@router.post("/scramble/by-difficulty", response_model=ScrambleResponse)
def generate_scramble_by_difficulty(request: DifficultyScrambleRequest) -> ScrambleResponse:
    # Difficulty tiers are randomized within bounded move ranges for quick UX.
    min_depth, max_depth = DIFFICULTY_RANGES[request.difficulty]
    depth = random.randint(min_depth, max_depth)
    logger.info(
        "difficulty scramble request received difficulty=%s selected_depth=%s seed=%s",
        request.difficulty,
        depth,
        request.seed,
    )
    generated = random_scramble(depth=depth, seed=request.seed)
    return ScrambleResponse(
        scramble=generated.scramble,
        moves=len(generated.scramble.split()),
        cube_state=generated.cube_state,
    )


@router.post("/solve", response_model=SolveResponse)
def solve_cube(request: SolveRequest) -> SolveResponse:
    logger.info("solve request algorithm=%s", request.algorithm.value)

    # Keep validation centralized so every solver call gets the same constraints.
    validation = CubeValidator.validate(request.cube_state)
    if not validation.valid:
        logger.warning("solve rejected by validation: %s", validation.errors)
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_CUBE_STATE",
                "message": "Cube configuration is invalid",
                "details": validation.errors,
            },
        )

    result = solver_wrapper.solve(
        request.cube_state,
        algorithm=AlgorithmType(request.algorithm.value),
    )

    # Convert native adapter failures to HTTP semantics expected by frontend.
    if not result.get("success"):
        logger.error("solve failed algorithm=%s error=%s details=%s", request.algorithm.value, result.get("error"), result.get("details"))
        error_msg = (result.get("error") or "Solver failed").lower()
        if "timeout" in error_msg:
            raise HTTPException(status_code=408, detail=result)
        raise HTTPException(status_code=500, detail=result)

    logger.info("solve succeeded algorithm=%s moves=%s backend=%s", request.algorithm.value, result.get("moves"), result.get("solver_backend"))

    stats = None
    if request.include_stats:
        stats = {
            "nodes_explored": result.get("nodes_explored"),
            "memory_mb": result.get("memory_mb"),
            "optimal": request.algorithm in {
                AlgorithmChoice.BFS,
                AlgorithmChoice.IDDFS,
                AlgorithmChoice.IDASTAR,
            },
            "solver_backend": result.get("solver_backend", "cpp"),
        }

    return SolveResponse(
        success=True,
        solution=result.get("solution", ""),
        moves=result.get("moves", 0),
        algorithm=request.algorithm.value,
        time_ms=result.get("time_ms", 0),
        statistics=stats,
    )


@router.get("/algorithms/{algorithm_name}")
def get_algorithm_info(algorithm_name: str) -> dict:
    key = algorithm_name.lower()
    if key not in ALGORITHM_INFO:
        raise HTTPException(status_code=404, detail="Unknown algorithm")
    return ALGORITHM_INFO[key]


# ──────────────────────────────────────────────────────
#  WebSocket endpoint – real-time streaming solve
# ──────────────────────────────────────────────────────
#
# Protocol:
#   1. Client sends JSON: {"cube_state": "...", "algorithm": "idastar"}
#   2. Server streams:
#      {"type": "progress", "message": "...", "data": {...}}
#      {"type": "progress", "message": "...", "data": {...}}
#      ...
#   3. Server sends final:
#      {"type": "result", "success": true, "solution": "...", ...}
#      or
#      {"type": "error", "message": "..."}
#   4. Connection is closed after the result.


# This endpoint lives under /ws/solve (no /api prefix) so we attach it
# directly.  The router prefix is /api so we use a separate mini-router.
ws_router = APIRouter(tags=["rubiks-solver-ws"])


@ws_router.websocket("/ws/solve")
async def ws_solve(websocket: WebSocket):
    await websocket.accept()
    solve_task: asyncio.Task | None = None

    try:
        # 1. Receive the solve request from the client.
        raw = await websocket.receive_text()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            await websocket.send_json({"type": "error", "message": "Invalid JSON"})
            await websocket.close()
            return

        cube_state = payload.get("cube_state", "")
        algorithm_str = payload.get("algorithm", "idastar")

        # Validate algorithm choice.
        try:
            algorithm = AlgorithmType(algorithm_str)
        except ValueError:
            await websocket.send_json({
                "type": "error",
                "message": f"Unknown algorithm: {algorithm_str}",
            })
            await websocket.close()
            return

        # 2. Validate cube state.
        validation = CubeValidator.validate(cube_state)
        if not validation.valid:
            await websocket.send_json({
                "type": "error",
                "message": validation.message,
                "errors": validation.errors,
            })
            await websocket.close()
            return

        # 3. Stream the solve.
        logger.info("ws_solve: starting algorithm=%s", algorithm.value)

        async def _run_solve():
            async for msg in solver_wrapper.solve_streaming(cube_state, algorithm):
                await websocket.send_json(msg)

        solve_task = asyncio.create_task(_run_solve())
        await solve_task

        logger.info("ws_solve: completed algorithm=%s", algorithm.value)

    except WebSocketDisconnect:
        # ─── CRITICAL: client disconnected mid-solve ───
        # Cancel the solve task which will trigger CancelledError inside
        # solve_streaming, which in turn calls proc.kill() on the C++ process.
        logger.warning("ws_solve: client disconnected, cleaning up subprocess")
        if solve_task and not solve_task.done():
            solve_task.cancel()
            try:
                await solve_task
            except asyncio.CancelledError:
                pass

    except Exception as exc:
        logger.exception("ws_solve: unexpected error: %s", exc)
        if solve_task and not solve_task.done():
            solve_task.cancel()
            try:
                await solve_task
            except asyncio.CancelledError:
                pass
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
        except Exception:
            pass

    finally:
        try:
            await websocket.close()
        except Exception:
            pass

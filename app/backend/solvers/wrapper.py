from __future__ import annotations

import asyncio
import os
import re
import subprocess
import tempfile
from enum import Enum
from typing import Any, AsyncGenerator

from utils.cube_utils import SOLVED_CUBE_STATE


class AlgorithmType(str, Enum):
    BFS = "bfs"
    DFS = "dfs"
    IDDFS = "iddfs"
    IDASTAR = "idastar"


DEFAULT_TIMEOUTS = {
    AlgorithmType.BFS: 120,
    AlgorithmType.DFS: 120,
    AlgorithmType.IDDFS: 120,
    AlgorithmType.IDASTAR: 120,
}


class CppSolverWrapper:
    """Wrapper for C++ Rubik's Cube solvers."""

    def __init__(self, executables_dir: str):
        self.executables_dir = executables_dir
        self.solvers = {
            AlgorithmType.BFS: os.path.join(executables_dir, "bfs_solver"),
            AlgorithmType.DFS: os.path.join(executables_dir, "dfs_solver"),
            AlgorithmType.IDDFS: os.path.join(executables_dir, "iddfs_solver"),
            AlgorithmType.IDASTAR: os.path.join(executables_dir, "idastar_solver"),
        }

    # ------------------------------------------------------------------
    # Synchronous solve – kept for backward-compatible REST endpoint
    # ------------------------------------------------------------------

    def solve(
        self,
        cube_state: str,
        algorithm: AlgorithmType,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        timeout = timeout or DEFAULT_TIMEOUTS[algorithm]

        # Fast path avoids spawning a native process for already solved cubes.
        if cube_state == SOLVED_CUBE_STATE:
            return {
                "success": True,
                "solution": "",
                "moves": 0,
                "time_ms": 0,
                "nodes_explored": 0,
                "algorithm": algorithm.value,
                "solver_backend": "cpp-korf-repo",
            }

        solver_path = self.solvers[algorithm]
        if not (os.path.exists(solver_path) and os.access(solver_path, os.X_OK)):
            return {
                "success": False,
                "error": (
                    f"C++ solver executable not found or not executable: {solver_path}. "
                    "Build solvers via app/backend/solvers/build_cpp_solvers.sh"
                ),
            }

        return self._run_cpp_solver(solver_path, cube_state, algorithm, timeout)

    def _run_cpp_solver(
        self, solver_path: str, cube_state: str, algorithm: AlgorithmType, timeout: int
    ) -> dict[str, Any]:
        # Adapters read cube input from a file path, so write a temp file per request.
        with tempfile.NamedTemporaryFile("w", delete=False) as fp:
            fp.write(cube_state)
            input_file = fp.name

        try:
            extra_args: list[str] = []
            if algorithm == AlgorithmType.DFS:
                extra_args = ["20"]
            elif algorithm == AlgorithmType.IDDFS:
                extra_args = ["20"]

            result = subprocess.run(
                [solver_path, input_file, *extra_args],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                return {"success": False, "error": result.stderr.strip() or "C++ solver failed"}
            return self._parse_cpp_output(result.stdout, algorithm)
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Solver timed out after {timeout} seconds",
            }
        finally:
            try:
                os.remove(input_file)
            except OSError:
                pass

    # ------------------------------------------------------------------
    # Async streaming solve – used by the WebSocket endpoint
    # ------------------------------------------------------------------

    async def solve_streaming(
        self,
        cube_state: str,
        algorithm: AlgorithmType,
        timeout: int | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Async generator that yields progress dicts then a final result dict.

        Each yielded dict has a ``"type"`` key:
        - ``"progress"`` – an intermediate progress update from the solver
        - ``"result"``   – the final solve result (success or failure)

        The caller is responsible for catching ``asyncio.CancelledError`` and
        terminating the subprocess (see the WebSocket handler).
        """
        timeout = timeout or DEFAULT_TIMEOUTS[algorithm]

        # Fast path.
        if cube_state == SOLVED_CUBE_STATE:
            yield {
                "type": "result",
                "success": True,
                "solution": "",
                "moves": 0,
                "time_ms": 0,
                "nodes_explored": 0,
                "algorithm": algorithm.value,
                "solver_backend": "cpp-korf-repo",
            }
            return

        solver_path = self.solvers[algorithm]
        if not (os.path.exists(solver_path) and os.access(solver_path, os.X_OK)):
            yield {
                "type": "result",
                "success": False,
                "error": (
                    f"C++ solver executable not found or not executable: {solver_path}. "
                    "Build solvers via app/backend/solvers/build_cpp_solvers.sh"
                ),
            }
            return

        # Write temp input file.
        with tempfile.NamedTemporaryFile("w", delete=False) as fp:
            fp.write(cube_state)
            input_file = fp.name

        extra_args: list[str] = []
        if algorithm == AlgorithmType.DFS:
            extra_args = ["20"]
        elif algorithm == AlgorithmType.IDDFS:
            extra_args = ["20"]

        proc: asyncio.subprocess.Process | None = None
        try:
            proc = await asyncio.create_subprocess_exec(
                solver_path, input_file, *extra_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Read stderr line-by-line for PROGRESS messages.
            assert proc.stderr is not None
            assert proc.stdout is not None
            
            last_error_line = ""

            start_time = asyncio.get_running_loop().time()
            while True:
                remaining = timeout - (asyncio.get_running_loop().time() - start_time)
                if remaining <= 0:
                    raise asyncio.TimeoutError()
                
                try:
                    # Read the next progress line with a timeout
                    line_coro = proc.stderr.readline()  # type: ignore[union-attr]
                    line = await asyncio.wait_for(line_coro, timeout=remaining)
                    if not line:
                        break
                    text = line.decode().strip()
                    if text.startswith("PROGRESS:"):
                        yield {"type": "progress", **_parse_progress_line(text)}
                    elif text:
                        last_error_line = text
                except asyncio.TimeoutError:
                    raise

            # Process finished emitting stderr, now collect stdout
            remaining = timeout - (asyncio.get_running_loop().time() - start_time)
            if remaining <= 0:
                raise asyncio.TimeoutError()
            
            stdout_bytes, _ = await asyncio.wait_for(proc.communicate(), timeout=remaining)
            stdout_text = stdout_bytes.decode() if stdout_bytes else ""

            if proc.returncode != 0:
                yield {
                    "type": "result",
                    "success": False,
                    "error": f"C++ solver failed: {last_error_line}",
                }
                return

            parsed = self._parse_cpp_output(stdout_text, algorithm)
            yield {"type": "result", **parsed}

        except asyncio.TimeoutError:
            if proc and proc.returncode is None:
                proc.kill()
                await proc.wait()
            yield {
                "type": "result",
                "success": False,
                "error": f"Solver timed out after {timeout} seconds",
            }

        except (asyncio.CancelledError, Exception) as exc:
            # Kill the subprocess if the task is cancelled (e.g. WebSocket disconnect)
            # or if any other exception occurs. This prevents zombie C++ processes.
            if proc and proc.returncode is None:
                proc.kill()
                await proc.wait()
            if isinstance(exc, asyncio.CancelledError):
                raise  # re-raise so caller knows it was cancelled
            yield {
                "type": "result",
                "success": False,
                "error": str(exc),
            }

        finally:
            try:
                os.remove(input_file)
            except OSError:
                pass

    # ------------------------------------------------------------------
    # Output parsing helpers
    # ------------------------------------------------------------------

    def _parse_cpp_output(self, output: str, algorithm: AlgorithmType) -> dict[str, Any]:
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        if not lines:
            return {"success": False, "error": "Empty solver output"}

        # Adapter contract: line 1 = move sequence, later lines include metadata.
        solution = lines[0]
        moves = len(solution.split()) if solution else 0
        time_ms = self._extract_int(lines, r"time\s*:\s*(\d+)")
        nodes = self._extract_int(lines, r"nodes\s*:\s*(\d+)")

        return {
            "success": True,
            "solution": solution,
            "moves": moves,
            "time_ms": time_ms,
            "nodes_explored": nodes,
            "algorithm": algorithm.value,
            "solver_backend": "cpp-korf-repo",
        }

    @staticmethod
    def _extract_int(lines: list[str], pattern: str) -> int:
        regex = re.compile(pattern, re.IGNORECASE)
        for line in lines:
            match = regex.search(line)
            if match:
                return int(match.group(1))
        return 0


def _parse_progress_line(text: str) -> dict[str, Any]:
    """Parse a ``PROGRESS: key=value key=value ...`` line from stderr."""
    # Remove the "PROGRESS:" prefix.
    body = text[len("PROGRESS:"):].strip()
    data: dict[str, Any] = {}
    parts = body.split()
    descriptions: list[str] = []
    for part in parts:
        if "=" in part:
            key, _, val = part.partition("=")
            # Try to convert numeric values.
            cleaned = val.rstrip("ms")
            try:
                data[key] = int(cleaned)
            except ValueError:
                data[key] = val
        else:
            descriptions.append(part)

    # Build a human-readable message from the data.
    if "iteration" in data and "bound" in data:
        msg = f"IDA* iteration {data['iteration']}, cost bound = {data['bound']}"
    elif "depth" in data:
        msg = f"Searching depth {data['depth']}"
        if "max_depth" in data:
            msg += f" / {data['max_depth']}"
    elif "nodes" in data:
        msg = f"Explored {data['nodes']:,} nodes"
        if "queue" in data:
            msg += f", queue size {data['queue']:,}"
    elif "searching" in data or descriptions:
        msg = "Solver searching..."
    else:
        msg = body

    if "elapsed" in data:
        msg += f" ({data['elapsed']}ms)"

    return {"message": msg, "data": data}

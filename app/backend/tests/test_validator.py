from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.cube_validator import CubeValidator


def test_valid_solved_cube() -> None:
    solved = "WWWWWWWWWRRRRRRRRRBBBBBBBBBYYYYYYYYYOOOOOOOOOGGGGGGGGG"
    result = CubeValidator.validate(solved)
    assert result.valid


def test_invalid_color_count() -> None:
    invalid = "W" * 54
    result = CubeValidator.validate(invalid)
    assert not result.valid

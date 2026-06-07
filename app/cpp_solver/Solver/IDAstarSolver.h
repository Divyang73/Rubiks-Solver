#ifndef IDASTARSOLVER_H
#define IDASTARSOLVER_H

#include <cassert>
#include <climits>
#include <cstdint>
#include <string>
#include <vector>

#include "../Model/RubiksCube.h"
#include "../PatternDatabases/CornerPatternDatabase.h"

// True IDA* (Korf 1985): iterative-deepening depth-first search with an
// admissible heuristic cost bound.  No visited map, no priority queue.
// Memory usage is O(d) where d is the solution depth.
template<typename T, typename H>
class IDAstarSolver {
private:
    CornerPatternDatabase cornerDB;
    std::vector<RubiksCube::MOVE> path;

    static const int FOUND = -1;
    // Sentinel meaning "no face was last" so all 6 faces are allowed at root.
    static const int NO_FACE = -1;

    // DFS with f-cost bound.
    // Applies moves directly to `cube` (passed by reference from solve()).
    // Undoes each move before returning unless the solution was found.
    // Returns FOUND if goal reached, otherwise the minimum f-cost that exceeded the bound.
    //
    // lastFace: face index (MOVE index / 3) of the previous move, or NO_FACE at root.
    // Skipping same-face consecutive moves is correct because any sequence of moves
    // on a single face reduces to at most one move.
    int search(T& cube, int g, int bound, int lastFace) {
        int h = static_cast<int>(cornerDB.getNumMoves(cube));
        int f = g + h;
        if (f > bound) return f;
        if (cube.isSolved()) return FOUND;

        int minExceeded = INT_MAX;
        for (int i = 0; i < 18; i++) {
            int thisFace = i / 3;
            if (thisFace == lastFace) continue;

            RubiksCube::MOVE curr = RubiksCube::MOVE(i);
            cube.move(curr);
            path.push_back(curr);

            int result = search(cube, g + 1, bound, thisFace);

            if (result == FOUND) return FOUND;
            if (result < minExceeded) minExceeded = result;

            path.pop_back();
            cube.invert(curr);
        }
        return minExceeded;
    }

public:
    T rubiksCube;

    IDAstarSolver(const T& _rubiksCube, const std::string& fileName) : rubiksCube(_rubiksCube) {
        cornerDB.fromFile(fileName);
    }

    // Returns the sequence of moves that solves the cube.
    // After solve() returns, rubiksCube holds the solved state.
    std::vector<RubiksCube::MOVE> solve() {
        int bound = static_cast<int>(cornerDB.getNumMoves(rubiksCube));
        path.clear();

        while (true) {
            int result = search(rubiksCube, 0, bound, NO_FACE);
            if (result == FOUND) {
                assert(rubiksCube.isSolved());
                return path;
            }
            if (result == INT_MAX) {
                // No solution reachable -- should not happen for a valid cube state.
                return {};
            }
            bound = result;
        }
    }
};

#endif // IDASTARSOLVER_H

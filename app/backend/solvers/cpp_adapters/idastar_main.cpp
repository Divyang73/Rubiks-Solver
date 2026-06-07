#include <chrono>
#include <climits>
#include <filesystem>
#include <iostream>

#include "common_solver_adapter.hpp"
#include "../../../cpp_solver/PatternDatabases/NibbleArray.cpp"
#include "../../../cpp_solver/PatternDatabases/PatternDatabase.cpp"
#include "../../../cpp_solver/PatternDatabases/CornerPatternDatabase.cpp"
#include "../../../cpp_solver/PatternDatabases/math.cpp"
#include "../../../cpp_solver/PatternDatabases/CornerPatternDatabase.h"
#include "../../../cpp_solver/Model/RubiksCube.h"

// ---------------------------------------------------------------------------
// Streaming IDA* solver – identical algorithm to IDAstarSolver.h but prints
// PROGRESS lines to stderr at each depth-bound iteration so the Python
// wrapper can stream them to the frontend via WebSocket.
// ---------------------------------------------------------------------------

static const int FOUND = -1;
static const int NO_FACE = -1;

static CornerPatternDatabase cornerDB;
static std::vector<RubiksCube::MOVE> path;
static long long nodesExplored = 0;

static int search(RubiksCube3dArray& cube, int g, int bound, int lastFace) {
    nodesExplored++;
    int h = static_cast<int>(cornerDB.getNumMoves(cube));
    // CRITICAL FIX: The provided cornerDepth5V1.txt is only computed up to depth 5.
    // Unvisited states return 15 (0x0F). 15 is INADMISSIBLE for states 6-14 moves away,
    // which breaks A* and forces a massive, warped search tree.
    // Since we know unvisited states are >5 moves away, the max admissible value is 6.
    if (h == 15) h = 6;

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

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: idastar_solver <input_file> [corner_db_path]\n";
        return 2;
    }

    try {
        const std::string state = readStateFromInputFile(argv[1]);
        RubiksCube3dArray cube = cubeFromProjectState(state);

        std::string dbPath;
        if (argc >= 3) {
            dbPath = argv[2];
        } else {
            const auto exePath = std::filesystem::absolute(argv[0]);
            dbPath = (exePath.parent_path() / "Database" / "cornerDepth5V1.txt").string();
        }

        // Load pattern database.
        cornerDB.fromFile(dbPath);

        auto started = std::chrono::high_resolution_clock::now();
        int bound = static_cast<int>(cornerDB.getNumMoves(cube));
        if (bound == 15) bound = 6;
        
        path.clear();
        int iteration = 0;

        while (true) {
            iteration++;
            // --- PROGRESS REPORTING (stderr) ---
            auto now = std::chrono::high_resolution_clock::now();
            auto elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(now - started).count();
            std::cerr << "PROGRESS: iteration=" << iteration
                      << " bound=" << bound
                      << " elapsed=" << elapsedMs << "ms"
                      << std::endl;

            int result = search(cube, 0, bound, NO_FACE);

            if (result == FOUND) {
                break;
            }
            if (result == INT_MAX) {
                // No solution reachable.
                path.clear();
                break;
            }
            bound = result;
        }

        auto ended = std::chrono::high_resolution_clock::now();
        const auto elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(ended - started).count();

        std::cout << movesToString(path) << "\n";
        std::cout << "Moves: " << path.size() << "\n";
        std::cout << "Time: " << elapsedMs << "ms\n";
        std::cout << "Nodes: " << nodesExplored << "\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << ex.what() << "\n";
        return 1;
    }
}

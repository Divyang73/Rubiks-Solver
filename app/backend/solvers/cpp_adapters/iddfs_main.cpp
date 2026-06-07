#include <chrono>
#include <iostream>

#include "common_solver_adapter.hpp"
#include "../../../cpp_solver/Solver/DFSSolver.h"

// ---------------------------------------------------------------------------
// Streaming IDDFS adapter – replicates the IDDFS loop manually so we can
// emit PROGRESS lines to stderr at each depth iteration.
// ---------------------------------------------------------------------------

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: iddfs_solver <input_file> [max_depth]\n";
        return 2;
    }

    int maxDepth = 20;
    if (argc >= 3) {
        maxDepth = std::max(1, std::stoi(argv[2]));
    }

    try {
        const std::string state = readStateFromInputFile(argv[1]);
        RubiksCube3dArray cube = cubeFromProjectState(state);

        auto started = std::chrono::high_resolution_clock::now();
        std::vector<RubiksCube::MOVE> moves;
        bool solved = false;
        long long totalNodes = 0;

        for (int depth = 1; depth <= maxDepth; depth++) {
            // --- PROGRESS REPORTING (stderr) ---
            auto now = std::chrono::high_resolution_clock::now();
            auto elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(now - started).count();
            std::cerr << "PROGRESS: depth=" << depth
                      << " max_depth=" << maxDepth
                      << " elapsed=" << elapsedMs << "ms"
                      << std::endl;

            DFSSolver<RubiksCube3dArray, Hash3d> dfsSolver(cube, depth);
            moves = dfsSolver.solve();
            totalNodes += dfsSolver.nodesExplored;
            
            if (dfsSolver.rubiksCube.isSolved()) {
                cube = dfsSolver.rubiksCube;
                solved = true;
                break;
            }
        }

        auto ended = std::chrono::high_resolution_clock::now();
        const auto elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(ended - started).count();

        if (solved) {
            std::cout << movesToString(moves) << "\n";
        } else {
            std::cout << "\n";
        }
        std::cout << "Moves: " << moves.size() << "\n";
        std::cout << "Time: " << elapsedMs << "ms\n";
        std::cout << "Nodes: " << totalNodes << "\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << ex.what() << "\n";
        return 1;
    }
}

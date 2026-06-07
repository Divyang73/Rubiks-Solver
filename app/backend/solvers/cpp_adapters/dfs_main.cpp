#include <chrono>
#include <iostream>

#include "common_solver_adapter.hpp"
#include "../../../cpp_solver/Solver/DFSSolver.h"

// ---------------------------------------------------------------------------
// Streaming DFS adapter – DFS has no natural depth iterations to report, so
// we emit a single "searching" progress line before launching the solver.
// The DFS solver library does not expose callbacks, so we cannot inject
// progress mid-search without modifying the upstream header.
// ---------------------------------------------------------------------------

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: dfs_solver <input_file> [max_depth]\n";
        return 2;
    }

    int maxDepth = 20;
    if (argc >= 3) {
        maxDepth = std::max(1, std::stoi(argv[2]));
    }

    try {
        const std::string state = readStateFromInputFile(argv[1]);
        RubiksCube3dArray cube = cubeFromProjectState(state);

        // --- PROGRESS REPORTING (stderr) ---
        std::cerr << "PROGRESS: searching max_depth=" << maxDepth
                  << " elapsed=0ms" << std::endl;

        auto started = std::chrono::high_resolution_clock::now();
        DFSSolver<RubiksCube3dArray, Hash3d> solver(cube, maxDepth);
        auto moves = solver.solve();
        auto ended = std::chrono::high_resolution_clock::now();

        const auto elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(ended - started).count();

        std::cout << movesToString(moves) << "\n";
        std::cout << "Moves: " << moves.size() << "\n";
        std::cout << "Time: " << elapsedMs << "ms\n";
        std::cout << "Nodes: " << solver.nodesExplored << "\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << ex.what() << "\n";
        return 1;
    }
}

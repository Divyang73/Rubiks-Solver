#include <chrono>
#include <iostream>
#include <queue>
#include <unordered_map>
#include <algorithm>
#include <cassert>

#include "common_solver_adapter.hpp"

// ---------------------------------------------------------------------------
// Streaming BFS adapter – since BFS does not have depth iterations, we emit
// timer-based PROGRESS lines to stderr every ~2 seconds.
// ---------------------------------------------------------------------------

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: bfs_solver <input_file>\n";
        return 2;
    }

    try {
        const std::string state = readStateFromInputFile(argv[1]);
        RubiksCube3dArray cube = cubeFromProjectState(state);

        auto started = std::chrono::high_resolution_clock::now();
        auto lastProgress = started;
        long long nodesExplored = 0;

        // Inline BFS with progress reporting.
        std::queue<RubiksCube3dArray> q;
        std::unordered_map<RubiksCube3dArray, bool, Hash3d> visited;
        std::unordered_map<RubiksCube3dArray, RubiksCube::MOVE, Hash3d> move_done;

        q.push(cube);
        visited[cube] = true;

        RubiksCube3dArray solvedCube = cube;
        bool solved = false;

        while (!q.empty()) {
            RubiksCube3dArray node = q.front();
            q.pop();
            nodesExplored++;

            // --- PROGRESS REPORTING (stderr) every ~2 seconds ---
            auto now = std::chrono::high_resolution_clock::now();
            auto sinceLast = std::chrono::duration_cast<std::chrono::milliseconds>(now - lastProgress).count();
            if (sinceLast >= 2000) {
                auto totalElapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - started).count();
                std::cerr << "PROGRESS: nodes=" << nodesExplored
                          << " queue=" << q.size()
                          << " elapsed=" << totalElapsed << "ms"
                          << std::endl;
                lastProgress = now;
            }

            if (node.isSolved()) {
                solvedCube = node;
                solved = true;
                break;
            }

            for (int i = 0; i < 18; i++) {
                auto curr_move = RubiksCube::MOVE(i);
                node.move(curr_move);
                if (!visited[node]) {
                    visited[node] = true;
                    move_done[node] = curr_move;
                    q.push(node);
                }
                node.invert(curr_move);
            }
        }

        std::vector<RubiksCube::MOVE> moves;
        if (solved) {
            RubiksCube3dArray curr = solvedCube;
            while (!(curr == cube)) {
                RubiksCube::MOVE curr_move = move_done[curr];
                moves.push_back(curr_move);
                curr.invert(curr_move);
            }
            std::reverse(moves.begin(), moves.end());
        }

        auto ended = std::chrono::high_resolution_clock::now();
        const auto elapsedMs = std::chrono::duration_cast<std::chrono::milliseconds>(ended - started).count();

        std::cout << movesToString(moves) << "\n";
        std::cout << "Moves: " << moves.size() << "\n";
        std::cout << "Time: " << elapsedMs << "ms\n";
        std::cout << "Nodes: " << nodesExplored << "\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << ex.what() << "\n";
        return 1;
    }
}

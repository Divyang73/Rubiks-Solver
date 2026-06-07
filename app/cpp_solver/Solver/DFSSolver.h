#include <cstdint>
#include <string>
#include <vector>
#include <map>
#include "../Model/RubiksCube.h"
#ifndef DFSSOLVER_H
#define DFSSOLVER_H
// Typename T: RubiksCube Representation used (3d, 1d, Bitboard)
// Typename H: Corresponding Hash function

template<typename T, typename H>
class DFSSolver {
private:

    std::vector<RubiksCube::MOVE> moves;
    int max_search_depth;

    //    DFS code to find the solution (helper function)
    bool dfs(int dep) {
        nodesExplored++;
        if (rubiksCube.isSolved()) return true;
        if (dep > max_search_depth) return false;
        for (int i = 0; i < 18; i++) {
            rubiksCube.move(RubiksCube::MOVE(i));
            moves.push_back(RubiksCube::MOVE(i));
            if (dfs(dep + 1)) return true;
            moves.pop_back();
            rubiksCube.invert(RubiksCube::MOVE(i));
        }
        return false;
    }

public:
    T rubiksCube;
    long long nodesExplored = 0;

    DFSSolver(T _rubiksCube, int _max_search_depth = 8) {
        rubiksCube = _rubiksCube;
        max_search_depth = _max_search_depth;
        nodesExplored = 0;
    }

    std::vector<RubiksCube::MOVE> solve() {
        dfs(1);
        return moves;
    }

};


#endif //DFSSOLVER_H

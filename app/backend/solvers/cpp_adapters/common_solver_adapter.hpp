#ifndef COMMON_SOLVER_ADAPTER_HPP
#define COMMON_SOLVER_ADAPTER_HPP

#include <chrono>
#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include "../../../cpp_solver/Model/RubiksCube.cpp"
#include "../../../cpp_solver/Model/RubiksCube3dArray.cpp"

inline char mapProjectColorToModelColor(char c) {
    // Project colors use U=W, R=R, F=B, D=Y, L=O, B=G.
    // Upstream model expects U=W, R=B, F=R, D=Y, L=G, B=O.
    switch (c) {
        case 'W': return 'W';
        case 'Y': return 'Y';
        case 'R': return 'B';
        case 'B': return 'R';
        case 'O': return 'G';
        case 'G': return 'O';
        default: throw std::runtime_error("Invalid sticker color");
    }
}

inline RubiksCube3dArray cubeFromProjectState(const std::string& state) {
    if (state.size() != 54) {
        throw std::runtime_error("Cube state must be 54 characters");
    }

    RubiksCube3dArray cube;

    auto setFace = [&](int modelFace, int startIdx) {
        for (int i = 0; i < 9; i++) {
            int row = i / 3;
            int col = i % 3;
            cube.cube[modelFace][row][col] = mapProjectColorToModelColor(state[startIdx + i]);
        }
    };

    // Project state order: U R F D L B
    // Model face indices: U=0, L=1, F=2, R=3, B=4, D=5
    setFace(0, 0);   // U
    setFace(3, 9);   // R
    setFace(2, 18);  // F
    setFace(5, 27);  // D
    setFace(1, 36);  // L
    setFace(4, 45);  // B

    return cube;
}

inline std::string readStateFromInputFile(const char* inputFilePath) {
    std::ifstream in(inputFilePath);
    if (!in.is_open()) {
        throw std::runtime_error("Unable to open input file");
    }

    std::string state;
    in >> state;
    return state;
}

inline std::string movesToString(const std::vector<RubiksCube::MOVE>& moves) {
    std::string out;
    for (size_t i = 0; i < moves.size(); i++) {
        if (i > 0) out += " ";
        out += RubiksCube::getMove(moves[i]);
    }
    return out;
}

#endif

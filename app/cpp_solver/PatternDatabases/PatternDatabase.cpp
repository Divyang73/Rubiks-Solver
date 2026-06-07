#include "PatternDatabase.h"

PatternDatabase::PatternDatabase(const size_t size) :
        database(size, 0xFF), size(size), numItems(0) {
}

PatternDatabase::PatternDatabase(const size_t size, uint8_t init_val) :
        database(size, init_val), size(size), numItems(0) {
}

// If the index is already set, it does nothing and returns false
// Else it sets ind and returns true

bool PatternDatabase::setNumMoves(const uint32_t ind, const uint8_t numMoves) {
    uint8_t oldMoves = this->getNumMoves(ind);

//    New item is getting added
    if(oldMoves == 0xF){
        ++this->numItems;
    }

    if(oldMoves > numMoves){
        this->database.set(ind, numMoves);
        return true;
    }
    return false;

}

bool PatternDatabase::setNumMoves(const RubiksCube &cube, const uint8_t numMoves) {
    return this->setNumMoves(this->getDatabaseIndex(cube), numMoves);
}

uint8_t PatternDatabase::getNumMoves(const uint32_t ind) const {
    return this->database.get(ind);
}

uint8_t PatternDatabase::getNumMoves(const RubiksCube &cube) const {
    return this->getNumMoves(this->getDatabaseIndex(cube));
}

size_t PatternDatabase::getSize() const {
    return this->size;
}

size_t PatternDatabase::getNumItems() const {
    return this->numItems;
}

bool PatternDatabase::isFull() const {
    return this->numItems == this->size;
}

void PatternDatabase::toFile(const std::string &filePath) const {

    std::ofstream writer(filePath, std::ios::out | std::ios::binary | std::ios::trunc);

    if(!writer.is_open())
        throw "Failed to open the file to write";

    writer.write(
            reinterpret_cast<const char*>(this->database.data()),
            this->database.storageSize()
            );

    writer.close();
}

// Returns true of database is loaded successfully
// else return false

bool PatternDatabase::fromFile(const std::string &filePath) {
    std::ifstream reader(filePath, std::ios::in | std::ios::ate);

    if(!reader.is_open())
        return false;

    size_t fileSize = reader.tellg();

    if(fileSize != this->database.storageSize()){
        reader.close();
        throw "Database corrupt! Failed to open Reader";
    }

    reader.seekg(0, std::ios::beg);
    reader.read(
            reinterpret_cast<char*> (this->database.data()),
            this->database.storageSize()
            );
    reader.close();
    this->numItems = this->size;
    return true;
}

std::vector<uint8_t> PatternDatabase::inflate() const {
    std::vector<uint8_t> inflated;
    this->database.inflate(inflated);
    return inflated;
}

void PatternDatabase::reset() {
    if(this->numItems != 0){
        this->database.reset(0xFF);
        this->numItems = 0;
    }
}
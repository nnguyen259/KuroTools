#include "Utilities.h"

std::string read_string(std::vector<uint8_t>& content, uint32_t& addr) {
    uint8_t sz = content[addr];

    std::string res(content.begin() + addr + 1, content.begin() + addr + 1 + sz);
    addr = addr + sz + 1;
    return res;
}

std::string read_null_terminated_string(std::vector<uint8_t>& content, uint32_t& addr) {
    std::vector<uint8_t> bytes = {};
    uint8_t b = content[addr];
    while (b != 0) {

        bytes.push_back(b);
        addr = addr + 1;
        b = content[addr];

    }
    return std::string(bytes.begin(), bytes.end());
}
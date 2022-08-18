
#include <fstream>
#include <algorithm>
#include <iterator>
#include <vector>
#include <crypto++/blowfish.h>
#include <crypto++/modes.h>
#include <crypto++/osrng.h>
#include <crypto++/cryptlib.h>
#include <crypto++/hex.h>
#include <crypto++/filters.h>
#include <crypto++/blowfish.h>
#include <crypto++/secblock.h>
#include <zstd.h>
#include "Utilities.h"
#include <unordered_set>

static std::vector<uint8_t>  key{ 0x16, 0x4B, 0x7D, 0x0F, 0x4F, 0xA7, 0x4C, 0xAC, 0xD3, 0x7A, 0x06, 0xD9, 0xF8, 0x6D, 0x20, 0x94 };
static std::vector<uint8_t>  IV{ 0x9D, 0x8F, 0x9D, 0xA1, 0x49, 0x60, 0xCC, 0x4C};


void decrypt(std::string filepath);

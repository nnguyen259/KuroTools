#include "CLEDecrypt.h"

void decrypt(std::string filepath)
{

	std::ifstream stream(filepath, std::ios::in | std::ios::binary);
	std::vector<uint8_t> ciphertext((std::istreambuf_iterator<char>(stream)), std::istreambuf_iterator<char>());

	uint32_t length = ciphertext.size();
	std::unordered_set<uint32_t> to_decrypt = { 0x41423943, 0x41423946 };
	std::unordered_set<uint32_t> to_decompress = { 0x41423944 };

	unsigned int current_addr = 0;
	size_t magic = read_data<size_t>(ciphertext, current_addr);
	size_t size = read_data<size_t>(ciphertext, current_addr);
	bool decrypt_ = (to_decrypt.count(magic) > 0);
	bool decomp = (to_decompress.count(magic) > 0);

	if (!((decrypt_) || (decomp))) //if we don't need to decrypt it, or to decompress it, the file is already fine
	{
		stream.close();

	}
	else {
		std::vector<char> plaintext = {};
		while ((decrypt_) || (decomp)) {
			ciphertext.erase(ciphertext.begin(), ciphertext.begin() + 8);
			if (decrypt_) {
				CryptoPP::CTR_Mode< CryptoPP::Blowfish >::Decryption d;
				d.SetKeyWithIV(key.data(), key.size(), IV.data(), IV.size());
				plaintext.resize(ciphertext.size());
				d.ProcessData(reinterpret_cast<unsigned char*>(plaintext.data()), ciphertext.data(), plaintext.size());

			}
			else {
				unsigned long long sz = ZSTD_getDecompressedSize((const void*)ciphertext.data(), ciphertext.size());
				plaintext.resize(sz);
				size_t const ret = ZSTD_decompress(plaintext.data(), plaintext.size(), ciphertext.data(), ciphertext.size());


			}

			ciphertext.assign(plaintext.begin(), plaintext.end());

			current_addr = 0;
			magic = read_data<size_t>(ciphertext, current_addr);
			size = read_data<size_t>(ciphertext, current_addr);
			decrypt_ = (to_decrypt.count(magic) > 0);
			decomp = (to_decompress.count(magic) > 0);

		}


		stream.close();
		std::ofstream out(filepath, std::ios::binary);
		out.write(plaintext.data(), plaintext.size());
		out.close();
	}
}

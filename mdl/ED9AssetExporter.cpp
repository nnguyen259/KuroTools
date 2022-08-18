
#include <iostream>
#include <fstream>
#include <vector>
#include "MDLFile.h"
#include "model.h"
#include <filesystem>
#include "AssetConfig.h"

namespace fs = std::filesystem;
int main(int argc, char** argv)
{
	if (argc > 1) {
		std::string filepath = std::string(argv[1]);
		std::error_code ec;

		AssetConfig conf("asset_config.json");

		if (fs::is_directory(filepath, ec))
		{
			std::vector<model> ani_mdls = {};
			model base_model;
			for (const auto& file : fs::directory_iterator(filepath)) {
				filepath = file.path().string();
				std::string base_filename = filepath.substr(filepath.find_last_of("/\\") + 1);
				std::string::size_type const p(base_filename.find_last_of('.'));
				std::string scene_name = base_filename.substr(0, p);

				decrypt(filepath);
				std::ifstream input(filepath, std::ios::binary);
				std::vector<unsigned char> buffer(std::istreambuf_iterator<char>(input), {});
				MDLFile mdl(scene_name, buffer);
				model m = mdl.extract_model(conf);
				if (m.meshes.size() != 0) 
					base_model = m;
				else
					ani_mdls.push_back(m);
			}
			for (size_t i = 0; i < ani_mdls.size(); i++) {
				base_model.to_merge(ani_mdls[i]);
			}
			base_model.to_fbx();
		}
		else {
			std::string base_filename = filepath.substr(filepath.find_last_of("/\\") + 1);
			std::string::size_type const p(base_filename.find_last_of('.'));
			std::string scene_name = base_filename.substr(0, p);

			decrypt(filepath);
			std::ifstream input(filepath, std::ios::binary);
			std::vector<unsigned char> buffer(std::istreambuf_iterator<char>(input), {});
			MDLFile mdl(scene_name, buffer);
			model m = mdl.extract_model(conf);
			m.to_fbx();
		}
	}


}

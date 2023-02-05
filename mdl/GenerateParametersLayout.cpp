// GenerateParametersLayout.cpp : Ce fichier contient la fonction 'main'. L'exécution du programme commence et se termine à cet endroit.
//

#include <iostream>
#include <fstream>
#include <vector>
#include <MDLFile.h>
#include <model.h>
#include <filesystem>
#include "AssetConfig.h"
#include <cstring>
#include <JsonGenerator.h>

namespace fs = std::filesystem;
int main(int argc, char** argv)
{
	
	if (argc > 1) {
		std::error_code ec;
		std::string filepath = std::string(argv[1]);
		AssetConfig conf("asset_config.json");
		if (fs::is_directory(filepath, ec))
		{
			std::vector<model> ani_mdls = {};
			model base_model;
			for (const auto& file : fs::directory_iterator(filepath)) {
				filepath = file.path().string();
				JsonGenerator gen(filepath, conf);

			}

		}
		else {

			std::string base_filename = filepath.substr(filepath.find_last_of("/\\") + 1);
			try {
				JsonGenerator gen(filepath, conf);
				
				
			}
			catch (std::exception e) {
				std::string msg = e.what();
				std::transform(msg.begin(), msg.end(), msg.begin(), ::toupper);
				std::cout << msg << " " << base_filename << std::endl;

			}
		}
	}
}

#pragma once
#include <string>
#include <iostream>
#include "AssetConfig.h"
class JsonGenerator
{
public:
	JsonGenerator(std::string filepath, AssetConfig conf) {
		std::string base_filename = filepath.substr(filepath.find_last_of("/\\") + 1);
		std::string::size_type const p(base_filename.find_last_of('.'));
		std::string scene_name = base_filename.substr(0, p);
		std::string extension = base_filename.substr(p+1, base_filename.length());
		
		if (extension.compare("mdl") == 0)
			MDLToJson(filepath, conf);
		else if (extension.compare("fbx") == 0)
			FBXToJson(filepath);
		else
			std::cout << "no idea" << std::endl;
		/*decrypt(filepath);
		std::ifstream input(filepath, std::ios::binary);
		std::vector<unsigned char> buffer(std::istreambuf_iterator<char>(input), {});
		MDLFile mdl(scene_name, buffer);*/
	}

	bool MDLToJson(std::string filepath, AssetConfig conf);
	bool FBXToJson(std::string filepath);

};


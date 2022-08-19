#pragma once
#include <string>
#include <json.hpp>
#include <fstream>
#include <unordered_map>
#include <iostream>
#include "CLEDecrypt.h"
using json = nlohmann::json;

struct AssetConfig
{

	std::unordered_map<std::string, std::unordered_map< unsigned int, std::string>> map_ids; //Key: Shader name Value: <Key: Switch map name, Value:tex slot value>
	int bone_limit_per_mesh = -1;

	AssetConfig(std::string json_filepath) {
		decrypt(json_filepath);
		std::ifstream f(json_filepath);
		//Be careful, the original asset_config file has comments in it, which are not supported by this lib (rightfully I think)
		json data = json::parse(f);

		if (data.count("BoneLimitPerMesh") > 0) {
		
			this->bone_limit_per_mesh = data["BoneLimitPerMesh"];
		
		}
		for (auto shader_data : data["ShaderInfos"]) {
			for (auto map_ : shader_data["switches"]) {
				this->map_ids[shader_data["name"]][map_["tex_slot"]] = map_["name"];
			}
		
		}
		
		f.close();
	
	
	
	
	}

};


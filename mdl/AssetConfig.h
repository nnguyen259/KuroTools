#pragma once
#include <string>
#include <nlohmann/json.hpp>
#include <fstream>
#include <unordered_map>
#include <iostream>
#include "CLEDecrypt.h"
using ordered_json = nlohmann::ordered_json;

struct AssetConfig
{

	std::unordered_map<std::string, std::unordered_map< unsigned int, std::string>> map_ids; //Key: Shader name Value: <Key: Switch map name, Value:tex slot value>
	std::unordered_map < std::string, std::unordered_map < std::string, unsigned int >> reverse_map_ids;
	int bone_limit_per_mesh = -1;

	AssetConfig(std::string json_filepath) {
		decrypt(json_filepath);
		std::ifstream f(json_filepath);
		//Be careful, the original asset_config file has comments in it, which are not supported by this lib (rightfully I think)
		ordered_json data = ordered_json::parse(f);

		if (data.count("BoneLimitPerMesh") > 0) {
		
			this->bone_limit_per_mesh = data["BoneLimitPerMesh"];
		
		}
		for (auto shader_data : data["ShaderInfos"]) {
			for (auto map_ : shader_data["switches"]) {
				this->map_ids[shader_data["name"]][map_["tex_slot"]] = map_["name"];
				this->reverse_map_ids[shader_data["name"]][map_["name"]] = map_["tex_slot"];
			}
		
		}
		f.close();
	}

};


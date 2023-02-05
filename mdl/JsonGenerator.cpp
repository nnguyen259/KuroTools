#include "JsonGenerator.h"
#include <CLEDecrypt.h>
#include <MDLFile.h>
bool JsonGenerator::MDLToJson(std::string filepath, AssetConfig conf) { 
	std::string base_filename = filepath.substr(filepath.find_last_of("/\\") + 1);
	std::string::size_type const p(base_filename.find_last_of('.'));
	std::string scene_name = base_filename.substr(0, p);
	decrypt(filepath);
	std::ifstream input(filepath, std::ios::binary);
	std::vector<unsigned char> buffer(std::istreambuf_iterator<char>(input), {});
	MDLFile mdl(scene_name, buffer);
	mdl.write_to_json(conf);
	
	
	return true; }
bool JsonGenerator::FBXToJson(std::string filepath) { 
	
	model m = model(filepath);
	m.to_json();
	return true; }
#pragma once
#include <cstdint>
#include <string>
#include <vector>
#include "Utilities.h"
#include "model.h"
#include "AssetConfig.h"
struct texture { 

	std::string name;
	uint32_t tex_slot;
	uint32_t int2;
	uint32_t int3;

	texture(std::vector<uint8_t>& content, uint32_t& addr) {
		this->name = read_string(content, addr);
		this->tex_slot = read_data<uint32_t>(content, addr);
		
		this->int2 = read_data<uint32_t>(content, addr);
		this->int3 = read_data<uint32_t>(content, addr);
	}
	std::string to_string();
	
	
};


struct switch_ {

	std::string name;
	uint32_t int1;

	switch_(std::vector<uint8_t>& content, uint32_t& addr) {
		this->name = read_string(content, addr);
		this->int1 = read_data<uint32_t>(content, addr);
	}
	std::string to_string();
};


struct param2 {

	std::string name;
	uint32_t type;
	std::vector<uint32_t> values;

	param2(std::vector<uint8_t>& content, uint32_t& addr) {
		this->name = read_string(content, addr);
		this->type = read_data<uint32_t>(content, addr);
		switch (this->type) {
		case 0:
		case 1:
		case 4:
			for (size_t i = 0; i < 1; i++)
				this->values.push_back(read_data<uint32_t>(content, addr));
			break;
		case 2:
		case 5:
			for (size_t i = 0; i < 2; i++)
				this->values.push_back(read_data<uint32_t>(content, addr));
			break;
		case 3:
		case 6:
			for (size_t i = 0; i < 3; i++)
				this->values.push_back(read_data<uint32_t>(content, addr));
			break;
		case 7:
			for (size_t i = 0; i < 4; i++)
				this->values.push_back(read_data<uint32_t>(content, addr));
			break;
		case 8:
			for (size_t i = 0; i < 16; i++)
				this->values.push_back(read_data<uint32_t>(content, addr));
			break;
		default:
			break;


		}

	}

	std::string to_string();

};
struct something_else2 {

	uint32_t a = 0, b = 0, c = 0;
	something_else2() = default;
	something_else2(std::vector<uint8_t>& content, uint32_t& addr) {
		this->a = read_data<uint32_t>(content, addr);
		this->b = read_data<uint32_t>(content, addr);
		this->c = read_data<uint32_t>(content, addr);
	}
	std::string to_string();

};

class material_data
{
public: 
	std::string str1;
	std::string str2;
	std::string str3;
	std::vector<texture> textures;
	std::vector<switch_> sths2;
	std::vector<param2> sths3;
	std::vector<uint8_t> uv_maps_idx;
	std::vector<uint8_t> sth1;
	something_else2 v3;
	float a = 0;
	uint32_t b = 0;

	material_data(std::vector<uint8_t>& content, uint32_t& addr);
	std::string to_string();

};


enum class datatype { face_indexes = 0x04, vertex_coordinates = 0x0C, uv_coordinates = 0x08, weights = 0x10 }; //not sure yet
enum class key_type { pos = 0x09, rot = 0x0A, scale = 0x0B, scrollUV = 0x0D, no_actual_idea = 0x0C}; 


struct mesh_data_stream {
	uint32_t id;
	std::vector<uint32_t> sth; //vertex, or index, or idk
	datatype type;
	mesh_data_stream(std::vector<uint8_t>& content, uint32_t& addr);


};
struct mesh_attributes {

	uint32_t material_id;
	std::vector<mesh_data_stream> datas;
	mesh_attributes(std::vector<uint8_t>& content, uint32_t& addr);
};

struct node_struct {
	std::string name;
	matrix4<float> transform;
	node_struct(std::vector<uint8_t>& content, uint32_t& addr);

};

struct keyframe_data {
	float time;
	std::vector<float> data;
	float flt2;
	vec2<float> v1, v2;
	keyframe_data(std::vector<uint8_t>& content, uint32_t& addr, size_t sz);

};



class node_data
{
public:

	std::string name;
	uint32_t id;
	uint32_t int1;
	uint32_t int2;
	vec3<float> T;
	vec4<float> something;
	uint32_t int3;
	vec3<float> R;
	vec3<float> S;
	vec3<float> v5;
	uint32_t int4;
	std::vector<uint32_t> children_ids;

	node_data(std::vector<uint8_t>& content, uint32_t& addr, uint32_t id);


};

class mesh_data
{
public:
	
	std::string name;
	std::vector<mesh_attributes> mesh_info;
	std::vector<node_struct> nodes;
	std::vector<float> clipping;

	mesh_data(std::vector<uint8_t>& content, uint32_t& addr);
	std::string to_string();

};



class bone_ani_data
{
public:

	std::string name;
	std::string bone_name;
	key_type ani_type;
	uint32_t b, c;
	std::vector<keyframe_data> keyframe_datas;
	
	bone_ani_data(std::vector<uint8_t>& content, uint32_t& addr);


};

struct anim_data {

	float start, end;
	std::vector< bone_ani_data> data;
	anim_data() = default;
	anim_data(std::vector<uint8_t>& content, uint32_t& addr, size_t cnt_struct);

};

class MDLFile
{
public:
	std::string name = "";
	std::vector<material_data> materials;
	std::vector<mesh_data> meshes;
	std::vector<node_data> nodes;
	std::vector<anim_data> ani;

	MDLFile(std::string name, std::vector<uint8_t>& content);
	model extract_model(AssetConfig conf);
	void create_node_hierarchy(tsl::ordered_map<std::string, node>& nodes, node_data node_info, unsigned int parent, std::string parent_name);
	bool write_to_json(AssetConfig conf);

};
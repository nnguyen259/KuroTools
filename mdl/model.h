#pragma once
#include <string>
#include <vector>
#include "Utilities.h"
#include <tsl/ordered_map.h>
#include <algorithm>
#include <assimp\scene.h>
#include <iostream>
#include "AssetConfig.h"



class node {
public:
	uint32_t id;
	
	std::string name;
	matrix4<float> transform;
	vec3<float> T, R, S; //I want to be sure
	std::vector<unsigned int> children;
	unsigned int parent;
	std::string parent_name;
};


struct tex {
	std::string name;
	std::string switch_name;
	unsigned int tex_slot;
	unsigned int uv;
	bool operator< (const tex& t2)
	{
		return this->tex_slot < t2.tex_slot;
	}
};

struct material {
	std::string name;
	std::string shader_name;
	unsigned int id;
	std::vector<tex> tex_data;
	std::vector<uint8_t> uv_map_ids;
};

struct bone {
	std::string name;
	std::vector<float> weights;
	std::vector<unsigned int> vertex_id;
	matrix4<float> offsetmatrix;
};

struct bounding_box {

	vec3<float> min;
	vec3<float> max;

};

struct mesh { //mesh are outside of the hierarchy, I think, they're not nodes?
	//std::map<std::string, bone> bones;
	std::string name;
	std::vector<vec3<float>> vertices;
	std::vector<vec3<float>> normals; //It's just a guess, I have no idea what it's supposed to be
	std::vector<vec3<float>> tangents;
	std::vector<vec3<unsigned int>> faces_indexes;
	std::vector < std::vector<vec2<float>>> uvs;
	std::map<std::string, bone> bones;
	unsigned int material_id = -1;
	mesh() = default;


};
class key {
public:
	float time;
	key(float time_) : time(time_) {}
	bool operator< (const key& k2)
	{
		return this->time < k2.time;
	}
};
struct keyframe_pos : public key {
	vec3<float> data;
	keyframe_pos(float time, vec3<float> data_) : key(time) {
		data = data_;
	}
};

struct keyframe_rot : public key {
	vec4<float> data;
	keyframe_rot(float time, vec4<float> data_) : key(time) {
		data = data_;
	}
};

struct keyframe_scl : public key {
	vec3<float> data;
	keyframe_scl(float time, vec3<float> data_) : key(time) {
		data = data_;
	}
};

struct bone_key_frames {
	std::vector<keyframe_pos> pos;
	std::vector<keyframe_rot> rot;
	std::vector<keyframe_scl> scl;

	void post_process_keys(float start, float end, vec3<float> position_bp, vec3<float> R, vec3<float> scaling_bp) {
		aiQuaternion rotation_bp(R.y, R.z, R.x);
		
		std::sort(pos.begin(), pos.end());
		std::sort(rot.begin(), rot.end());
		std::sort(scl.begin(), scl.end());

		if ((pos.size() != 0) || (rot.size() != 0) || (scl.size() != 0)) {
			//in that case we need to check that each of them has at least one key
			keyframe_pos pos_key(start, { position_bp.x,position_bp.y,position_bp.z });
			keyframe_rot rot_key(start, { rotation_bp.x,rotation_bp.y,rotation_bp.z, rotation_bp.w });
			keyframe_scl scl_key(start, { scaling_bp.x,scaling_bp.y,scaling_bp.z });

			if (pos.size() == 0)
			{
				pos.push_back(pos_key);
			}
			else if (pos[0].time > start) {
				pos.insert(pos.begin(),pos_key);
			}

			if (rot.size() == 0)
			{
				rot.push_back(rot_key);
			}
			else if (rot[0].time > start) {
				rot.insert(rot.begin(), rot_key);
			}
			if (scl.size() == 0)
			{
				scl.push_back(scl_key);
			}
			else if (pos[0].time > start) {
				scl.insert(scl.begin(), scl_key);
			}

		}
		for (auto& k : rot) {
			aiQuaternion current_rot(k.data.t, k.data.x, k.data.y, k.data.z);
			current_rot = rotation_bp * current_rot;
			k.data.t = current_rot.w;
			k.data.x = current_rot.x;
			k.data.y = current_rot.y;
			k.data.z = current_rot.z;
		}
	}


	//don't need to resample actually. I misread assimp documentation. Apparently you only need a single key if there are keys for the other components
	void interpolate_keys(float start, float end, vec3<float> position_bp, vec3<float> R, vec3<float> scaling_bp) {
		aiQuaternion rotation_bp(R.y, R.z, R.x);

		std::sort(pos.begin(), pos.end());
		std::sort(rot.begin(), rot.end());
		std::sort(scl.begin(), scl.end());
		std::vector<float> time_scale = { start, end };
		for (auto k : pos) {
			time_scale.push_back(k.time);
		}
		for (auto& k : rot) {
			time_scale.push_back(k.time);
			aiQuaternion current_rot(k.data.t, k.data.x, k.data.y, k.data.z);
			current_rot = rotation_bp * current_rot;
			k.data.t = current_rot.w;
			k.data.x = current_rot.x;
			k.data.y = current_rot.y;
			k.data.z = current_rot.z;
		}
		for (auto k : scl) {
			time_scale.push_back(k.time);
		}

		std::sort(time_scale.begin(), time_scale.end());
		time_scale.erase(std::unique(time_scale.begin(), time_scale.end()), time_scale.end());

		int idx_pos = 0, idx_rot = 0, idx_scl = 0;
		unsigned int time_cnt = 0;
		for (auto time : time_scale) {
			keyframe_pos pos_key(time, { 0,0,0 });
			pos_key.time = time;
			if (idx_pos < pos.size()) {
				if (pos[idx_pos].time > time) {
					if ((idx_pos - 1) >= 0) {
						keyframe_pos previous_key = pos[idx_pos - 1];

						float t = ((float)(time - previous_key.time)) / (pos[idx_pos].time - previous_key.time);
						pos_key.data.x = (1 - t) * previous_key.data.x + t * pos[idx_pos].data.x;
						pos_key.data.y = (1 - t) * previous_key.data.y + t * pos[idx_pos].data.y;
						pos_key.data.z = (1 - t) * previous_key.data.z + t * pos[idx_pos].data.z;
					}
					else {
						pos_key.data.x = pos[idx_pos].data.x;
						pos_key.data.y = pos[idx_pos].data.y;
						pos_key.data.z = pos[idx_pos].data.z;

					}
					pos.insert(pos.begin() + idx_pos, pos_key);
					
				}
				
			}
			else {
				if ((idx_pos - 1) >= 0) {
					keyframe_pos previous_key = pos[idx_pos - 1];


					pos_key.data.x = previous_key.data.x;
					pos_key.data.y = previous_key.data.y;
					pos_key.data.z = previous_key.data.z;
				}
				else {
					pos_key.data.x = position_bp.x;
					pos_key.data.y = position_bp.y;
					pos_key.data.z = position_bp.z;

				}
				pos.insert(pos.begin() + idx_pos, pos_key);
			
			}

			idx_pos++;

			keyframe_rot rot_key(time, { 0,0,0, 0 });
			rot_key.time = time;
			if (idx_rot < rot.size()) {
				if (rot[idx_rot].time > time) {
					if ((idx_rot - 1) >= 0) {
						keyframe_rot previous_key = rot[idx_rot - 1];

						float t = ((float)(time - previous_key.time)) / (rot[idx_rot].time - previous_key.time);
						rot_key.data.x = (1 - t) * previous_key.data.x + t * rot[idx_rot].data.x;
						rot_key.data.y = (1 - t) * previous_key.data.y + t * rot[idx_rot].data.y;
						rot_key.data.z = (1 - t) * previous_key.data.z + t * rot[idx_rot].data.z;
						rot_key.data.t = (1 - t) * previous_key.data.t + t * rot[idx_rot].data.t;
					}
					else {
						rot_key.data.x = rot[idx_rot].data.x;
						rot_key.data.y = rot[idx_rot].data.y;
						rot_key.data.z = rot[idx_rot].data.z;
						rot_key.data.t = rot[idx_rot].data.t;
					}

					rot.insert(rot.begin() + idx_rot, rot_key);
					
				}
			}
			else {
				if ((idx_rot - 1) >= 0) {
					keyframe_rot previous_key = rot[idx_rot - 1];


					rot_key.data.x = previous_key.data.x;
					rot_key.data.y = previous_key.data.y;
					rot_key.data.z = previous_key.data.z;
					rot_key.data.t = previous_key.data.t;
				}
				else {
					rot_key.data.x = rotation_bp.x;
					rot_key.data.y = rotation_bp.y;
					rot_key.data.z = rotation_bp.z;
					rot_key.data.t = rotation_bp.w;

				}

				rot.insert(rot.begin() + idx_rot, rot_key);
				
			}

			idx_rot++;


			keyframe_scl scl_key(time, { 0,0,0 });
			scl_key.time = time;
			if (idx_scl < scl.size()) {
				if (scl[idx_scl].time > time) {
					if ((idx_scl - 1) >= 0) {
						keyframe_scl previous_key = scl[idx_scl - 1];

						float t = ((float)(time - previous_key.time)) / (scl[idx_scl].time - previous_key.time);
						scl_key.data.x = (1 - t) * previous_key.data.x + t * scl[idx_scl].data.x;
						scl_key.data.y = (1 - t) * previous_key.data.y + t * scl[idx_scl].data.y;
						scl_key.data.z = (1 - t) * previous_key.data.z + t * scl[idx_scl].data.z;
					}
					else {
						scl_key.data.x = scl[idx_scl].data.x;
						scl_key.data.y = scl[idx_scl].data.y;
						scl_key.data.z = scl[idx_scl].data.z;

					}
					scl.insert(scl.begin() + idx_scl, scl_key);
					
				}
			}
			else {
				if ((idx_scl - 1) >= 0) {
					keyframe_scl previous_key = scl[idx_scl - 1];


					scl_key.data.x = previous_key.data.x;
					scl_key.data.y = previous_key.data.y;
					scl_key.data.z = previous_key.data.z;
				}
				else {
					scl_key.data.x = scaling_bp.x;
					scl_key.data.y = scaling_bp.y;
					scl_key.data.z = scaling_bp.z;

				}
				scl.insert(scl.begin() + idx_scl, scl_key);
				
			}
			idx_scl++;

			time_cnt++;
		}
	}
};

struct animation {
	std::string name;
	float start, end;
	std::map<std::string, bone_key_frames> ani_bone_keys;
};



class model
{
public:
	model() = default;
	model(std::string fbx_file);
	~model() = default;
	std::string name;
	std::map<std::string, std::vector<mesh>> meshes; //node name
	std::map<std::string, animation> anis; //animation name
	animation bind_pose; //I think blender sets the bind pose as the first pose it finds among the animations, effectively FUCKING UP the transforms
	std::map<unsigned int, material> mats;
	tsl::ordered_map<std::string, node> nodes;
	void to_json();
	void to_mdl(AssetConfig config);
	void to_fbx(const AssetConfig &conf);
	void to_merge(const model& m2);
};

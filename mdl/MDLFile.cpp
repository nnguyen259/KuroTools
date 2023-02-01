#include "MDLFile.h"
#include "Utilities.h"
#include <iostream>
#include <fstream>
#include <nlohmann/json.hpp>
using ordered_json = nlohmann::ordered_json;


bool MDLFile::write_to_json(AssetConfig conf) {
	
	ordered_json j;

	
	for (auto mat : this->materials) {
		
		for (auto param : mat.sths3){
			std::string value = "";
			switch (param.type) {
			case 0:
			case 1:
			case 4:
				
				value = value + std::to_string(read_as_float(param.values[0]));
				
				break;
			case 2:
			case 5:
				value = value + "[";
				for (size_t i = 0; i < 1; i++)
					value = value + std::to_string(read_as_float(param.values[i])) + ",";
				value = value + std::to_string(read_as_float(param.values[1]));
				value = value + "]";
				break;
			case 3:
			case 6:
				value = value + "[";
				for (size_t i = 0; i < 2; i++)
					value = value + std::to_string(read_as_float(param.values[i])) + ",";
				value = value + std::to_string(read_as_float(param.values[2]));
				value = value + "]";
				break;
			case 7:
				value = value + "[";
				for (size_t i = 0; i < 3; i++)
					value = value + std::to_string(read_as_float(param.values[i])) + ",";
				value = value + std::to_string(read_as_float(param.values[3]));
				value = value + "]";
				break;
			case 8:
				value = value + "[";
				for (size_t i = 0; i < 15; i++)
					value = value + std::to_string(read_as_float(param.values[i])) + ",";
				value = value + std::to_string(read_as_float(param.values[15]));
				value = value + "]";
				break;
			}
			j[mat.str1][mat.str2][param.name] = value;
		}
		for (auto switch__ : mat.sths2) {
			
			j[mat.str1]["switches"][switch__.name] = (int)switch__.int1;
		}
		j[mat.str1]["unknown values"]["a"] = (int)mat.v3.a;
		j[mat.str1]["unknown values"]["b"] = (int)mat.v3.b;
		j[mat.str1]["unknown values"]["c"] = (int)mat.v3.c;
		j[mat.str1]["unknown values"]["d"] = (float)mat.a;
		j[mat.str1]["unknown values"]["e"] = (int)mat.b;
		unsigned int uv_idx = 0;
		for (auto tex : mat.textures) {

			std::string switch_name = conf.map_ids[mat.str2][tex.tex_slot];
			j[mat.str1]["texture maps"][switch_name]["texture"] = tex.name;
			j[mat.str1]["texture maps"][switch_name]["uv map index"] = (int)mat.uv_maps_idx[uv_idx];
			uv_idx++;
		
		}

	}

	std::ofstream o(this->name + ".json");
	o << std::setw(4) << j << std::endl;
	
	o.close();
	
	return true; }

material_data::material_data(std::vector<uint8_t>& content, uint32_t &addr) {

	unsigned int init = addr;
	this->str1 = read_string(content, addr);
	this->str2 = read_string(content, addr);
	this->str3 = read_string(content, addr);
	size_t cnt = read_data<uint32_t>(content, addr);

	for (size_t i = 0; i < cnt; i++) {
		this->textures.push_back(texture(content, addr));
	}

	cnt = read_data<uint32_t>(content, addr);
	size_t cnt_params = cnt;
	for (size_t i = 0; i < cnt; i++) {
		param2 param = param2(content, addr);
		this->sths3.push_back(param);
		
	}
	cnt = read_data<uint32_t>(content, addr);

	size_t cnt_switch = cnt;
	for (size_t i = 0; i < cnt; i++) {
		this->sths2.push_back(switch_(content, addr));
	}


	cnt = read_data<uint32_t>(content, addr);
	for (size_t i = 0; i < cnt; i++) {
		this->uv_maps_idx.push_back(read_data<uint8_t>(content, addr));
	}

	cnt = read_data<uint32_t>(content, addr);
	for (size_t i = 0; i < cnt; i++) {
		this->sth1.push_back(read_data<uint8_t>(content, addr));
	}

	this->v3 = something_else2(content, addr);
	this->a = read_data<float>(content, addr);
	this->b = read_data<uint32_t>(content, addr);
	unsigned int end = addr;
	//std::cout << this->str1 << " " << std::hex << end-init << " " << this->v3.a << " " << this->v3.b << " " << this->v3.c << std::endl;


	



}
std::string texture::to_string() {
	std::string result = "";
	result = result + "texture name: " + this->name + "\n";
	result = result + "MAPID: " + std::to_string(this->tex_slot) + "\n";
	result = result + "IDK1: " + std::to_string(this->int2) + "\n";
	result = result + "IDK2: " + std::to_string(this->int3) + "\n";
	return result;
}

std::string param2::to_string() {
	std::string result = "";
	result = result + "something else name: " + this->name + "\n";
	result = result + "type: " + std::to_string(this->type) + "\n";
	for (auto i : this->values) {
		result = result + "param: " + std::to_string(i) + "\n";
	}
	
	return result;
}

std::string switch_::to_string() {
	std::string result = "";
	result = result + "something2 name: " + this->name + "\n";
	result = result + "int: " + std::to_string(this->int1) + "\n";
	return result;
}

std::string something_else2::to_string() {
	std::string result = "";
	result = result + "A: " + std::to_string(this->a) + "\n";
	result = result + "B: " + std::to_string(this->b) + "\n";
	result = result + "C: " + std::to_string(this->c) + "\n";
	return result;
}

std::string material_data::to_string() {
	std::string result = "";
	result = result + "name: " + this->str1 + "\n";
	result = result + "name2: " + this->str2 + "\n";
	result = result + "material_name: " + this->str3 + "\n";
	for (auto tex : this->textures)
		result = result + tex.to_string();
	for (auto sth : this->sths3)
		result = result + sth.to_string();
	for (auto sth : this->sths2)
		result = result + sth.to_string();
	result = result + "uv maps_idx: ";
	for (auto sth : this->uv_maps_idx)
		result = result + std::to_string(sth);
	result = result + "\n";
	for (auto sth : this->sth1)
		result = result + std::to_string(sth);
	result = result + "\n";
	result = result + this->v3.to_string();
	result = result + std::to_string(this->a) + "\n";
	result = result + std::to_string(this->b) + "\n";
	return result;

}

mesh_data_stream::mesh_data_stream(std::vector<uint8_t>& content, uint32_t& addr) {
	
	this->id = read_data<uint32_t>(content, addr);
	size_t size = read_data<uint32_t>(content, addr);
	this->type = static_cast<datatype>(read_data<uint32_t>(content, addr));
	
	size_t cnt = size / 4;
	for (size_t i = 0; i < cnt; i++) {
		this->sth.push_back(read_data<uint32_t>(content, addr));
		
	}
}

mesh_attributes::mesh_attributes(std::vector<uint8_t>& content, uint32_t& addr) {
	
	this->material_id = read_data<uint32_t>(content, addr);
	//std::cout << "material id: " << material_id << std::endl;
	size_t cnt = read_data<uint32_t>(content, addr);
	for (size_t i = 0; i < cnt; i++) {
		this->datas.push_back(mesh_data_stream(content, addr));
		auto stream = this->datas[this->datas.size() - 1];
		//std::cout << std::hex << addr << " " << stream.id << " " << (uint32_t) stream.type << " " << stream.sth.size() << std::endl;

	}
	
}

node_struct::node_struct(std::vector<uint8_t>& content, uint32_t& addr) {
	this->name = read_string(content, addr);
	this->transform  = read_data<matrix4<float>>(content,addr);
}

keyframe_data::keyframe_data(std::vector<uint8_t>& content, uint32_t& addr, size_t sz) {
	this->time = read_data<float>(content, addr);
	for (size_t i = 0; i < sz; i++) {
		this->data.push_back(read_data<float>(content, addr));
	}

	this->flt2 = read_data<float>(content, addr);
	this->v1 = read_data<vec2<float>>(content, addr);
	this->v2 = read_data<vec2<float>>(content, addr);
}

mesh_data::mesh_data(std::vector<uint8_t>& content, uint32_t& addr) {

	this->name = read_string(content, addr);
	size_t size = read_data<uint32_t>(content, addr);
	size_t cnt = read_data<uint32_t>(content, addr);
	//std::cout << this->name << std::endl;
	for (size_t i = 0; i < cnt; i++) {
		this->mesh_info.push_back(mesh_attributes(content, addr));
	}
	
	size_t nb_nodes = read_data<uint32_t>(content, addr);
	//std::cout << "nb bones " << nb_nodes << std::endl;
	for (size_t i = 0; i < nb_nodes; i++) {
		this->nodes.push_back(node_struct(content, addr));
	}

	cnt = read_data<uint32_t>(content, addr); //1403da718
	
	for (size_t i = 0; i < cnt / 4; i++) {
		float clip = read_data<float>(content, addr);
		this->clipping.push_back(clip);
		//std::cout << clip << " ";
	}
	//std::cout << std::endl;

}

std::string mesh_data::to_string() {
	std::string result = "";
	result = result + this->name;
	result = result + " " + std::to_string(this->mesh_info.size());
	return result;

}




node_data::node_data(std::vector<uint8_t>& content, uint32_t& addr, uint32_t id) {

	this->id = id;
	this->name = read_string(content, addr);
	
	this->int1 = read_data<uint32_t>(content, addr); //type of node : mesh 2, bone 1, locator 0
	this->int2 = read_data<uint32_t>(content, addr); // equals -1 if not a mesh, otherwise id of the "pack" of meshes in the second section
	
	this->T = read_data<vec3<float>>(content, addr);
	this->something = read_data<vec4<float>>(content, addr); 
	this->int3 = read_data<uint32_t>(content, addr);
	this->R = read_data<vec3<float>>(content, addr);
	this->S = read_data<vec3<float>>(content, addr);
	
	this->v5 = read_data<vec3<float>>(content, addr);
	this->int4 = read_data<uint32_t>(content, addr);
	size_t cnt = this->int4 * 4;
	for (size_t i = 0; i < cnt / 4; i++) {
		this->children_ids.push_back(read_data<uint32_t>(content, addr));
	}


}

size_t get_cnt(key_type sz)

{
	switch (sz) {
	default:{
		std::string mess = "unknown type " + std::to_string((uint32_t)sz);
		throw std::exception(mess.c_str());
		return 1; }
	case key_type::pos://position
	case key_type::scale://scale
	//case 0xe:
		return 3;
	case key_type::rot: //quaternion
	//case 0xf:
		return 4;
	case key_type::scrollUV:
		return 2;
	case key_type::no_actual_idea: //used for grendel somehow
		return 1;
	}
}



bone_ani_data::bone_ani_data(std::vector<uint8_t>& content, uint32_t& addr) {
	this->name = read_string(content, addr);
	this->bone_name = read_string(content, addr);
	this->ani_type = read_data<key_type>(content, addr);
	this->b = read_data<uint32_t>(content, addr);
	this->c = read_data<uint32_t>(content, addr);
	size_t cnt = read_data<uint32_t>(content, addr);
	//std::cout << " " << std::hex << addr << std::endl;
	size_t sz_ = get_cnt(this->ani_type);

	for (size_t i = 0; i < cnt; i++) {
		this->keyframe_datas.push_back(keyframe_data(content, addr, sz_));
	}
	
}

anim_data::anim_data(std::vector<uint8_t>& content, uint32_t& addr, size_t cnt_struct) {
	for (size_t j = 0; j < cnt_struct; j++) {
		this->data.push_back(bone_ani_data(content, addr));
	}
	this->start = read_data<float>(content, addr);
	this->end = read_data<float>(content, addr);

}

MDLFile::MDLFile(std::string name, std::vector<uint8_t>& content) {

	this->name = name;
	uint32_t no_idea = content[0x4];
	uint32_t no_idea2 = content[0x8];
	uint32_t addr = 0x0C;
	uint32_t type;
	uint32_t size;
	uint32_t cnt_struct;
	
	while (addr < content.size() - 4) {

		type = read_data<uint32_t>(content, addr);
		size = read_data<uint32_t>(content, addr);
		cnt_struct = read_data<uint32_t>(content, addr);

		switch (type) {
		case 0:
			for (size_t j = 0; j < cnt_struct; j++) {
				material_data struc = material_data(content, addr);
				/*std::ofstream file(struc.str1 + "params.txt");
				file << struc.to_string();
				file.close();*/

				this->materials.push_back(struc);
			}
			break;
		case 1:
			for (size_t j = 0; j < cnt_struct; j++) {
				this->meshes.push_back(mesh_data(content, addr));
			}
			break;
		case 2:{
			for (size_t j = 0; j < cnt_struct; j++) {
				this->nodes.push_back(node_data(content, addr, j));
			}
			//debug TRS 
			std::vector<node_data> nodes_sorted = {};
			for (auto node_ : this->nodes) {
				nodes_sorted.push_back(node_);
			}
			std::sort(nodes_sorted.begin(), nodes_sorted.end(), [](node_data a, node_data b)
				{
					return a.name > b.name;
				});
			/*for (auto node : nodes_sorted) {
				std::cout << "written as:" << " " << node.name << std::endl;
				std::cout << "" << "T " << node.T.x << " " << node.T.y << " " << node.T.z << std::endl;
				std::cout << "" << "R " << node.R.x << " " << node.R.y << " " << node.R.z << std::endl;
				std::cout << "" << "S " << node.S.x << " " << node.S.y << " " << node.S.z << std::endl;
			}*/

			break;
		}
			case 3:
				this->ani.push_back(anim_data(content, addr, cnt_struct));
				break;
			default:
				throw std::exception("unknown section type");
		
		
		}
		
	}


}

void MDLFile::create_node_hierarchy(tsl::ordered_map<std::string, node> &nodes, node_data node_info, unsigned int parent, std::string parent_name) {
	
	node nd;
	nd.id = node_info.id;
	nd.parent = parent;
	nd.parent_name = parent_name;
	nd.T = node_info.T;
	nd.R = node_info.R;
	nd.S = node_info.S;
	nd.transform = matrix4<float>(node_info.T, node_info.R, node_info.S);
	nd.name = node_info.name;
	nd.children = node_info.children_ids;
	nodes[nd.name] = nd;
	for (unsigned int children_id = 0; children_id < nd.children.size(); children_id++) {
		create_node_hierarchy(nodes, this->nodes[nd.children[children_id]], nd.id, nd.name);
		
	}

	

}

model MDLFile::extract_model(AssetConfig conf) {
	model mdl;
	mdl.name = this->name;
	unsigned int id_mat = 0;
	//The first thing we'll do is creating the node using the third section info
	

	create_node_hierarchy(mdl.nodes, this->nodes[0], -1, "");
	for (material_data structa : this->materials) {

		material mat;
		mat.name = structa.str1; //at least str1 is unique
		mat.id = id_mat;
		id_mat++;
		unsigned int tex_id = 0;
		for (texture tex : structa.textures) {
			std::string switch_name = conf.map_ids[structa.str2][tex.tex_slot];
			mat.tex_data.push_back({ tex.name, switch_name, tex.tex_slot, structa.uv_maps_idx[tex_id] });
			tex_id++;
		}
		mat.uv_map_ids = structa.uv_maps_idx;
		mdl.mats[mat.id] = mat;

	}



	for (mesh_data structb : this->meshes) {
		
		
		unsigned int internal_mesh_id = 0;
		for (mesh_attributes meshes_data : structb.mesh_info) {
			std::string material_name = this->materials[meshes_data.material_id].str1;// std::string(this->materials[meshes_data.material_id].st1.begin(), this->materials[meshes_data.material_id].sth1.end());

			mesh m;
			
			m.name = structb.name;
			if (mdl.nodes.count(m.name) == 0) {
				node mesh_node = mdl.nodes[structb.name];
				mesh_node.children = {};
				mesh_node.name = m.name;
				mesh_node.id = mdl.nodes.size();
				mdl.nodes[m.name] = mesh_node;
				//mdl.nodes[structb.name].children.push_back(mesh_node.id);
				if (mdl.nodes[structb.name].parent != -1){
					mdl.nodes[mdl.nodes[structb.name].parent_name].children.push_back(mesh_node.id); //adding it to the hierarchy at the same level than the first mesh of its kind
				}
			
			}
			

			std::vector<float> weights, vertices, normals, tangents;
			
			std::vector<std::vector<vec2<float>>> uv_maps;
			std::vector<unsigned int> face_idx, bones_ids;
			m.material_id = meshes_data.material_id;
			for (mesh_data_stream mesh_data : meshes_data.datas) {

				switch (mesh_data.type) {
					case datatype::vertex_coordinates: {
						//Idk why there are 3 separate streams of type C but they don't contain each coordinate. The first stream seems to match the face indexes stream, not the others, so I will just drop the last two for the time being?
						float* floats = reinterpret_cast<float*>(mesh_data.sth.data());
						std::vector<float> a = std::vector<float>(floats, floats + mesh_data.sth.size());
						if (mesh_data.id == 0) { //1403dab80
							vertices = a;
						}
						else if (mesh_data.id == 1)
							normals = a;
						else if (mesh_data.id == 2)
							tangents = a;
						break;
					}

					case datatype::face_indexes:
						face_idx = mesh_data.sth;
						break;
					case datatype::uv_coordinates:{
						vec2<float>* floats = reinterpret_cast<vec2<float>*>(mesh_data.sth.data());
						m.uvs.push_back(std::vector<vec2<float>>(floats, floats + mesh_data.sth.size()/2));
						break;
					}
					case datatype::weights:{
						switch (mesh_data.id) {
						case 5:
						{
							float* floats = reinterpret_cast<float*>(mesh_data.sth.data());
							weights = std::vector<float>(floats, floats + mesh_data.sth.size());
							break;
						}
						case 6:{
							bones_ids = mesh_data.sth;
							break;
						}
						}
						break;
					}

						
				}

			}
			
			//std::ofstream myfile;
			//myfile.open(m.name + ".txt");
			
			for (size_t i = 0; i < vertices.size()/3; i++) {
				m.vertices.push_back({ vertices[i * 3], vertices[i * 3 + 1], vertices[i * 3 + 2] });
				m.normals.push_back({ normals[i * 3], normals[i * 3 + 1], normals[i * 3 + 2] });
				m.tangents.push_back({ tangents[i * 3], tangents[i * 3 + 1], tangents[i * 3 + 2] });

				//myfile << vertices[i * 3] << " " << vertices[i * 3 + 1] << " " << vertices[i * 3 + 2] << " | ";
				//myfile << normals[i * 3] << " " << normals[i * 3 + 1] << " " << normals[i * 3 + 2] << " | ";
				//myfile << tangents[i * 3] << " " << tangents[i * 3 + 1] << " " << tangents[i * 3 + 2] << std::endl;
			}
			

			for (size_t i = 0; i < face_idx.size()/3; i++) {
				m.faces_indexes.push_back({ face_idx[i * 3], face_idx[i * 3 + 1], face_idx[i * 3 + 2] });
				//myfile << face_idx[i * 3] << " " << face_idx[i * 3 + 1] << " " << face_idx[i * 3 + 2] << std::endl;
			}

			//myfile.close();
			for (size_t i = 0; i < bones_ids.size() / 4; i++) {

				unsigned int vertex_id = i;

				node_struct node_1 = structb.nodes[bones_ids[i * 4]];
				node_struct node_2 = structb.nodes[bones_ids[i * 4 + 1]];
				node_struct node_3 = structb.nodes[bones_ids[i * 4 + 2]];
				node_struct node_4 = structb.nodes[bones_ids[i * 4 + 3]];
				m.bones[node_1.name].vertex_id.push_back(vertex_id);
				m.bones[node_2.name].vertex_id.push_back(vertex_id);
				m.bones[node_3.name].vertex_id.push_back(vertex_id);
				m.bones[node_4.name].vertex_id.push_back(vertex_id);

				m.bones[node_1.name].weights.push_back(weights[i * 4 + 0]);
				m.bones[node_2.name].weights.push_back(weights[i * 4 + 1]);
				m.bones[node_3.name].weights.push_back(weights[i * 4 + 2]);
				m.bones[node_4.name].weights.push_back(weights[i * 4 + 3]);
				
			}
			std::sort(mdl.mats[m.material_id].tex_data.begin(), mdl.mats[m.material_id].tex_data.end());
			
			for (auto node_ : structb.nodes) {
				m.bones[name].offsetmatrix = node_.transform;
			}

			std::vector<std::string> bones_to_erase = {};
			for (auto bone_it : m.bones) {
				if (mdl.nodes.count(bone_it.first) == 0) //Prevents the fbx from loading in blender but not the dae, so I get rid of any bone that doesn't have a node. Not sure what I'm supposed to do here tbh. It's the same with animation specific nodes
					bones_to_erase.push_back(bone_it.first);
			}
			for (auto bone_name_to_erase : bones_to_erase)
				m.bones.erase(bone_name_to_erase);


			mdl.meshes[m.name].push_back(m);
			internal_mesh_id++;
		}
		
	
	}




	//create ani data
	mdl.bind_pose.name = "bind_pose";
	mdl.bind_pose.start = 0;
	mdl.bind_pose.end = 0.1;
	
	for (auto nd : mdl.nodes) {
		aiQuaternion rotation_bp(mdl.nodes[nd.first].R.y, mdl.nodes[nd.first].R.z, mdl.nodes[nd.first].R.x);
		mdl.bind_pose.ani_bone_keys[nd.first].pos.push_back(keyframe_pos(0, { mdl.nodes[nd.first].T.x, mdl.nodes[nd.first].T.y, mdl.nodes[nd.first].T.z }));
		mdl.bind_pose.ani_bone_keys[nd.first].rot.push_back(keyframe_rot(0, { rotation_bp.x, rotation_bp.y, rotation_bp.z, rotation_bp.w }));
		mdl.bind_pose.ani_bone_keys[nd.first].scl.push_back(keyframe_scl(0, { mdl.nodes[nd.first].S.x, mdl.nodes[nd.first].S.y, mdl.nodes[nd.first].S.z }));

	}

	for (anim_data anim : this->ani) {
		animation ani;
		ani.name = mdl.name;
		ani.start = anim.start;
		ani.end = anim.end;
		for (bone_ani_data anim_bone_data : anim.data) {
			
			switch (anim_bone_data.ani_type) {
				case key_type::pos: {
					for (auto poskey : anim_bone_data.keyframe_datas) {
						ani.ani_bone_keys[anim_bone_data.bone_name].pos.push_back(keyframe_pos( poskey.time, {poskey.data[0],poskey.data[1],poskey.data[2]} ));
						
					}
					break;
				}
				case key_type::rot: {
					for (auto rotkey : anim_bone_data.keyframe_datas) {
						ani.ani_bone_keys[anim_bone_data.bone_name].rot.push_back(keyframe_rot( rotkey.time, {rotkey.data[0],rotkey.data[1],rotkey.data[2], rotkey.data[3]} ));
					}
					break;
				}
				case key_type::scale: {
					for (auto sclkey : anim_bone_data.keyframe_datas) {
						ani.ani_bone_keys[anim_bone_data.bone_name].scl.push_back(keyframe_scl(sclkey.time, {sclkey.data[0],sclkey.data[1],sclkey.data[2]}));
					}
					break;
				}
			}
			
		}
		for (auto& ani_bone_k : ani.ani_bone_keys) {
			
			
			ani_bone_k.second.post_process_keys(ani.start, ani.end, mdl.nodes[ani_bone_k.first].T, mdl.nodes[ani_bone_k.first].R, mdl.nodes[ani_bone_k.first].S);
		}

		mdl.anis[ani.name] = ani;

	}
	

	return mdl;




}
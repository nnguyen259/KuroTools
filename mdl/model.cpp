#include "model.h"
#include <assimp\scene.h>
#include <assimp\Exporter.hpp>
#include <assimp\cimport.h>
#include <iostream>
#include <filesystem>
#include "CLEDecrypt.h"
#include <assimp/postprocess.h>
#include <set>
#include <algorithm> 
namespace fs = std::filesystem;

std::unordered_set<std::string> all_possible_texture_maps_switches = {
	"SWITCH_DIFFUSEMAP0",
	"SWITCH_DIFFUSEMAP1",
	"SWITCH_DIFFUSEMAP2",
	"SWITCH_NORMALMAP0",
	"SWITCH_NORMALMAP1",
	"SWITCH_NORMALMAP2",
	"SWITCH_GLOWMAP0",
	"SWITCH_GLOWMAP1",
	"SWITCH_MASKMAP0",
	"SWITCH_MASKMAP1",
	"SWITCH_MASKMAP2",
	"SWITCH_TOONMAP",
	"SWITCH_DUDVMAP",
	"TRANSLUCENT_MAP",
	"",
};


void model::to_fbx(const AssetConfig &conf) {

	size_t real_nb_of_meshes = 0;
	for (auto mesh : this->meshes) {
		real_nb_of_meshes += mesh.second.size();
	}
		

	std::map <std::string, std::vector<unsigned int>> meshes_id; 
	std::map<std::string, std::vector<aiBone*>> bones_ptr;
	aiMesh** aimeshes = new aiMesh * [real_nb_of_meshes];
	aiMaterial** aimaterials = new aiMaterial * [this->mats.size()];

	aiNode** aiNodes = new aiNode * [this->nodes.size()];

	unsigned int idx_node = 0;
	std::map<unsigned int, aiNode*> node_ptrs;
	std::map<std::string, aiNode*> node_ptrs_str;
	size_t nb_nodes = this->nodes.size();

	for (auto it_nd : this->nodes) {

		aiNodes[idx_node] = new aiNode();
		aiNodes[idx_node]->mName = it_nd.second.name;
		aiMatrix4x4 transform_node = aiMatrix4x4(it_nd.second.transform.a.x, it_nd.second.transform.a.y, it_nd.second.transform.a.z, it_nd.second.transform.a.t,
			it_nd.second.transform.b.x, it_nd.second.transform.b.y, it_nd.second.transform.b.z, it_nd.second.transform.b.t,
			it_nd.second.transform.c.x, it_nd.second.transform.c.y, it_nd.second.transform.c.z, it_nd.second.transform.c.t,
			it_nd.second.transform.d.x, it_nd.second.transform.d.y, it_nd.second.transform.d.z, it_nd.second.transform.d.t);

		aiNodes[idx_node]->mTransformation = transform_node.Transpose();

		size_t nb_children = it_nd.second.children.size();
		aiNodes[idx_node]->mNumChildren = nb_children;
		aiNodes[idx_node]->mChildren = new aiNode * [nb_children]();

		node_ptrs[it_nd.second.id] = aiNodes[idx_node];
		node_ptrs_str[it_nd.second.name] = aiNodes[idx_node];
		idx_node++;


	}

	aiNode* rootNode = NULL;
	idx_node = 0;
	for (auto ptr_node : node_ptrs) {
		
		unsigned int id = ptr_node.first;
		std::string name = ptr_node.second->mName.C_Str();
		if (id == 0)
			rootNode = ptr_node.second;
		std::vector<unsigned int> children_ids = this->nodes[name].children;
		for (unsigned int i = 0; i < children_ids.size(); i++) {
			ptr_node.second->mChildren[i] = node_ptrs[children_ids[i]];
			node_ptrs[children_ids[i]]->mParent = ptr_node.second;
		}
	}

	size_t cnt_mat = 0;
	
	for (auto material_ : this->mats) {
		aiMaterial* mat_ = new aiMaterial();
		aiString name;
		name.Set(material_.second.name);
		mat_->AddProperty(&name, AI_MATKEY_NAME);
		aiTextureType type;
		int channel = 0;

		for (auto tex : material_.second.tex_data) {
			aiString nametex;
			
			std::string texture_full_name = tex.name + ".dds";
			std::string full_path = std::filesystem::current_path().string() + "\\" + texture_full_name;
			if (!fs::exists(full_path))
				std::cout << "The texture " << full_path << " was not found.\n";
			else
				decrypt(full_path);

			nametex.Set(texture_full_name);
			if (tex.switch_name == "SWITCH_DIFFUSEMAP0")
				type = aiTextureType_DIFFUSE;
			else if (tex.switch_name == "SWITCH_DIFFUSEMAP1")
				type = aiTextureType_DIFFUSE;
			else if (tex.switch_name == "SWITCH_DIFFUSEMAP2")
				type = aiTextureType_DIFFUSE;
			else if (tex.switch_name == "SWITCH_NORMALMAP0")
				type = aiTextureType_NORMALS;
			else if (tex.switch_name == "SWITCH_NORMALMAP1")
				type = aiTextureType_NORMALS;
			else if (tex.switch_name == "SWITCH_GLOWMAP0")
				type = aiTextureType_EMISSIVE;
			else if (tex.switch_name == "SWITCH_GLOWMAP1")
				type = aiTextureType_EMISSIVE;
			else if (tex.switch_name == "SWITCH_MASKMAP0")
				type = aiTextureType_UNKNOWN;
			else if (tex.switch_name == "SWITCH_MASKMAP1")
				type = aiTextureType_UNKNOWN;
			else if (tex.switch_name == "SWITCH_TOONMAP")
				type = aiTextureType_UNKNOWN;
			else if (tex.switch_name == "SWITCH_NORMALMAP2")
				type = aiTextureType_NORMALS;
			else if (tex.switch_name == "SWITCH_MASKMAP2")
				type = aiTextureType_UNKNOWN;
			else if (tex.switch_name == "SWITCH_DUDVMAP")
				type = aiTextureType_UNKNOWN;
			else if (tex.switch_name == "TRANSLUCENT_MAP")
				type = aiTextureType_UNKNOWN;
			else if (tex.switch_name == "")
				type = aiTextureType_UNKNOWN;
			else {
				type = aiTextureType_UNKNOWN;
				std::cout << "Unknown switch " << tex.switch_name << std::endl;
			}

			size_t nb_tex = mat_->GetTextureCount(type);
			mat_->AddProperty(&nametex, AI_MATKEY_TEXTURE(type, nb_tex));
			aiTextureMapping mapping = aiTextureMapping_UV;
			mat_->AddProperty<int>((int*)&mapping, 1, AI_MATKEY_MAPPING(type, nb_tex));
			mat_->AddProperty<int>((int*)&channel, 1, AI_MATKEY_UVWSRC(type, nb_tex));
			channel++;
	}

	aimaterials[cnt_mat] = mat_;
	cnt_mat++;
	}

	unsigned int count_mesh = 0;
	for (auto it_msh : this->meshes) {

		
		unsigned int count_mesh_within_node = 0;
		for (auto mesh_ : it_msh.second) {


			aimeshes[count_mesh] = new aiMesh();
			
			aimeshes[count_mesh]->mMaterialIndex = mesh_.material_id;
			aimeshes[count_mesh]->mVertices = new aiVector3D[mesh_.vertices.size()];
			aimeshes[count_mesh]->mNormals = new aiVector3D[mesh_.normals.size()];
			aimeshes[count_mesh]->mTangents = new aiVector3D[mesh_.tangents.size()];

			for (size_t cnt = 0; cnt < mesh_.uvs.size(); cnt++) {
				aimeshes[count_mesh]->mNumUVComponents[cnt] = 2;
				aimeshes[count_mesh]->mTextureCoords[cnt] = new aiVector3D[mesh_.vertices.size()];
			}
			

			for (unsigned int idx_v = 0; idx_v < mesh_.vertices.size(); idx_v++)
			{
				aimeshes[count_mesh]->mVertices[idx_v].x = mesh_.vertices[idx_v].x;
				aimeshes[count_mesh]->mVertices[idx_v].y = mesh_.vertices[idx_v].y;
				aimeshes[count_mesh]->mVertices[idx_v].z = mesh_.vertices[idx_v].z;

				for (size_t idx_tex = 0; idx_tex < mesh_.uvs.size(); idx_tex++) {
					
					float x = mesh_.uvs[this->mats[mesh_.material_id].uv_map_ids[idx_tex]][idx_v].x; //here i'm not 100% sure, but there are 8 slots, and the tex slots go above 7, so I just sorted them by tex_slot (as defined in the asset config json)
					float y = mesh_.uvs[this->mats[mesh_.material_id].uv_map_ids[idx_tex]][idx_v].y;

					if (x < 0)
						x = -x;
					if (y < 0)
						y = y - floor(y);

					if (x > 1)
						x = (x - floor(x));
					if (y > 1)
						y = (y - floor(y));

					aimeshes[count_mesh]->mTextureCoords[idx_tex][idx_v].x = x;
					aimeshes[count_mesh]->mTextureCoords[idx_tex][idx_v].y = y;
					aimeshes[count_mesh]->mTextureCoords[idx_tex][idx_v].z = 0;
				}
				
			}
			for (unsigned int idx_v = 0; idx_v < mesh_.normals.size(); idx_v++)
			{
				aimeshes[count_mesh]->mNormals[idx_v].x = mesh_.normals[idx_v].x;
				aimeshes[count_mesh]->mNormals[idx_v].y = mesh_.normals[idx_v].y;
				aimeshes[count_mesh]->mNormals[idx_v].z = mesh_.normals[idx_v].z;
			}

			for (unsigned int idx_v = 0; idx_v < mesh_.tangents.size(); idx_v++)
			{
				aimeshes[count_mesh]->mTangents[idx_v].x = mesh_.tangents[idx_v].x;
				aimeshes[count_mesh]->mTangents[idx_v].y = mesh_.tangents[idx_v].y;
				aimeshes[count_mesh]->mTangents[idx_v].z = mesh_.tangents[idx_v].z;
			}

			size_t nb_faces = mesh_.faces_indexes.size();
			aiFace* faces = new aiFace[nb_faces];

			for (unsigned int idx_face = 0; idx_face < nb_faces; idx_face++)
			{

				faces[idx_face].mNumIndices = 3;
				faces[idx_face].mIndices = new unsigned[3];
				faces[idx_face].mIndices[0] = mesh_.faces_indexes[idx_face].x;
				faces[idx_face].mIndices[1] = mesh_.faces_indexes[idx_face].y;
				faces[idx_face].mIndices[2] = mesh_.faces_indexes[idx_face].z;

			}

			aiBone** aibones = new aiBone * [mesh_.bones.size()];
			size_t nb_bones = 0;

			nb_bones = mesh_.bones.size();
			unsigned int count_bones = 0;
			for (auto it_b : mesh_.bones) {
				aiBone * ptr_bone = new aiBone();
				aibones[count_bones] = ptr_bone;
				aibones[count_bones]->mNumWeights = it_b.second.weights.size();
				aibones[count_bones]->mWeights = new aiVertexWeight[aibones[count_bones]->mNumWeights]();
				if (aibones[count_bones]->mNumWeights > 0) {
					/*float maxweight = *std::max_element(it_b.second.weights.begin(), it_b.second.weights.end());
					float minweight = *std::min_element(it_b.second.weights.begin(), it_b.second.weights.end());*/

					for (unsigned int idx_w = 0; idx_w < aibones[count_bones]->mNumWeights; idx_w++) {


						aiVertexWeight weight;
						weight.mWeight = it_b.second.weights[idx_w];// / maxweight;
						weight.mVertexId = it_b.second.vertex_id[idx_w];

						if ((weight.mWeight > 1.0)) {
							//throw std::exception("invalid weight");
							weight.mWeight = 1.0;
						}
						if ((weight.mWeight < 0)) {
							weight.mWeight = 0;
						}
						aibones[count_bones]->mWeights[idx_w] = weight;
					}
				}
				
				aibones[count_bones]->mName = it_b.first;
				
				bones_ptr[aibones[count_bones]->mName.C_Str()].push_back(aibones[count_bones]);
				count_bones++;
			}

			count_mesh_within_node++;
			aimeshes[count_mesh]->mNumBones = mesh_.bones.size();
			aimeshes[count_mesh]->mBones = aibones;
			aimeshes[count_mesh]->mNumVertices = mesh_.vertices.size();
			aimeshes[count_mesh]->mNumFaces = nb_faces;
			aimeshes[count_mesh]->mFaces = faces;
			aimeshes[count_mesh]->mPrimitiveTypes = aiPrimitiveType_TRIANGLE;
			aimeshes[count_mesh]->mName = mesh_.name;

			meshes_id[mesh_.name].push_back(count_mesh);
			count_mesh++;
		}
	}

	for (unsigned int id_mesh = 0; id_mesh < real_nb_of_meshes; id_mesh++) {

		aiMesh* mesh_ptr = aimeshes[id_mesh];
		for (unsigned int bones_id = 0; bones_id < mesh_ptr->mNumBones; bones_id++)
		{
			mesh_ptr->mBones[bones_id]->mOffsetMatrix = aiMatrix4x4();
			std::string bone_name = mesh_ptr->mBones[bones_id]->mName.C_Str();
			aiNode* current_node = node_ptrs_str[bone_name];
			while (true) {
				
				mesh_ptr->mBones[bones_id]->mOffsetMatrix = current_node->mTransformation * mesh_ptr->mBones[bones_id]->mOffsetMatrix;
				current_node = current_node->mParent;
				if (current_node == NULL) {

					break;
				}


			}

			mesh_ptr->mBones[bones_id]->mOffsetMatrix = mesh_ptr->mBones[bones_id]->mOffsetMatrix.Inverse();
			aiNode* mesh_one = node_ptrs_str[mesh_ptr->mName.C_Str()];
			mesh_ptr->mBones[bones_id]->mOffsetMatrix = mesh_one->mTransformation * mesh_ptr->mBones[bones_id]->mOffsetMatrix;
			mesh_ptr->mBones[bones_id]->mOffsetMatrix = mesh_ptr->mBones[bones_id]->mOffsetMatrix.Inverse();
			aiMatrix4x4 inverse_transform = mesh_ptr->mBones[bones_id]->mOffsetMatrix;
			

		}
	}

	//animations
	
	std::vector<aiAnimation*> animations_vec = {};
	unsigned int id_ani = 0;
	if (this->anis.size() > 0) {
		aiAnimation* bind_pose_ani = new aiAnimation;

		bind_pose_ani->mName = this->bind_pose.name;
		float duration_in_seconds = (this->bind_pose.end - this->bind_pose.start);
		bind_pose_ani->mTicksPerSecond = 24;//Honestly, who cares
		bind_pose_ani->mDuration = duration_in_seconds * bind_pose_ani->mTicksPerSecond;

		aiNodeAnim** ani_nodes = new aiNodeAnim * [this->bind_pose.ani_bone_keys.size()];
		unsigned int count_bones_with_ibm = 0;
		id_ani++;
		for (auto it_nd : this->bind_pose.ani_bone_keys) {
			std::string current_bone = it_nd.first;

			if (node_ptrs_str.count(current_bone) > 0) {
				aiNode* current_node = node_ptrs_str[current_bone];

				aiNodeAnim* node_ani = new aiNodeAnim();
				bone_key_frames keys = it_nd.second;

				std::vector<aiVectorKey> position_keys;
				std::vector<aiQuatKey> rotation_keys;
				std::vector<aiVectorKey> scaling_keys;

				if (!keys.pos.empty()) {

					for (keyframe_pos key : keys.pos) {
						aiVector3D pos_key = aiVector3D(key.data.x, key.data.y, key.data.z);
						position_keys.push_back(aiVectorKey((key.time - this->bind_pose.start), pos_key));
					}

				}
				if (!keys.rot.empty()) {
					size_t id = 0;
					for (keyframe_rot key : keys.rot) {
						aiQuaternion rotation_key = aiQuaternion(key.data.t, key.data.x, key.data.y, key.data.z);
						rotation_keys.push_back(aiQuatKey((key.time - this->bind_pose.start), rotation_key));

					}

				}
				if (!keys.scl.empty()) {
					for (keyframe_scl key : keys.scl) {


						aiVector3D scaling_key = aiVector3D(key.data.x, key.data.y, key.data.z);
						scaling_keys.push_back(aiVectorKey(key.time - this->bind_pose.start, scaling_key));

					}

				}
				node_ani->mNodeName = current_bone;
				node_ani->mNumPositionKeys = position_keys.size();
				node_ani->mNumRotationKeys = rotation_keys.size();
				node_ani->mNumScalingKeys = scaling_keys.size();

				node_ani->mPositionKeys = new aiVectorKey[node_ani->mNumPositionKeys];
				node_ani->mRotationKeys = new aiQuatKey[node_ani->mNumRotationKeys];
				node_ani->mScalingKeys = new aiVectorKey[node_ani->mNumScalingKeys];

				memcpy(node_ani->mPositionKeys, position_keys.data(), node_ani->mNumPositionKeys * sizeof(aiVectorKey));
				memcpy(node_ani->mRotationKeys, rotation_keys.data(), node_ani->mNumRotationKeys * sizeof(aiQuatKey));
				memcpy(node_ani->mScalingKeys, scaling_keys.data(), node_ani->mNumScalingKeys * sizeof(aiVectorKey));


				ani_nodes[count_bones_with_ibm] = node_ani;
				count_bones_with_ibm++;
			}
		}
		if (count_bones_with_ibm > 0) {
			bind_pose_ani->mChannels = ani_nodes;
			bind_pose_ani->mNumChannels = count_bones_with_ibm;
			animations_vec.push_back(bind_pose_ani);
		}

	}

	
	for (auto ani_ : this->anis) {

		aiAnimation* ani = new aiAnimation;
		
		ani->mName = ani_.second.name;
		float duration_in_seconds = (ani_.second.end - ani_.second.start);
		ani->mTicksPerSecond = 24;//Honestly, who cares
		ani->mDuration = duration_in_seconds * ani->mTicksPerSecond;

		aiNodeAnim** ani_nodes = new aiNodeAnim * [ani_.second.ani_bone_keys.size()];

		unsigned int count_bones_with_ibm = 0;
		for (auto it_nd : ani_.second.ani_bone_keys) {
				std::string current_bone = it_nd.first;
				
				if (node_ptrs_str.count(current_bone) > 0) {
					aiNode* current_node = node_ptrs_str[current_bone];
					
					aiNodeAnim* node_ani = new aiNodeAnim();
					bone_key_frames keys = it_nd.second;

					std::vector<aiVectorKey> position_keys;
					std::vector<aiQuatKey> rotation_keys;
					std::vector<aiVectorKey> scaling_keys;



					if (!keys.pos.empty()) {

						for (keyframe_pos key : keys.pos) {
							aiVector3D pos_key = aiVector3D(key.data.x, key.data.y, key.data.z);
							position_keys.push_back(aiVectorKey((key.time - ani_.second.start), pos_key));
						}

					}
					if (!keys.rot.empty()) {
						size_t id = 0;
						for (keyframe_rot key : keys.rot) {
							aiQuaternion rotation_key = aiQuaternion(key.data.t, key.data.x, key.data.y, key.data.z);
							rotation_keys.push_back(aiQuatKey((key.time - ani_.second.start), rotation_key));
							
						}

					}
					if (!keys.scl.empty()) {
						for (keyframe_scl key : keys.scl) {

					
							aiVector3D scaling_key = aiVector3D(key.data.x, key.data.y, key.data.z);
							scaling_keys.push_back(aiVectorKey(key.time - ani_.second.start, scaling_key));

						}

					}
					node_ani->mNodeName = current_bone;
					node_ani->mNumPositionKeys = position_keys.size();
					node_ani->mNumRotationKeys = rotation_keys.size();
					node_ani->mNumScalingKeys = scaling_keys.size();

					node_ani->mPositionKeys = new aiVectorKey[node_ani->mNumPositionKeys];
					node_ani->mRotationKeys = new aiQuatKey[node_ani->mNumRotationKeys];
					node_ani->mScalingKeys = new aiVectorKey[node_ani->mNumScalingKeys];

					memcpy(node_ani->mPositionKeys, position_keys.data(), node_ani->mNumPositionKeys * sizeof(aiVectorKey));
					memcpy(node_ani->mRotationKeys, rotation_keys.data(), node_ani->mNumRotationKeys * sizeof(aiQuatKey));
					memcpy(node_ani->mScalingKeys, scaling_keys.data(), node_ani->mNumScalingKeys * sizeof(aiVectorKey));


					ani_nodes[count_bones_with_ibm] = node_ani;
					count_bones_with_ibm++;
				}
			}
		if (count_bones_with_ibm > 0) {
			ani->mChannels = ani_nodes;
			ani->mNumChannels = count_bones_with_ibm;
			animations_vec.push_back(ani);
			id_ani++;
		}
	}
	aiAnimation** animations = new aiAnimation * [animations_vec.size()];
	memcpy(animations, animations_vec.data(), animations_vec.size() * sizeof(aiAnimation*));

	idx_node = 0;
	
	for (auto it_m : meshes_id) {
		if (node_ptrs_str.count(it_m.first) > 0) {
			node_ptrs_str[it_m.first]->mNumMeshes = it_m.second.size();
			node_ptrs_str[it_m.first]->mMeshes = new unsigned int[it_m.second.size()];
			for (size_t i = 0; i < it_m.second.size(); i++)
				node_ptrs_str[it_m.first]->mMeshes[i] = it_m.second[i];
		}
		else {
			throw std::exception("for some reason the meshes names don't match the node names"); //I don't know if it's important for the game

		}
	}

	
	

	

	aiScene* out = new aiScene();

	out->mMaterials = aimaterials;
	out->mNumMaterials = cnt_mat;

	out->mNumMeshes = real_nb_of_meshes;
	out->mMeshes = aimeshes;
	
	out->mRootNode = rootNode;
	out->mMetaData = new aiMetadata();

	
	out->mAnimations = animations;
	out->mNumAnimations = animations_vec.size();

	Assimp::Exporter exporter;
	
	std::cout << "Writing " << this->name + ".fbx" << std::endl;

	unsigned int PreProcessingFlags = aiProcess_JoinIdenticalVertices;// | aiProcess_OptimizeMeshes | aiProcess_OptimizeGraph;
	if (conf.bone_limit_per_mesh != -1) {
		//Something made for CS4 that didn't seem to work well 
		#define AI_SBBC_DEFAULT_MAX_BONES conf.bone_limit_per_mesh;
		PreProcessingFlags |= aiProcess_SplitByBoneCount;
	}
	exporter.Export(out, "fbx", this->name + ".fbx", PreProcessingFlags); // aiProcess_CalcTangentSpace

	delete out;


}


aiNode* find_rig_node(aiNode* current_node, std::set<std::string> bones_) {

	if (current_node == NULL) return NULL;
	else {
		if (bones_.count(current_node->mName.C_Str()) > 0) {
			return current_node->mParent;
		}
		else {

			for (unsigned int children_id = 0; children_id < current_node->mNumChildren; children_id++) {
				aiNode* top = find_rig_node(current_node->mChildren[children_id], bones_);
				if (top != NULL)
					return top;

			}
		}

		
	}
	return NULL;
}


bool create_node_map(tsl::ordered_map<std::string, node>& map, std::unordered_set<aiNode*> &node_list, aiNode* current_node, unsigned int &id, unsigned int parent) {
	if (current_node == NULL) return true;
	else {
		node_list.emplace(current_node);
		node nd;
		nd.id = id;
		nd.parent = parent;
		
		nd.name = current_node->mName.C_Str();
		if (current_node->mParent != NULL) {
			if (nd.name.compare(current_node->mParent->mName.C_Str()) == 0) {
				current_node = NULL; //I think we only need one node for all meshes of the same name
				return false;
			}
		
		}
		
		//current_node->mTransformation.Transpose();
		nd.transform.a = { current_node->mTransformation.a1, current_node->mTransformation.a2, current_node->mTransformation.a3, current_node->mTransformation.a4 };
		nd.transform.b = { current_node->mTransformation.b1, current_node->mTransformation.b2, current_node->mTransformation.b3, current_node->mTransformation.b4 };
		nd.transform.c = { current_node->mTransformation.c1, current_node->mTransformation.c2, current_node->mTransformation.c3, current_node->mTransformation.c4 };
		nd.transform.d = { current_node->mTransformation.d1, current_node->mTransformation.d2, current_node->mTransformation.d3, current_node->mTransformation.d4 };
		
		//std::cout << nd.name << std::endl;
		
		vec3<float> scl;
		vec3<float> pos;
		vec3<float> rot;
		current_node->mTransformation.Transpose();
		//c'est le bordel mais je cherche
		matrix4<float> transposed;
		transposed.a = { current_node->mTransformation.a1, current_node->mTransformation.a2, current_node->mTransformation.a3, current_node->mTransformation.a4 };
		transposed.b = { current_node->mTransformation.b1, current_node->mTransformation.b2, current_node->mTransformation.b3, current_node->mTransformation.b4 };
		transposed.c = { current_node->mTransformation.c1, current_node->mTransformation.c2, current_node->mTransformation.c3, current_node->mTransformation.c4 };
		transposed.d = { current_node->mTransformation.d1, current_node->mTransformation.d2, current_node->mTransformation.d3, current_node->mTransformation.d4 };

		nd.transform.decompose(nd.T, nd.R, nd.S); 

	
		map[nd.name] = nd;
		for (unsigned int children_id = 0; children_id < current_node->mNumChildren; children_id++) {
			std::string children_name = current_node->mChildren[children_id]->mName.C_Str();
			/*unsigned int index = children_name.find_last_of(children_name);
			if (index != -1) {
				std::string substr = children_name.substr(0, index - 1);
				if (substr.compare("chr0000_body9") == 0) {
				}
				else {
					map[nd.name].children.push_back(++id);
					bool success = create_node_map(map, current_node->mChildren[children_id], id, nd.id);
					if (!success) {
						map[nd.name].children.pop_back();
						id--;

					}
				
				
				
				}


			}
			else {*/
				map[nd.name].children.push_back(++id);
				bool success = create_node_map(map, node_list, current_node->mChildren[children_id], id, nd.id);
				if (!success) {
					map[nd.name].children.pop_back();
					id--;
			
				}
			//}
		}
		
	}

}
void model::to_json() {

//parse the default layouts json
	std::ifstream f("default_layouts.json");
	ordered_json default_layouts = ordered_json::parse(f);
	ordered_json result;

	std::vector<std::pair<std::string, std::vector<tex>>> list_of_materials;
	for (auto mat : this->mats){
		list_of_materials.push_back(std::make_pair(mat.second.name, mat.second.tex_data));
	}
	
	
	for (std::pair<std::string, std::vector<tex>> item : list_of_materials) {
		if (default_layouts.count(item.first) > 0) {
			result[item.first] = default_layouts[item.first];
		}
		else
			result[item.first]["status"] = "Missing from the default layout json, to be filled manually";

		for (auto tex : item.second) {

			int index = tex.name.find_last_of(".");
			if (index != -1)
				tex.name = tex.name.substr(0, index);
			tex.name = tex.name.substr(tex.name.find_last_of("/\\") + 1);
			result[item.first]["texture maps"][tex.switch_name]["texture"] = tex.name;
			result[item.first]["texture maps"][tex.switch_name]["uv map index"] = tex.uv;
			

		}
		//My understanding is that setting some of the switches will activate/desactivate a set of parameters (in the first list); 
		//I can't possibly link all the switches to which parameters so we will set dummy textures in the default_layout
		for (auto param_it = result[item.first]["switches"].cbegin(); param_it != result[item.first]["switches"].cend(); param_it++) {
			{
				int current_val = param_it.value();
				std::string switch_name = param_it.key();
				/*if (all_possible_texture_maps_switches.count(param_it.key()) > 0) //if it's a texture map switch
				{
					if (used_texture_maps.count(param_it.key()) == 0) { //if no texture is assigned, we disable it otherwise it will crash?
						result[item.first]["Switches"].erase(param_it);
					}
					else {
						
						result[item.first]["Switches"][switch_name] = current_val;
						param_it++;
					}
				}
				else {
					result[item.first]["Switches"][switch_name] = current_val;
					
				param_it++
				}*/
				result[item.first]["switches"][switch_name] = current_val;
			}
		}
		
	}
	f.close();

	std::ofstream o(this->name + ".json");
	o << std::setw(4) << result << std::endl;
	o.close();




}


bounding_box get_bounding_box(std::vector<mesh> meshes) {

	bounding_box result = { 0,0,0,0,0,0 };
	bool init = false;
	for (auto m : meshes) {
		for (auto vert : m.vertices) {

			if (!init) {
				result.min.x = vert.x;
				result.min.y = vert.y;
				result.min.z = vert.z;
				result.max.x = vert.x;
				result.max.y = vert.y;
				result.max.z = vert.z;
				init = true;
			}
			else {
				if (vert.x < result.min.x) {
					result.min.x = vert.x;
				}
				if (vert.y < result.min.y) {
					result.min.y = vert.y;
				}
				if (vert.z < result.min.z) {
					result.min.z = vert.z;
				}

				if (vert.x > result.max.x) {
					result.max.x = vert.x;
				}
				if (vert.y > result.max.y) {
					result.max.y = vert.y;
				}
				if (vert.z > result.max.z) {
					result.max.z = vert.z;
				}
			}
		}

	}
	return result;
}

template <typename T, typename Compare>
std::vector<std::size_t> sort_permutation(
	const std::vector<T>& vec,
	Compare compare)
{
	std::vector<std::size_t> p(vec.size());
	std::iota(p.begin(), p.end(), 0);
	std::sort(p.begin(), p.end(),
		[&](std::size_t i, std::size_t j) { return compare(vec[i], vec[j]); });
	return p;
}

template <typename T>
std::vector<T> apply_permutation(
	const std::vector<T>& vec,
	const std::vector<std::size_t>& p)
{
	std::vector<T> sorted_vec(vec.size());
	std::transform(p.begin(), p.end(), sorted_vec.begin(),
		[&](std::size_t i) { return vec[i]; });
	return sorted_vec;
}

template <typename T>
void apply_permutation_in_place(
	std::vector<T>& vec,
	const std::vector<std::size_t>& p)
{
	std::vector<bool> done(vec.size());
	for (std::size_t i = 0; i < vec.size(); ++i)
	{
		if (done[i])
		{
			continue;
		}
		done[i] = true;
		std::size_t prev_j = i;
		std::size_t j = p[i];
		while (i != j)
		{
			std::swap(vec[prev_j], vec[j]);
			done[j] = true;
			prev_j = j;
			j = p[j];
		}
	}
}


void model::to_mdl(AssetConfig config) {
	ordered_json j;
	//Parse the corresponding json
	std::ifstream f(this->name + ".json");
	if (f.is_open()) {
	
		j = ordered_json::parse(f);
		f.close();
	}
	else {
		f.close();
		std::ifstream g("default_layouts.json");
		if (!g.is_open())
			throw std::exception("You need at least 1 json file to specify the material parameters values!");
		j = ordered_json::parse(g);
		g.close();
	}

	//depending on the values in "meshes", will remove the nodes in excess and rename the meshes accordingly
	//for (auto nd = )

	//We can write the mdl
	std::vector<uint8_t> start = { 0x4D, 0x44, 0x4C, 0x20, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
	std::vector<uint8_t> first_section = {};
	std::vector<uint8_t> second_section = {};
	std::vector<uint8_t> third_section = {};
	uint32_t u32;
	add_bytes(first_section, (uint32_t)this->mats.size());
	for (auto mat : this->mats) {
		std::vector<uint8_t> mat_name = std::vector<uint8_t>(mat.second.name.begin(), mat.second.name.end());
		uint8_t byte_size = (mat_name.size());
		add_bytes(first_section, byte_size);
		first_section.insert(first_section.end(), mat_name.begin(), mat_name.begin() + mat_name.size());
		auto it = j[mat.second.name].items().begin();
		if ((j[mat.second.name].count("status") > 0) || (it == j[mat.second.name].items().end())) {
			
			std::string error = "No shader for this material " + mat.second.name + ", please add one";
			throw std::exception(error.c_str());
		}
		else {

			std::string str_shader = it.key();
			mat.second.shader_name = str_shader;
			std::vector<uint8_t> shader_name = std::vector<uint8_t>(str_shader.begin(), str_shader.end());

			byte_size = (shader_name.size());
			add_bytes(first_section, byte_size);
			first_section.insert(first_section.end(), shader_name.begin(), shader_name.begin() + shader_name.size());
			add_bytes(first_section, byte_size);
			first_section.insert(first_section.end(), shader_name.begin(), shader_name.begin() + shader_name.size());

			std::unordered_set<std::string> enabled_texture_maps = {};
			uint32_t nb_texture = 0;
			//on oublie tex_data et on prend ce qui est dans le json
			if (j[mat.second.name].count("texture maps") > 0) {
				mat.second.uv_map_ids.clear();
				mat.second.tex_data.clear();
				nb_texture = j[mat.second.name]["texture maps"].size();
				
				for (auto texture : j[mat.second.name]["texture maps"].items()) {
					
					tex t = { texture.value()["texture"], texture.key(), config.reverse_map_ids[mat.second.shader_name][texture.key()], texture.value()["uv map index"] };
					mat.second.tex_data.push_back(t);
				}
				std::sort(mat.second.tex_data.begin(), mat.second.tex_data.end());


			}
			add_bytes(first_section, (uint32_t)mat.second.tex_data.size());
			
			for (auto texture : mat.second.tex_data) {
				enabled_texture_maps.emplace(texture.switch_name);
				std::vector<uint8_t> tex_name = std::vector<uint8_t>(texture.name.begin(), texture.name.end());
				byte_size = (texture.name.size());
				add_bytes(first_section, byte_size);
				first_section.insert(first_section.end(), tex_name.begin(), tex_name.begin() + tex_name.size());
				add_bytes(first_section, texture.tex_slot);
				add_bytes(first_section, 1);
				add_bytes(first_section, 0);
			}
			
			add_bytes(first_section, (int32_t) j[mat.second.name][str_shader].size());
			for (auto param_it = j[mat.second.name][str_shader].items().begin(); param_it != j[mat.second.name][str_shader].items().end(); param_it++) {
				std::vector<uint8_t> param_name = std::vector<uint8_t>(param_it.key().begin(), param_it.key().end());
				byte_size = (param_it.key().size());
				add_bytes(first_section, byte_size);
				first_section.insert(first_section.end(), param_name.begin(), param_name.begin() + param_name.size());

				std::vector<float> values = {};
				std::string current_val = param_it.value();
				int index = current_val.find_last_of("[");
				int nb_values = 0;
				if (index == -1) {
					values.push_back(std::stof(current_val));
					nb_values++;
				}
				else {
					current_val = current_val.substr(index + 1);
					index = current_val.find_first_of(",");

					while (index != -1) {
						values.push_back(std::stof(current_val.substr(0, index - 1)));
						current_val = current_val.substr(index + 1);
						index = current_val.find_last_of(",");
						nb_values++;
					}
					int index_close = current_val.find_last_of("]");
					values.push_back(std::stof(current_val.substr(0, index_close - 1)));
					nb_values++;
				}
				//Idk how to distinguish the 0, 1, and 4 types yet (didn't really check them) I'll assume they're all of 0 type for the moment
				int type = 0;
				switch (nb_values) {
				case 1:
					type = 0;
					break;
				case 2:
					type = 2;
					break;
				case 3:
					type = 3;
					break;
				case 4:
					type = 7;
					break;
				case 16:
					type = 8;
					break;
				}

				add_bytes(first_section, type);

				for (auto v : values) {
					add_bytes(first_section, v);
				}

			}
			add_bytes(first_section, (uint32_t)j[mat.second.name]["switches"].size()); //I think this number is fixed for a material or shader but you can dedice to toggle them (-1 = on, 0 = off?)
			for (auto param_it = j[mat.second.name]["switches"].items().begin(); param_it != j[mat.second.name]["switches"].items().end(); param_it++) {
				
				std::vector<uint8_t> switch_name = std::vector<uint8_t>(param_it.key().begin(), param_it.key().end());
				
				
				int current_val = param_it.value();
				
				byte_size = (param_it.key().size());
				add_bytes(first_section, byte_size);
				first_section.insert(first_section.end(), switch_name.begin(), switch_name.begin() + switch_name.size());
				add_bytes(first_section, current_val);
				
				
			}
			add_bytes(first_section, 8);
			uint8_t uv_channel;
			for (unsigned int uv_idx = 0; uv_idx < 8; uv_idx++) {
				if (uv_idx < mat.second.uv_map_ids.size()) {
					uv_channel = mat.second.uv_map_ids[uv_idx];

				}
				else
					uv_channel = 0;
				add_bytes(first_section, uv_channel);
			}
			//no idea what that is
			add_bytes(first_section, 2);
			uint8_t byte = 0;
			add_bytes(first_section, byte);
			add_bytes(first_section, byte);
			//same
			uint32_t a = 0, b = 0, c = 0, e = 0;
			float d = 0;
			if (j[mat.second.name].count("unknown values") > 0) {
				int str = j[mat.second.name]["unknown values"]["a"];
				a = str;
				str = j[mat.second.name]["unknown values"]["b"];
				b = str;
				str = j[mat.second.name]["unknown values"]["c"];
				c = str;
				float f = j[mat.second.name]["unknown values"]["d"];
				d = f;
				str = j[mat.second.name]["unknown values"]["e"];
				e = str;
			}
			add_bytes(first_section, a);
			add_bytes(first_section, b);
			add_bytes(first_section, c);
			add_bytes(first_section, d);
			add_bytes(first_section, e);



		}
	}
	add_bytes_front(first_section, (uint32_t)first_section.size());
	
	//starting geometry section
	add_bytes(first_section, 1);
	add_bytes(second_section, (uint32_t)this->meshes.size());
	uint8_t byte_size;
	std::set<std::string> bones_names = {};
	for (auto it = this->meshes.begin(); it != this->meshes.end(); it++) {
		auto mesh = *it;
		unsigned int mesh_cnt = 0;
		std::vector<uint8_t> mesh_name = std::vector<uint8_t>(mesh.first.begin(), mesh.first.end());
		byte_size = (mesh.first.size());
		add_bytes(second_section, byte_size);
		second_section.insert(second_section.end(), mesh_name.begin(), mesh_name.begin() + mesh_name.size());

		std::vector<uint8_t> individual_meshes = {};
		add_bytes(individual_meshes, (uint32_t)mesh.second.size());
		

		for (auto m : mesh.second) {
			//on va sérialiser les "mesh_attributes"
			add_bytes(individual_meshes, (uint32_t)m.material_id);
			size_t nb_streams = 11 + (m.bones.size() > 0) * 4 + (m.tangents.size() > 0);
			if (m.bones.size() == 0)
				std::cout << "WARNING! Your mesh " << mesh.first << " doesn't have bones! It might not show up in game for this reason. Please add an armature to the mesh if necessary." << std::endl;
			add_bytes(individual_meshes, (uint32_t) nb_streams);
			//les mesh data streams sont ordonnés comme ça : 
			//id, size, type, et la data
			//avec type = 12 pour les vertices, 4 pour les faces, 8 pour les uvs, 16 pour les poids
			//plus spécifiquement id = 0 pour les vertices, 1 pour les normales, 2 pour les tangentes, 
			//5 pour les poids et 6 pour les id des bones
			std::vector<uint8_t> vertices_stream = {};
			add_bytes(vertices_stream, 12);
			for (auto v : m.vertices) {
				add_bytes(vertices_stream, v.x);
				add_bytes(vertices_stream, v.y);
				add_bytes(vertices_stream, v.z);
			}
			add_bytes_front(vertices_stream, (uint32_t) (vertices_stream.size() -4));
			add_bytes_front(vertices_stream, 0);

			std::vector<uint8_t> normals_stream = {};
			add_bytes(normals_stream, 12);
			for (auto v : m.normals) {
				add_bytes(normals_stream, v.x);
				add_bytes(normals_stream, v.y);
				add_bytes(normals_stream, v.z);
			}
			add_bytes_front(normals_stream, (uint32_t)(normals_stream.size()-4));
			add_bytes_front(normals_stream, 1);
			std::vector<uint8_t> tangents_stream = {};
			if (m.tangents.size() > 0){
				add_bytes(tangents_stream, 12);
				for (auto v : m.tangents) {
					add_bytes(tangents_stream, v.x);
					add_bytes(tangents_stream, v.y);
					add_bytes(tangents_stream, v.z);
				}
				add_bytes_front(tangents_stream, (uint32_t)(tangents_stream.size()-4));
				add_bytes_front(tangents_stream, 2);
			}


			std::vector<uint8_t> uv_streams = {};
			
			std::vector<vec2<float>> current_uv;
			for (unsigned int uv_id = 0; uv_id < 8; uv_id++) {
				std::vector<uint8_t> single_uv = {};
				
				add_bytes(single_uv, 8);
				if (uv_id < m.uvs.size()) {
					current_uv = m.uvs[uv_id];
				}
				for (auto uv : current_uv) {
					add_bytes(single_uv, uv.x);
					add_bytes(single_uv, uv.y);

				}
				add_bytes_front(single_uv, (uint32_t)(single_uv.size() - 4));
				add_bytes_front(single_uv, 4);
				uv_streams.insert(uv_streams.end(), single_uv.begin(), single_uv.end());
			}
			
			std::vector<uint8_t> bones_stream1 = {};
			if (m.bones.size() > 0){
				add_bytes(bones_stream1, 16);
				for (auto v : m.vertices) {
					add_bytes(bones_stream1, 0);
					add_bytes(bones_stream1, 0);
					add_bytes(bones_stream1, 0);
					add_bytes(bones_stream1, 0);
				}
				add_bytes_front(bones_stream1, (uint32_t)(bones_stream1.size() - 4));
				add_bytes_front(bones_stream1, 3);
			}
			std::vector<uint8_t> bones_stream2 = {};
			if (m.bones.size() > 0) {
				add_bytes(bones_stream2, 16);
				for (auto v : m.vertices) {
					add_bytes(bones_stream2, 0);
					add_bytes(bones_stream2, 0);
					add_bytes(bones_stream2, 0);
					add_bytes(bones_stream2, 0);
				}
				add_bytes_front(bones_stream2, (uint32_t)(bones_stream2.size() - 4));
				add_bytes_front(bones_stream2, 3);
			}

			std::vector<uint8_t> weights_u8_vec = {};
			std::vector<uint8_t> bones_u8_vec = {};
			
			

			if (m.bones.size() > 0) {
				
				std::vector<std::string> adeleteapres = {};
				for (auto b : m.bones) {
					adeleteapres.push_back(b.first);
				
				}

				std::vector < std::vector<float>> weights_ = std::vector<std::vector<float>>(m.vertices.size());;
				std::vector < std::vector<unsigned int>> bones_ids_ = std::vector<std::vector<unsigned int>>(m.vertices.size());;;
				std::vector<float> weights_stream = std::vector<float>(4 * m.vertices.size());
				std::fill(weights_stream.begin(), weights_stream.end(), 0);
				std::vector<unsigned int> bones_stream = std::vector<unsigned int>(4 * m.vertices.size());;
				std::fill(bones_stream.begin(), bones_stream.end(), 0);
				unsigned int bone_id = 0;
				for (auto b : m.bones) {
					
					
					bones_names.emplace(b.second.name);
					for (unsigned int vertice = 0; vertice < b.second.vertex_id.size(); vertice++) {
						float w = b.second.weights[vertice];
						if (w > 1)
							w = 1;
						if (w < 0)
							w = 0;
						if (weights_[b.second.vertex_id[vertice]].size() < 4) {
							weights_[b.second.vertex_id[vertice]].push_back(w);
							bones_ids_[b.second.vertex_id[vertice]].push_back(bone_id);

						}
						else {
							auto itmin = std::min_element(weights_[b.second.vertex_id[vertice]].begin(), weights_[b.second.vertex_id[vertice]].end());
							if (*itmin < w) {
								*itmin = w;
								bones_ids_[b.second.vertex_id[vertice]][itmin - weights_[b.second.vertex_id[vertice]].begin()] = bone_id;

							}
						}


					}
					
					bone_id++;
				}
				
				for (unsigned int i_v = 0; i_v < weights_.size(); i_v++) {
					//I thought it was necessary the weights were sorted but nope :)
					auto p = sort_permutation(weights_[i_v],
						[](float const& a, float const& b) { return a > b; });

					weights_[i_v] = apply_permutation(weights_[i_v], p);
					bones_ids_[i_v] = apply_permutation(bones_ids_[i_v], p);
					
					//If tbe sum of the weights is not equal to 1, the vertex will not display; but if it's equal to 1 there is no guarantee it will display for some reason either
					for (unsigned int w = 0; w < weights_[i_v].size(); w++) {
						
						

						memcpy(&weights_stream[4 * i_v + w], &weights_[i_v][w], sizeof(float));
						memcpy(&bones_stream[4 * i_v + w], &bones_ids_[i_v][w], sizeof(float));
					
					}
				}
				
				uint8_t* weights_u8 = reinterpret_cast<uint8_t*>(weights_stream.data());
				weights_u8_vec = std::vector<uint8_t>(weights_u8, weights_u8 + weights_stream.size() * 4);
				add_bytes_front(weights_u8_vec, 16);
				add_bytes_front(weights_u8_vec, (uint32_t)(weights_u8_vec.size() - 4));
				add_bytes_front(weights_u8_vec, 5);
			

				uint8_t* bones_u8 = reinterpret_cast<uint8_t*>(bones_stream.data());
				bones_u8_vec = std::vector<uint8_t>(bones_u8, bones_u8 + bones_stream.size() * 4);
				add_bytes_front(bones_u8_vec, 16);
				add_bytes_front(bones_u8_vec, (uint32_t)(bones_u8_vec.size() - 4));
				add_bytes_front(bones_u8_vec, 6);
			}
			std::vector<uint8_t> faces_stream = {};
			add_bytes(faces_stream, 4);
			for (auto f : m.faces_indexes) {
				add_bytes(faces_stream, f.x);
				add_bytes(faces_stream, f.y);
				add_bytes(faces_stream, f.z);
			}
			add_bytes_front(faces_stream, (uint32_t)(faces_stream.size() - 4));
			add_bytes_front(faces_stream, 7);
			


			individual_meshes.insert(individual_meshes.end(), vertices_stream.begin(), vertices_stream.end());
			individual_meshes.insert(individual_meshes.end(), normals_stream.begin(), normals_stream.end());
			individual_meshes.insert(individual_meshes.end(), tangents_stream.begin(), tangents_stream.end());
			individual_meshes.insert(individual_meshes.end(), uv_streams.begin(), uv_streams.end());
			individual_meshes.insert(individual_meshes.end(), bones_stream1.begin(), bones_stream1.end());
			individual_meshes.insert(individual_meshes.end(), bones_stream2.begin(), bones_stream2.end());
			individual_meshes.insert(individual_meshes.end(), weights_u8_vec.begin(), weights_u8_vec.end());
			individual_meshes.insert(individual_meshes.end(), bones_u8_vec.begin(), bones_u8_vec.end());
			individual_meshes.insert(individual_meshes.end(), faces_stream.begin(), faces_stream.end());

			
			mesh_cnt++;
		}
		

		add_bytes(individual_meshes, (uint32_t)mesh.second[0].bones.size());
		for (auto bone : mesh.second[0].bones) { 

			std::vector<uint8_t> bone_name = std::vector<uint8_t>(bone.first.begin(), bone.first.end());
			byte_size = (bone.first.size());
			add_bytes(individual_meshes, byte_size);
			individual_meshes.insert(individual_meshes.end(), bone_name.begin(), bone_name.begin() + bone_name.size());
			
			std::vector<uint8_t> vec_mat = serialize_matrix44(bone.second.offsetmatrix);
			
			individual_meshes.insert(individual_meshes.end(), vec_mat.begin(), vec_mat.end());
		}
		add_bytes_front(individual_meshes, (uint32_t)(individual_meshes.size()));
		add_bytes(individual_meshes, 0x2C); 
		bounding_box bb = get_bounding_box(mesh.second);
		add_bytes(individual_meshes, bb.min.x);
		add_bytes(individual_meshes, bb.min.y);
		add_bytes(individual_meshes, bb.min.z);
		add_bytes(individual_meshes, 0);
		add_bytes(individual_meshes, bb.max.x);
		add_bytes(individual_meshes, bb.max.y);
		add_bytes(individual_meshes, bb.max.z);
		add_bytes(individual_meshes, 0);
		add_bytes(individual_meshes, 0);
		add_bytes(individual_meshes, 0);
		add_bytes(individual_meshes, 0);
		
		second_section.insert(second_section.end(), individual_meshes.begin(), individual_meshes.end());
		
	}
	add_bytes_front(second_section, (uint32_t)(second_section.size()));
	add_bytes(second_section, 2);
	//final section in a regular mdl
	add_bytes(third_section, (uint32_t) this->nodes.size());
	for (auto node : this->nodes) {
		//add_bytes(third_section, node.second.id);

		std::vector<uint8_t> node_name = std::vector<uint8_t>(node.first.begin(), node.first.end());
		byte_size = (node.first.size());
		add_bytes(third_section, byte_size);
		third_section.insert(third_section.end(), node_name.begin(), node_name.begin() + node_name.size());
		
		uint32_t nodetype = 0;
		if (this->meshes.count(node.first) > 0)//if it's a mesh, basically
			nodetype = 2;
		else if (bones_names.count(node.first) > 0) //if it's a bone
			nodetype = 1;
		//else it's a locator
		add_bytes(third_section, nodetype); //FFS!!!
		unsigned int mesh_id = -1;
		if (nodetype == 2) {
			mesh_id = distance(this->meshes.begin(), this->meshes.find(node.first));
		}
		add_bytes(third_section, mesh_id);
		add_bytes(third_section, node.second.T);
		add_bytes(third_section, vec4<float>({ 0,0,0,1 })); //no idea what that is!!!
		add_bytes(third_section, 0);
		add_bytes(third_section, node.second.R);
		add_bytes(third_section, node.second.S);
		
		add_bytes(third_section, vec3<float>({ 0,0,0})); //no idea what that is!!!
		add_bytes(third_section, (uint32_t)node.second.children.size());
		for (auto child_id : node.second.children) {
			add_bytes(third_section, child_id);
		}
	}
	add_bytes_front(third_section, (uint32_t)(third_section.size()));


	std::vector<uint8_t> full_content = {};
	full_content.insert(full_content.end(), start.begin(), start.end());
	full_content.insert(full_content.end(), first_section.begin(), first_section.end());
	full_content.insert(full_content.end(), second_section.begin(), second_section.end());
	full_content.insert(full_content.end(), third_section.begin(), third_section.end());
	add_bytes(full_content, -1);

	std::ofstream fout(this->name + ".mdl", std::ios::out | std::ios::binary);
	fout.write((char*)&full_content[0], full_content.size() * 1);
	fout.close();
	//Are there animations?

	for (auto ani : this->anis) {
		std::vector<uint8_t> ani_bytes = { 0x4D, 0x44, 0x4C, 0x20, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00 };
		ani_bytes.insert(ani_bytes.end(), third_section.begin(), third_section.end());
		std::vector<uint8_t> anim_section = {};
		size_t count = 0;
		for (auto ani_bone_data : ani.second.ani_bone_keys) {
			std::string bone_name = ani_bone_data.first;
			//translate
			if (ani_bone_data.second.pos.size() > 0) {
				count++;
				std::string component = bone_name + "_translate";
				std::vector<uint8_t> bytes = std::vector<uint8_t>(component.begin(), component.end());
				byte_size = (component.size());
				add_bytes(anim_section, byte_size);
				anim_section.insert(anim_section.end(), bytes.begin(), bytes.begin() + bytes.size());
				bytes = std::vector<uint8_t>(bone_name.begin(), bone_name.end());
				byte_size = (bone_name.size());
				add_bytes(anim_section, byte_size);
				anim_section.insert(anim_section.end(), bone_name.begin(), bone_name.begin() + bone_name.size());
				add_bytes(anim_section, 0x09);
				add_bytes(anim_section, 0x0);
				add_bytes(anim_section, 0x0);
				add_bytes(anim_section, (uint32_t) ani_bone_data.second.pos.size());
				//pos = 0x09, rot = 0x0A, scale = 0x0B, scrollUV = 0x0D, no_actual_idea = 0x0C};
				for (auto k : ani_bone_data.second.pos) {
					add_bytes(anim_section, k.time);
					add_bytes(anim_section, k.data.x);
					add_bytes(anim_section, k.data.y);
					add_bytes(anim_section, k.data.z);
					add_bytes(anim_section, 0x0);
					add_bytes(anim_section, 0x0);
					add_bytes(anim_section, 0x0);
					add_bytes(anim_section, 0x0);
					add_bytes(anim_section, 0x0);
				
				}
				
			
			}
			//rotate
			if (ani_bone_data.second.rot.size() > 0) {
				count++;
				std::string component = bone_name + "_rotate";
				std::vector<uint8_t> bytes = std::vector<uint8_t>(component.begin(), component.end());
				byte_size = (component.size());
				add_bytes(anim_section, byte_size);
				anim_section.insert(anim_section.end(), bytes.begin(), bytes.begin() + bytes.size());
				bytes = std::vector<uint8_t>(bone_name.begin(), bone_name.end());
				byte_size = (bone_name.size());
				add_bytes(anim_section, byte_size);
				anim_section.insert(anim_section.end(), bone_name.begin(), bone_name.begin() + bone_name.size());
				add_bytes(anim_section, 0x0A);
				add_bytes(anim_section, 0x0);
				add_bytes(anim_section, 0x0);
				add_bytes(anim_section, (uint32_t)ani_bone_data.second.rot.size());
				//pos = 0x09, rot = 0x0A, scale = 0x0B, scrollUV = 0x0D, no_actual_idea = 0x0C};
				for (auto k : ani_bone_data.second.rot) {
					add_bytes(anim_section, k.time);
					add_bytes(anim_section, k.data.x);
					add_bytes(anim_section, k.data.y);
					add_bytes(anim_section, k.data.z);
					add_bytes(anim_section, k.data.t);
					add_bytes(anim_section, 0x0);
					add_bytes(anim_section, 0x0);
					add_bytes(anim_section, 0x0);
					add_bytes(anim_section, 0x0);
					add_bytes(anim_section, 0x0);
				}
				

			}
			//scaling
			if (ani_bone_data.second.scl.size() > 0) {
				count++;
				std::string component = bone_name + "_scale";
				std::vector<uint8_t> bytes = std::vector<uint8_t>(component.begin(), component.end());
				byte_size = (component.size());
				add_bytes(anim_section, byte_size);
				anim_section.insert(anim_section.end(), bytes.begin(), bytes.begin() + bytes.size());
				bytes = std::vector<uint8_t>(bone_name.begin(), bone_name.end());
				byte_size = (bone_name.size());
				add_bytes(anim_section, byte_size);
				anim_section.insert(anim_section.end(), bone_name.begin(), bone_name.begin() + bone_name.size());
				add_bytes(anim_section, 0x0B);
				add_bytes(anim_section, 0x0);
				add_bytes(anim_section, 0x0);
				add_bytes(anim_section, (uint32_t)ani_bone_data.second.scl.size());
				//pos = 0x09, rot = 0x0A, scale = 0x0B, scrollUV = 0x0D, no_actual_idea = 0x0C};
				for (auto k : ani_bone_data.second.scl) {
					add_bytes(anim_section, k.time);
					add_bytes(anim_section, k.data.x);
					add_bytes(anim_section, k.data.y);
					add_bytes(anim_section, k.data.z);
					add_bytes(anim_section, 0x0);
					add_bytes(anim_section, 0x0);
					add_bytes(anim_section, 0x0);
					add_bytes(anim_section, 0x0);
					add_bytes(anim_section, 0x0);
				}

			}
		
		}
		add_bytes(anim_section, ani.second.start);
		add_bytes(anim_section, ani.second.end);
		add_bytes_front(anim_section, (uint32_t)(count));
		add_bytes_front(anim_section, (uint32_t)(anim_section.size()));
		add_bytes_front(anim_section, 3);
		add_bytes(anim_section, 0xFFFFFFFF);
		ani_bytes.insert(ani_bytes.end(), anim_section.begin(), anim_section.end());
		std::cout << "Writing ani mdl: " << ani.first << ".mdl" << std::endl;
		std::ofstream fout(ani.first + ".mdl", std::ios::out | std::ios::binary);
		fout.write((char*)&ani_bytes[0], ani_bytes.size() * 1);
		fout.close();
	}


}

model::model(std::string fbx_file) {

	std::string base_filename = fbx_file.substr(fbx_file.find_last_of("/\\") + 1);
	std::string::size_type const p(base_filename.find_last_of('.'));
	std::string scene_name = base_filename.substr(0, p);
	std::set<std::string> bones_ = {};
	this->name = scene_name;
	


	const aiScene* m_pScene = aiImportFile(fbx_file.c_str(),aiProcess_CalcTangentSpace || aiProcess_GenSmoothNormals);
	
	unsigned int id_nd = 0;
	std::unordered_set<aiNode*> node_list; //Obviously I have way too many maps and vectors and stuff. This one is only used because aiNode holds the connection between them and the aiMeshes, allowing me to retrieve the associated transform for the inverse bind matrix 
	create_node_map(this->nodes, node_list, m_pScene->mRootNode, id_nd, -1);
	std::map<unsigned int, node> nodes_id = {};

	for (auto nd : this->nodes) {
		nodes_id[nd.second.id] = nd.second;
		
		

	}
	for (unsigned int idx_mesh = 0; idx_mesh < m_pScene->mNumMeshes; idx_mesh++) {

		aiMesh *current_mesh = m_pScene->mMeshes[idx_mesh];

		for (unsigned int idx_bone = 0; idx_bone < current_mesh->mNumBones; idx_bone++) {
		
			bones_.emplace(current_mesh->mBones[idx_bone]->mName.C_Str());
		
		}
	}

	aiNode* top_rig = find_rig_node(m_pScene->mRootNode, bones_);
	float start = 0;
	
	for (unsigned int i = 0; i < m_pScene->mNumAnimations; i++) {
		auto anim = m_pScene->mAnimations[i];

		std::string full_name = anim->mName.C_Str();
		full_name = full_name.substr(full_name.find_last_of("|") + 1);
		bool isittheone = true;

		if (isittheone == true) {
			if (this->anis.count(full_name) == 0) {
				this->anis[full_name].name = full_name;
				this->anis[full_name].start = start;
				this->anis[full_name].end = start + anim->mDuration / anim->mTicksPerSecond;
				start = start + anim->mDuration / anim->mTicksPerSecond;
			}
			for (unsigned int j = 0; j < anim->mNumChannels; j++) {
				std::string bone_name = anim->mChannels[j]->mNodeName.C_Str();
				aiQuaternion rotation_bp(this->nodes[bone_name].R.y, this->nodes[bone_name].R.z, this->nodes[bone_name].R.x);
				for (unsigned int k = 0; k < anim->mChannels[j]->mNumPositionKeys; k++) {

					vec3<float> pos = { anim->mChannels[j]->mPositionKeys[k].mValue.x, anim->mChannels[j]->mPositionKeys[k].mValue.y, anim->mChannels[j]->mPositionKeys[k].mValue.z };
					keyframe_pos key(anim->mChannels[j]->mPositionKeys[k].mTime / anim->mTicksPerSecond + this->anis[full_name].start, pos);
					this->anis[full_name].ani_bone_keys[bone_name].pos.push_back(key);

				}
				for (unsigned int k = 0; k < anim->mChannels[j]->mNumScalingKeys; k++) {
					vec3<float> sc = { anim->mChannels[j]->mScalingKeys[k].mValue.x, anim->mChannels[j]->mScalingKeys[k].mValue.y, anim->mChannels[j]->mScalingKeys[k].mValue.z };
					keyframe_scl key(anim->mChannels[j]->mScalingKeys[k].mTime / anim->mTicksPerSecond + this->anis[full_name].start, sc);
					this->anis[full_name].ani_bone_keys[bone_name].scl.push_back(key);
				}
				for (unsigned int k = 0; k < anim->mChannels[j]->mNumRotationKeys; k++) {
					aiQuaternion rotated = { rotation_bp.w, -rotation_bp.x, -rotation_bp.y, -rotation_bp.z };
					aiQuaternion identity = rotated * anim->mChannels[j]->mRotationKeys[k].mValue;

					vec4<float> rot = { identity.x, identity.y, identity.z,identity.w };
					keyframe_rot key(anim->mChannels[j]->mRotationKeys[k].mTime / anim->mTicksPerSecond + this->anis[full_name].start, rot);
					this->anis[full_name].ani_bone_keys[bone_name].rot.push_back(key);
				}
			}
		}
		
	}
	for (aiNode* nd_ptr : node_list) {


		for (unsigned int idx_mesh = 0; idx_mesh < nd_ptr->mNumMeshes; idx_mesh++) {

			aiMesh *current_mesh = m_pScene->mMeshes[nd_ptr->mMeshes[idx_mesh]];

			mesh mesh_;
			mesh_.material_id = current_mesh->mMaterialIndex;
			mesh_.name = current_mesh->mName.C_Str();
			//std::cout << "MESH " << mesh_.name << " " << current_mesh->mNumVertices << " " << std::endl;;
			for (unsigned int vertice_idx = 0; vertice_idx < current_mesh->mNumVertices; vertice_idx++) {
				mesh_.vertices.push_back(vec3<float>({ current_mesh->mVertices[vertice_idx].x, current_mesh->mVertices[vertice_idx].y, current_mesh->mVertices[vertice_idx].z }));
			}
			for (unsigned int face_idx = 0; face_idx < current_mesh->mNumFaces; face_idx++) {
				mesh_.faces_indexes.push_back(vec3<unsigned int>({ current_mesh->mFaces[face_idx].mIndices[0], current_mesh->mFaces[face_idx].mIndices[1], current_mesh->mFaces[face_idx].mIndices[2] }));
			}

			for (unsigned int normals_idx = 0; normals_idx < current_mesh->mNumVertices; normals_idx++)
			{
				if (current_mesh->mNormals != NULL)
					mesh_.normals.push_back(vec3<float>({ current_mesh->mNormals[normals_idx].x,current_mesh->mNormals[normals_idx].y,current_mesh->mNormals[normals_idx].z }));
				if (current_mesh->mTangents != NULL)
					mesh_.tangents.push_back(vec3<float>({ current_mesh->mTangents[normals_idx].x,current_mesh->mTangents[normals_idx].y,current_mesh->mTangents[normals_idx].z }));

			}

			for (unsigned int uv_channel = 0; uv_channel < current_mesh->GetNumUVChannels(); uv_channel++){
				std::vector<vec2<float>> channel = {};
				for (unsigned int uv_idx = 0; uv_idx < current_mesh->mNumVertices; uv_idx++) {
					channel.push_back(vec2<float>({ current_mesh->mTextureCoords[uv_channel][uv_idx][0], current_mesh->mTextureCoords[uv_channel][uv_idx][1] }));
				}
				mesh_.uvs.push_back(channel);
			}
			for (unsigned int bone_idx = 0; bone_idx < current_mesh->mNumBones; bone_idx++) {
				aiBone b = *current_mesh->mBones[bone_idx];

				current_mesh->mBones[bone_idx]->mOffsetMatrix = aiMatrix4x4();
				std::string bone_name = current_mesh->mBones[bone_idx]->mName.C_Str();

				node current_node = this->nodes[bone_name];
				while (true) {
					//std::cout << current_node->mName.C_Str() << std::endl;
					aiMatrix4x4 local = { current_node.transform.a.x, current_node.transform.a.y, current_node.transform.a.z, current_node.transform.a.t,
										current_node.transform.b.x, current_node.transform.b.y, current_node.transform.b.z, current_node.transform.b.t,
										current_node.transform.c.x, current_node.transform.c.y, current_node.transform.c.z, current_node.transform.c.t,
										current_node.transform.d.x, current_node.transform.d.y, current_node.transform.d.z, current_node.transform.d.t };
					current_mesh->mBones[bone_idx]->mOffsetMatrix = local * current_mesh->mBones[bone_idx]->mOffsetMatrix;
				
				
					if (current_node.parent == -1) {

						break;
					}
					current_node = nodes_id[current_node.parent];
				}

				current_mesh->mBones[bone_idx]->mOffsetMatrix = current_mesh->mBones[bone_idx]->mOffsetMatrix.Inverse();
				
				aiMatrix4x4 meshlocal = { nd_ptr->mTransformation.a1, nd_ptr->mTransformation.a2, nd_ptr->mTransformation.a3, nd_ptr->mTransformation.a4,
										  nd_ptr->mTransformation.b1, nd_ptr->mTransformation.b2, nd_ptr->mTransformation.b3, nd_ptr->mTransformation.b4,
										  nd_ptr->mTransformation.c1, nd_ptr->mTransformation.c2, nd_ptr->mTransformation.c3, nd_ptr->mTransformation.c4,
										  nd_ptr->mTransformation.d1, nd_ptr->mTransformation.d2, nd_ptr->mTransformation.d3, nd_ptr->mTransformation.d4 };
				;
				current_mesh->mBones[bone_idx]->mOffsetMatrix = meshlocal * current_mesh->mBones[bone_idx]->mOffsetMatrix;
				current_mesh->mBones[bone_idx]->mOffsetMatrix = current_mesh->mBones[bone_idx]->mOffsetMatrix.Inverse();
		   
				bone b_;
				b_.name = b.mName.C_Str();
				b.mOffsetMatrix = current_mesh->mBones[bone_idx]->mOffsetMatrix;
				b.mOffsetMatrix.Transpose();
				b_.offsetmatrix.a = { b.mOffsetMatrix.a1, b.mOffsetMatrix.a2,b.mOffsetMatrix.a3,b.mOffsetMatrix.a4 };
				b_.offsetmatrix.b = { b.mOffsetMatrix.b1, b.mOffsetMatrix.b2,b.mOffsetMatrix.b3,b.mOffsetMatrix.b4 };
				b_.offsetmatrix.c = { b.mOffsetMatrix.c1, b.mOffsetMatrix.c2,b.mOffsetMatrix.c3,b.mOffsetMatrix.c4 };
				b_.offsetmatrix.d = { b.mOffsetMatrix.d1, b.mOffsetMatrix.d2,b.mOffsetMatrix.d3,b.mOffsetMatrix.d4 };
				//std::cout << b_.name << std::endl;
				for (unsigned int weight_id = 0; weight_id < b.mNumWeights; weight_id++) {
					b_.vertex_id.push_back(b.mWeights[weight_id].mVertexId);
					b_.weights.push_back(b.mWeights[weight_id].mWeight);
				}
			
				mesh_.bones[b_.name] = b_;
			}

			aiMaterial *mat = m_pScene->mMaterials[current_mesh->mMaterialIndex];
			material m;
			m.id = current_mesh->mMaterialIndex;
			aiString name;
			mat->Get(AI_MATKEY_NAME, name);
			m.name = name.C_Str();
			size_t diff_count = mat->GetTextureCount(aiTextureType_DIFFUSE);
			for (unsigned int slot = 0; slot < diff_count; slot++) {
				aiString tex_name;
				mat->Get(AI_MATKEY_TEXTURE(aiTextureType_DIFFUSE, slot), tex_name);
				tex tex_;
				tex_.name = tex_name.C_Str();
				tex_.switch_name = "SWITCH_DIFFUSEMAP0";// tex_name.C_Str();
				tex_.tex_slot = slot;
			
				int uv_channel;
				mat->Get(AI_MATKEY_UVWSRC(aiTextureType_DIFFUSE, slot), uv_channel);
				tex_.uv = uv_channel;
				m.tex_data.push_back(tex_);
				m.uv_map_ids.push_back(uv_channel);
			}
			size_t spec_count = mat->GetTextureCount(aiTextureType_SPECULAR);
			for (unsigned int slot = 0; slot < spec_count; slot++) {
				aiString tex_name;
				mat->Get(AI_MATKEY_TEXTURE(aiTextureType_SPECULAR, slot), tex_name);
				tex tex_;
				tex_.name = tex_name.C_Str();
				tex_.switch_name = "SWITCH_MASKMAP0"; 
				tex_.tex_slot = slot;
				int uv_channel;
				mat->Get(AI_MATKEY_UVWSRC(aiTextureType_SPECULAR, slot), uv_channel);
				tex_.uv = uv_channel;
				m.tex_data.push_back(tex_);
				m.uv_map_ids.push_back(uv_channel);
			}
			size_t ambient_count = mat->GetTextureCount(aiTextureType_AMBIENT);
			for (unsigned int slot = 0; slot < ambient_count; slot++) {
				aiString tex_name;
				mat->Get(AI_MATKEY_TEXTURE(aiTextureType_AMBIENT, slot), tex_name);
				tex tex_;
				tex_.name = tex_name.C_Str();
				tex_.switch_name = "SWITCH_MASKMAP0";
				tex_.tex_slot = slot;
				int uv_channel;
				mat->Get(AI_MATKEY_UVWSRC(aiTextureType_AMBIENT, slot), uv_channel);
				tex_.uv = uv_channel;
				m.tex_data.push_back(tex_);
				m.uv_map_ids.push_back(uv_channel);
			}
			size_t emissive_count = mat->GetTextureCount(aiTextureType_EMISSIVE);
			for (unsigned int slot = 0; slot < emissive_count; slot++) {
				aiString tex_name;
				mat->Get(AI_MATKEY_TEXTURE(aiTextureType_EMISSIVE, slot), tex_name);
				tex tex_;
				tex_.name = tex_name.C_Str();
				tex_.switch_name = "SWITCH_MASKMAP0";
				tex_.tex_slot = slot;
				int uv_channel;
				mat->Get(AI_MATKEY_UVWSRC(aiTextureType_EMISSIVE, slot), uv_channel);
				tex_.uv = uv_channel;
				m.tex_data.push_back(tex_);
				m.uv_map_ids.push_back(uv_channel);
			}
			size_t height_count = mat->GetTextureCount(aiTextureType_HEIGHT);
			for (unsigned int slot = 0; slot < height_count; slot++) {
				aiString tex_name;
				mat->Get(AI_MATKEY_TEXTURE(aiTextureType_HEIGHT, slot), tex_name);
				tex tex_;
				tex_.name = tex_name.C_Str();
				tex_.switch_name = "SWITCH_MASKMAP0";
				tex_.tex_slot = slot;
				int uv_channel;
				mat->Get(AI_MATKEY_UVWSRC(aiTextureType_HEIGHT, slot), uv_channel);
				tex_.uv = uv_channel;
				m.tex_data.push_back(tex_);
				m.uv_map_ids.push_back(uv_channel);
			}
			size_t normals_count = mat->GetTextureCount(aiTextureType_NORMALS);
			for (unsigned int slot = 0; slot < normals_count; slot++) {
				aiString tex_name;
				mat->Get(AI_MATKEY_TEXTURE(aiTextureType_NORMALS, slot), tex_name);
				tex tex_;
				tex_.name = tex_name.C_Str();
				tex_.switch_name = "SWITCH_NORMALMAP0";
				tex_.tex_slot = slot;
				int uv_channel;
				mat->Get(AI_MATKEY_UVWSRC(aiTextureType_NORMALS, slot), uv_channel);
				tex_.uv = uv_channel;
				m.tex_data.push_back(tex_);
				m.uv_map_ids.push_back(uv_channel);
			}
			size_t shiny_count = mat->GetTextureCount(aiTextureType_SHININESS);
			for (unsigned int slot = 0; slot < shiny_count; slot++) {
				aiString tex_name;
				mat->Get(AI_MATKEY_TEXTURE(aiTextureType_SHININESS, slot), tex_name);
				tex tex_;
				tex_.name = tex_name.C_Str();
				tex_.switch_name = "SWITCH_MASKMAP0";
				tex_.tex_slot = slot;
				int uv_channel;
				mat->Get(AI_MATKEY_UVWSRC(aiTextureType_SHININESS, slot), uv_channel);
				tex_.uv = uv_channel;
				m.tex_data.push_back(tex_);
				m.uv_map_ids.push_back(uv_channel);
			}
			size_t opac_count = mat->GetTextureCount(aiTextureType_OPACITY);
			for (unsigned int slot = 0; slot < opac_count; slot++) {
				aiString tex_name;
				mat->Get(AI_MATKEY_TEXTURE(aiTextureType_OPACITY, slot), tex_name);
				tex tex_;
				tex_.name = tex_name.C_Str();
				tex_.switch_name = "SWITCH_MASKMAP0";
				tex_.tex_slot = slot;
				int uv_channel;
				mat->Get(AI_MATKEY_UVWSRC(aiTextureType_OPACITY, slot), uv_channel);
				tex_.uv = uv_channel;
				m.tex_data.push_back(tex_);
				m.uv_map_ids.push_back(uv_channel);
			}
			size_t disp_count = mat->GetTextureCount(aiTextureType_DISPLACEMENT);
			for (unsigned int slot = 0; slot < disp_count; slot++) {
				aiString tex_name;
				mat->Get(AI_MATKEY_TEXTURE(aiTextureType_DISPLACEMENT, slot), tex_name);
				tex tex_;
				tex_.name = tex_name.C_Str();
				tex_.switch_name = "SWITCH_MASKMAP0";
				tex_.tex_slot = slot;
				int uv_channel;
				mat->Get(AI_MATKEY_UVWSRC(aiTextureType_DISPLACEMENT, slot), uv_channel);
				tex_.uv = uv_channel;
				m.tex_data.push_back(tex_);
				m.uv_map_ids.push_back(uv_channel);
			}
			size_t lightmap_count = mat->GetTextureCount(aiTextureType_LIGHTMAP);
			for (unsigned int slot = 0; slot < lightmap_count; slot++) {
				aiString tex_name;
				mat->Get(AI_MATKEY_TEXTURE(aiTextureType_LIGHTMAP, slot), tex_name);
				tex tex_;
				tex_.name = tex_name.C_Str();
				tex_.switch_name = "SWITCH_MASKMAP0";
				tex_.tex_slot = slot;
				int uv_channel;
				mat->Get(AI_MATKEY_UVWSRC(aiTextureType_LIGHTMAP, slot), uv_channel);
				tex_.uv = uv_channel;
				m.tex_data.push_back(tex_);
				m.uv_map_ids.push_back(uv_channel);
			}
			size_t reflec_count = mat->GetTextureCount(aiTextureType_REFLECTION);
			for (unsigned int slot = 0; slot < reflec_count; slot++) {
				aiString tex_name;
				mat->Get(AI_MATKEY_TEXTURE(aiTextureType_REFLECTION, slot), tex_name);
				tex tex_;
				tex_.name = tex_name.C_Str();
				tex_.switch_name = "SWITCH_MASKMAP0";
				tex_.tex_slot = slot;
				int uv_channel;
				mat->Get(AI_MATKEY_UVWSRC(aiTextureType_REFLECTION, slot), uv_channel);
				tex_.uv = uv_channel;
				m.tex_data.push_back(tex_);
				m.uv_map_ids.push_back(uv_channel);
			}
			size_t ukn_count = mat->GetTextureCount(aiTextureType_UNKNOWN);
			for (unsigned int slot = 0; slot < ukn_count; slot++) {
				aiString tex_name;
				mat->Get(AI_MATKEY_TEXTURE(aiTextureType_UNKNOWN, slot), tex_name);
				tex tex_;
				tex_.name = tex_name.C_Str();
				tex_.switch_name = "SWITCH_MASKMAP0";
				tex_.tex_slot = slot;
				int uv_channel;
				mat->Get(AI_MATKEY_UVWSRC(aiTextureType_UNKNOWN, slot), uv_channel);
				tex_.uv = uv_channel;
				m.tex_data.push_back(tex_);
				m.uv_map_ids.push_back(uv_channel);
			}
			this->mats[mesh_.material_id] = m;

			this->meshes[mesh_.name].push_back(mesh_);
		}
	}

}
void model::to_merge(const model& m2) {

	for (auto ani : m2.anis) {
		if (this->anis.count(ani.first) == 0) {
			std::cout << "Adding animation " << ani.second.name << std::endl;
			this->anis[ani.first] = ani.second;
		}
	}
}
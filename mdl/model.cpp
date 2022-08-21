#include "model.h"
#include <assimp\scene.h>
#include <assimp\Exporter.hpp>
#include <iostream>
#include <filesystem>
#include "CLEDecrypt.h"
#include <assimp/postprocess.h>

namespace fs = std::filesystem;
void model::to_fbx(const AssetConfig &conf) {

	size_t real_nb_of_meshes = 0;
	for (auto mesh : this->meshes)
		real_nb_of_meshes += mesh.second.size();

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
				type = aiTextureType_OPACITY;
			else if (tex.switch_name == "SWITCH_MASKMAP1")
				type = aiTextureType_OPACITY;
			else if (tex.switch_name == "SWITCH_TOONMAP")
				type = aiTextureType_UNKNOWN;
			else if (tex.switch_name == "SWITCH_NORMALMAP2")
				type = aiTextureType_NORMALS;
			else if (tex.switch_name == "SWITCH_MASKMAP2")
				type = aiTextureType_OPACITY;
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

	//animations
	
	std::vector<aiAnimation*> animations_vec = {};
	unsigned int id_ani = 0;
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

					aiVector3t< float> scaling;
					aiQuaterniont< float > rotation;
					aiVector3t< float > position;

					aiVector3t< float> scaling_bp;
					aiQuaterniont< float > rotation_bp;
					aiVector3t< float > position_bp;

					aiMatrix4x4 bind_pos = current_node->mTransformation;

					bind_pos.Decompose(scaling_bp, rotation_bp, position_bp);


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
	for (idx_node = 0; idx_node < nb_nodes; idx_node++) {
		aiNode* current_node = aiNodes[idx_node];
		std::string current_node_name = current_node->mName.C_Str();
		
		std::string bone_name = current_node_name;
		aiMatrix4x4 inverse_transform;
		while (true) {
			inverse_transform = current_node->mTransformation * inverse_transform;
			current_node = current_node->mParent;
			if (current_node == NULL) break;
			current_node_name = current_node->mName.C_Str();
		}
		inverse_transform = inverse_transform.Inverse();
		for (aiBone* current_bone : bones_ptr[bone_name]) {
			current_bone->mOffsetMatrix = inverse_transform;
		}
		

	}

	for (auto it_m : meshes_id) {
		node_ptrs_str[it_m.first]->mNumMeshes = it_m.second.size();
		node_ptrs_str[it_m.first]->mMeshes = new unsigned int[it_m.second.size()];
		for (size_t i = 0; i < it_m.second.size(); i++)
			node_ptrs_str[it_m.first]->mMeshes[i] = it_m.second[i];
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

void model::to_merge(const model& m2) {

	for (auto ani : m2.anis) {
		if (this->anis.count(ani.first) == 0) {
			std::cout << "Adding animation " << ani.second.name << std::endl;
			this->anis[ani.first] = ani.second;
		}
	}
}
#pragma once

#include <cstdint>
#include <string>
#include <vector>
#include <assimp/scene.h>

template <class T>
struct vec2 {
    T x, y;
};

template <class T>
struct vec3 {
    T x, y, z;
};
template <class T>
struct vec4 {
    T x, y, z, t;
};
template <class T>
struct matrix4 {
    vec4<T> a, b, c, d;
    matrix4() = default;
    matrix4(vec3<T> t, vec3<T> r, vec3<T> s)
    {
        aiQuaternion quat(r.y, r.z, r.x);

        a.x = (1.0f - 2.0f * (quat.y * quat.y + quat.z * quat.z)) * s.x;
        a.y = (quat.x * quat.y + quat.z * quat.w) * s.x * 2.0f;
        a.z = (quat.x * quat.z - quat.y * quat.w) * s.x * 2.0f;
        a.t = 0.0f;
        b.x = (quat.x * quat.y - quat.z * quat.w) * s.y * 2.0f;
        b.y = (1.0f - 2.0f * (quat.x * quat.x + quat.z * quat.z)) * s.y;
        b.z = (quat.y * quat.z + quat.x * quat.w) * s.y * 2.0f;
        b.t = 0.0f;
        c.x = (quat.x * quat.z + quat.y * quat.w) * s.z * 2.0f;
        c.y = (quat.y * quat.z - quat.x * quat.w) * s.z * 2.0f;
        c.z = (1.0f - 2.0f * (quat.x * quat.x + quat.y * quat.y)) * s.z;
        c.t = 0.0f;
        d.x = t.x;
        d.y = t.y;
        d.z = t.z;
        d.t = 1.0f;
    }
	void decompose(vec3<float>& T, vec3<float>& R, vec3<float>& S);
	std::string to_string() {
	
		std::string result = "";
		result = result + std::to_string(a.x) + " " + std::to_string(a.y) + " " + std::to_string(a.z) + " " + std::to_string(a.t) + "\n";
		result = result + std::to_string(b.x) + " " + std::to_string(b.y) + " " + std::to_string(b.z) + " " + std::to_string(b.t) + "\n";
		result = result + std::to_string(c.x) + " " + std::to_string(c.y) + " " + std::to_string(c.z) + " " + std::to_string(c.t) + "\n";
		result = result + std::to_string(d.x) + " " + std::to_string(d.y) + " " + std::to_string(d.z) + " " + std::to_string(d.t) + "\n";
		return result;
	}
};

template <class T>
T read_data(std::vector<uint8_t> &content, uint32_t &addr)
{
    void* ptr = content.data() + addr;
    T result = *(static_cast<T*>(ptr));
    addr = addr + sizeof(T);

    return result;
}
template <class T>
void add_bytes(std::vector<uint8_t> &content, T value) {
	uint8_t* val_ptr = (uint8_t *)&value;
	for (unsigned int i = 0; i < sizeof(value); i++)
		content.push_back(val_ptr[i]);
}

template <class T>
std::vector<uint8_t> serialize_vector(std::vector<T> vec) {


	return std::vector<uint8_t>(vec.data(), vec.data() + vec.size());

}


template <class T>
void add_bytes_front(std::vector<uint8_t>& content, T value) {
	uint8_t* val_ptr = (uint8_t*)&value;
	for (int i = sizeof(value)-1; i >= 0; i--)
		content.insert(content.begin(), val_ptr[i]);
}
float read_as_float(uint32_t u32);
std::string read_string(std::vector<uint8_t>& content, uint32_t& addr);
std::vector<uint8_t> serialize_matrix44(matrix4<float> m);
vec3<float> quat_to_euler(vec4<float> quat);


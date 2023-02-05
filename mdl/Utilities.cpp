#include "Utilities.h"
#include <iostream>
#define M_PI 3.14159265358979323846
std::vector<uint8_t> serialize_matrix44(matrix4<float> m) {
	std::vector<uint8_t> output = {};
	add_bytes(output, m.a);
	add_bytes(output, m.b);
	add_bytes(output, m.c);
	add_bytes(output, m.d);
	return output;

}

vec3<float> quat_to_euler(vec4<float> quat) {
	
	float test = (quat.t * quat.y - quat.x * quat.z);
	float cosp, sinp, pitch;

	if (test < -0.5) {
		cosp = 1;
		sinp = 0;
		pitch = - M_PI / 2;

	}
	else if (test > 0.5) {
	
		cosp = 0;
		sinp = 1;
		pitch = M_PI / 2;
	
	}
	else{
		
		// pitch (y-axis rotation)
		sinp = std::sqrt(1 + 2 * (quat.t * quat.y - quat.x * quat.z));
		cosp = std::sqrt(1 - 2 * (quat.t * quat.y - quat.x * quat.z));
		pitch = 2 * std::atan2(sinp, cosp) - M_PI / 2;

		// yaw (z-axis rotation)
		
	}
	float sinr_cosp = 2 * (quat.t * quat.x + quat.y * quat.z);
	float cosr_cosp = 1 - 2 * (quat.x * quat.x + quat.y * quat.y);
	float roll = std::atan2(sinr_cosp, cosr_cosp);
	float siny_cosp = 2 * (quat.t * quat.z + quat.x * quat.y);
	float cosy_cosp = 1 - 2 * (quat.y * quat.y + quat.z * quat.z);
	float yaw = std::atan2(siny_cosp, cosy_cosp);

	return { roll, pitch, yaw };
}

void matrix4<float>::decompose(vec3<float>& T, vec3<float>& R, vec3<float>& S) {
	T.x = a.t;
	T.y = b.t;
	T.z = c.t;
	S.x = sqrt(a.x * a.x + b.x * b.x + c.x * c.x);
	S.y = sqrt(a.y * a.y + b.y * b.y + c.y * c.y);
	S.z = sqrt(a.z * a.z + b.z * b.z + c.z * c.z);

	float m00 = a.x / S.x;
	float m01 = a.y / S.x;
	float m02 = a.z / S.x;
	float m03 = 0;
	float m10 = b.x / S.y;
	float m11 = b.y / S.y;
	float m12 = b.z / S.y;
	float m13 = 0;
	float m20 = c.x / S.z;
	float m21 = c.y / S.z;
	float m22 = c.z / S.z;
	float m23 = 0;
	float m30 = 0;
	float m31 = 0;
	float m32 = 0;
	float m33 = 1;

	float tr = m00 + m11 + m22;
	float qw, qx, qy, qz;
	if (tr > 0) {
		float S = sqrt(tr + 1.0) * 2; // S=4*qw 
		qw = 0.25 * S;
		qx = (m21 - m12) / S;
		qy = (m02 - m20) / S;
		qz = (m10 - m01) / S;
	}
	else if ((m00 > m11)& (m00 > m22)) {
		float S = sqrt(1.0 + m00 - m11 - m22) * 2; // S=4*qx 
		qw = (m21 - m12) / S;
		qx = 0.25 * S;
		qy = (m01 + m10) / S;
		qz = (m02 + m20) / S;
	}
	else if (m11 > m22) {
		float S = sqrt(1.0 + m11 - m00 - m22) * 2; // S=4*qy
		qw = (m02 - m20) / S;
		qx = (m01 + m10) / S;
		qy = 0.25 * S;
		qz = (m12 + m21) / S;
	}
	else {
		float S = sqrt(1.0 + m22 - m00 - m11) * 2; // S=4*qz
		qw = (m10 - m01) / S;
		qx = (m02 + m20) / S;
		qy = (m12 + m21) / S;
		qz = 0.25 * S;
	}
	//we got our quaternion
	float mod = sqrt(qw * qw + qx * qx + qy * qy + qz * qz);

	R = quat_to_euler(vec4<float>({ qx/mod, qy / mod, qz / mod, qw / mod }));
	
}

float read_as_float(uint32_t u32) {
	float f;
	memcpy(&f, &u32, sizeof(u32));
	return f;
}

std::string read_string(std::vector<uint8_t>& content, uint32_t& addr) {
    uint8_t sz = content[addr];

    std::string res(content.begin() + addr + 1, content.begin() + addr + 1 + sz);
    addr = addr + sz + 1;
    return res;
}

std::string read_null_terminated_string(std::vector<uint8_t>& content, uint32_t& addr) {
    std::vector<uint8_t> bytes = {};
    uint8_t b = content[addr];
    while (b != 0) {

        bytes.push_back(b);
        addr = addr + 1;
        b = content[addr];

    }
    return std::string(bytes.begin(), bytes.end());
}
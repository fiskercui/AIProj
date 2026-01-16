#ifndef VEC3_H
#define VEC3_H

#include <cmath>
#include <iostream>

// 3D vector class - used for points, directions, and colors
class Vec3 {
public:
    double x, y, z;

    // Constructors
    Vec3() : x(0), y(0), z(0) {}
    Vec3(double x, double y, double z) : x(x), y(y), z(z) {}

    // Accessor methods (for color output)
    double r() const { return x; }
    double g() const { return y; }
    double b() const { return z; }

    // Unary operators
    Vec3 operator-() const { return Vec3(-x, -y, -z); }
    
    // Compound assignment operators
    Vec3& operator+=(const Vec3& v) {
        x += v.x;
        y += v.y;
        z += v.z;
        return *this;
    }

    Vec3& operator*=(double t) {
        x *= t;
        y *= t;
        z *= t;
        return *this;
    }

    Vec3& operator/=(double t) {
        return *this *= 1/t;
    }

    // Vector operations
    double length() const {
        return std::sqrt(length_squared());
    }

    double length_squared() const {
        return x*x + y*y + z*z;
    }

    // Normalize the vector (make it unit length)
    Vec3 normalized() const {
        double len = length();
        return Vec3(x/len, y/len, z/len);
    }

    // Check if vector is near zero in all dimensions
    bool near_zero() const {
        const double epsilon = 1e-8;
        return (std::fabs(x) < epsilon) && (std::fabs(y) < epsilon) && (std::fabs(z) < epsilon);
    }
};

// Type aliases for clarity
using Point3 = Vec3;   // 3D point
using Color = Vec3;    // RGB color

// Utility functions
inline std::ostream& operator<<(std::ostream& out, const Vec3& v) {
    return out << v.x << ' ' << v.y << ' ' << v.z;
}

// Binary operators
inline Vec3 operator+(const Vec3& u, const Vec3& v) {
    return Vec3(u.x + v.x, u.y + v.y, u.z + v.z);
}

inline Vec3 operator-(const Vec3& u, const Vec3& v) {
    return Vec3(u.x - v.x, u.y - v.y, u.z - v.z);
}

inline Vec3 operator*(const Vec3& u, const Vec3& v) {
    return Vec3(u.x * v.x, u.y * v.y, u.z * v.z);
}

inline Vec3 operator*(double t, const Vec3& v) {
    return Vec3(t * v.x, t * v.y, t * v.z);
}

inline Vec3 operator*(const Vec3& v, double t) {
    return t * v;
}

inline Vec3 operator/(const Vec3& v, double t) {
    return (1/t) * v;
}

// Dot product
inline double dot(const Vec3& u, const Vec3& v) {
    return u.x * v.x + u.y * v.y + u.z * v.z;
}

// Cross product
inline Vec3 cross(const Vec3& u, const Vec3& v) {
    return Vec3(
        u.y * v.z - u.z * v.y,
        u.z * v.x - u.x * v.z,
        u.x * v.y - u.y * v.x
    );
}

// Unit vector
inline Vec3 unit_vector(const Vec3& v) {
    return v / v.length();
}

// Random vector generation (needed for materials)
inline Vec3 random_vec3() {
    return Vec3(random_double(), random_double(), random_double());
}

inline Vec3 random_vec3(double min, double max) {
    return Vec3(random_double(min, max), random_double(min, max), random_double(min, max));
}

// Generate random vector in unit sphere (for diffuse materials)
inline Vec3 random_in_unit_sphere() {
    while (true) {
        Vec3 p = random_vec3(-1, 1);
        if (p.length_squared() < 1)
            return p;
    }
}

// Generate random unit vector (uniform distribution on sphere surface)
inline Vec3 random_unit_vector() {
    return unit_vector(random_in_unit_sphere());
}

// Generate random vector in hemisphere (for diffuse materials)
inline Vec3 random_in_hemisphere(const Vec3& normal) {
    Vec3 in_unit_sphere = random_in_unit_sphere();
    if (dot(in_unit_sphere, normal) > 0.0)
        return in_unit_sphere;
    else
        return -in_unit_sphere;
}

// Reflect vector v around normal n
inline Vec3 reflect(const Vec3& v, const Vec3& n) {
    return v - 2 * dot(v, n) * n;
}

// Refract vector (for glass materials)
inline Vec3 refract(const Vec3& uv, const Vec3& n, double etai_over_etat) {
    double cos_theta = std::fmin(dot(-uv, n), 1.0);
    Vec3 r_out_perp = etai_over_etat * (uv + cos_theta * n);
    Vec3 r_out_parallel = -std::sqrt(std::fabs(1.0 - r_out_perp.length_squared())) * n;
    return r_out_perp + r_out_parallel;
}

#endif
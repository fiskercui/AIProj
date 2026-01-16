#ifndef HITTABLE_H
#define HITTABLE_H

#include "ray.h"
#include "vec3.h"
#include <memory>

// Forward declaration
class Material;

// Structure to store hit information
struct HitRecord {
    Point3 point;           // Hit point in 3D space
    Vec3 normal;            // Surface normal at hit point
    std::shared_ptr<Material> material;  // Material of the hit object
    double t;               // Parameter t where ray hit the object
    bool front_face;        // Did ray hit from outside?

    // Set the normal to always point against the ray direction
    void set_face_normal(const Ray& r, const Vec3& outward_normal) {
        front_face = dot(r.direction, outward_normal) < 0;
        normal = front_face ? outward_normal : -outward_normal;
    }
};

// Abstract class for any object that can be hit by a ray
class Hittable {
public:
    virtual ~Hittable() = default;
    
    // Check if ray hits this object between t_min and t_max
    // If hit, fill in the hit_record and return true
    virtual bool hit(const Ray& r, double t_min, double t_max, HitRecord& rec) const = 0;
};

#endif
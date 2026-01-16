#ifndef SPHERE_H
#define SPHERE_H

#include "hittable.h"
#include "vec3.h"

class Sphere : public Hittable {
public:
    Point3 center;
    double radius;
    std::shared_ptr<Material> material;

    Sphere() {}
    Sphere(Point3 center, double radius, std::shared_ptr<Material> material)
        : center(center), radius(radius), material(material) {}

    virtual bool hit(const Ray& r, double t_min, double t_max, HitRecord& rec) const override;
};

// Ray-sphere intersection using quadratic formula
// Sphere equation: (P - C) · (P - C) = r²
// Ray equation: P(t) = A + tb
// Substituting: (A + tb - C) · (A + tb - C) = r²
// This gives us a quadratic equation: at² + bt + c = 0
bool Sphere::hit(const Ray& r, double t_min, double t_max, HitRecord& rec) const {
    Vec3 oc = r.origin - center;
    
    // Quadratic formula coefficients
    double a = dot(r.direction, r.direction);
    double half_b = dot(oc, r.direction);
    double c = dot(oc, oc) - radius * radius;
    
    // Discriminant
    double discriminant = half_b * half_b - a * c;
    
    if (discriminant < 0) {
        return false;  // No intersection
    }
    
    double sqrtd = std::sqrt(discriminant);
    
    // Find the nearest root that lies in the acceptable range
    double root = (-half_b - sqrtd) / a;
    if (root < t_min || t_max < root) {
        root = (-half_b + sqrtd) / a;
        if (root < t_min || t_max < root) {
            return false;
        }
    }
    
    // Fill in the hit record
    rec.t = root;
    rec.point = r.at(rec.t);
    Vec3 outward_normal = (rec.point - center) / radius;
    rec.set_face_normal(r, outward_normal);
    rec.material = material;
    
    return true;
}

#endif
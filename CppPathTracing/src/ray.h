#ifndef RAY_H
#define RAY_H

#include "vec3.h"

// Ray class - represents a ray in 3D space
// A ray is defined by: P(t) = origin + t * direction
// where t is a parameter that moves along the ray
class Ray {
public:
    Point3 origin;
    Vec3 direction;

    // Constructors
    Ray() {}
    Ray(const Point3& origin, const Vec3& direction) 
        : origin(origin), direction(direction) {}

    // Get point at parameter t along the ray
    Point3 at(double t) const {
        return origin + t * direction;
    }
};

#endif
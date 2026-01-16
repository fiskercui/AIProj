#ifndef MATERIAL_H
#define MATERIAL_H

#include "ray.h"
#include "hittable.h"
#include "vec3.h"
#include "utils.h"

// Forward declaration
struct HitRecord;

// Abstract material class
class Material {
public:
    virtual ~Material() = default;
    
    // Scatter function: given an incoming ray and hit record,
    // determine if the ray scatters and what color attenuation to apply
    virtual bool scatter(
        const Ray& r_in,
        const HitRecord& rec,
        Color& attenuation,
        Ray& scattered
    ) const = 0;
};

// Lambertian (diffuse) material - matte surfaces
class Lambertian : public Material {
public:
    Color albedo;  // Surface color

    Lambertian(const Color& albedo) : albedo(albedo) {}

    virtual bool scatter(
        const Ray& r_in,
        const HitRecord& rec,
        Color& attenuation,
        Ray& scattered
    ) const override {
        // Scatter in random direction from surface
        Vec3 scatter_direction = rec.normal + random_unit_vector();
        
        // Catch degenerate scatter direction
        if (scatter_direction.near_zero())
            scatter_direction = rec.normal;
        
        scattered = Ray(rec.point, scatter_direction);
        attenuation = albedo;
        return true;
    }
};

// Metal material - reflective surfaces
class Metal : public Material {
public:
    Color albedo;
    double fuzz;  // Fuzziness of reflection (0 = perfect mirror, 1 = very fuzzy)

    Metal(const Color& albedo, double fuzz) : albedo(albedo), fuzz(fuzz < 1 ? fuzz : 1) {}

    virtual bool scatter(
        const Ray& r_in,
        const HitRecord& rec,
        Color& attenuation,
        Ray& scattered
    ) const override {
        Vec3 reflected = reflect(unit_vector(r_in.direction), rec.normal);
        scattered = Ray(rec.point, reflected + fuzz * random_in_unit_sphere());
        attenuation = albedo;
        return (dot(scattered.direction, rec.normal) > 0);
    }
};

// Dielectric material - glass, water, etc.
class Dielectric : public Material {
public:
    double refractive_index;

    Dielectric(double refractive_index) : refractive_index(refractive_index) {}

    virtual bool scatter(
        const Ray& r_in,
        const HitRecord& rec,
        Color& attenuation,
        Ray& scattered
    ) const override {
        attenuation = Color(1.0, 1.0, 1.0);  // Glass doesn't absorb light
        double refraction_ratio = rec.front_face ? (1.0 / refractive_index) : refractive_index;

        Vec3 unit_direction = unit_vector(r_in.direction);
        double cos_theta = std::fmin(dot(-unit_direction, rec.normal), 1.0);
        double sin_theta = std::sqrt(1.0 - cos_theta * cos_theta);

        bool cannot_refract = refraction_ratio * sin_theta > 1.0;
        Vec3 direction;

        // Use Schlick's approximation for reflectance
        if (cannot_refract || reflectance(cos_theta, refraction_ratio) > random_double())
            direction = reflect(unit_direction, rec.normal);
        else
            direction = refract(unit_direction, rec.normal, refraction_ratio);

        scattered = Ray(rec.point, direction);
        return true;
    }

private:
    // Schlick's approximation for reflectance
    static double reflectance(double cosine, double ref_idx) {
        double r0 = (1 - ref_idx) / (1 + ref_idx);
        r0 = r0 * r0;
        return r0 + (1 - r0) * std::pow((1 - cosine), 5);
    }
};

#endif
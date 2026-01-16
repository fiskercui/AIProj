#include <iostream>
#include <fstream>
#include "vec3.h"
#include "ray.h"
#include "utils.h"
#include "hittable_list.h"
#include "sphere.h"
#include "material.h"

#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

// Recursive ray color calculation with material scattering
Color ray_color(const Ray& r, const Hittable& world, int depth) {
    HitRecord rec;
    
    // If we've exceeded the ray bounce limit, no more light is gathered
    if (depth <= 0)
        return Color(0, 0, 0);
    
    // Check if ray hits anything in the scene (start from 0.001 to avoid shadow acne)
    if (world.hit(r, 0.001, infinity, rec)) {
        Ray scattered;
        Color attenuation;
        
        // Ask the material how it scatters light
        if (rec.material->scatter(r, rec, attenuation, scattered)) {
            // Recursively trace the scattered ray
            return attenuation * ray_color(scattered, world, depth - 1);
        }
        
        // If material doesn't scatter, return black (absorbed)
        return Color(0, 0, 0);
    }
    
    // Background: blue to white gradient (sky)
    Vec3 unit_direction = unit_vector(r.direction);
    double t = 0.5 * (unit_direction.y + 1.0);
    return (1.0 - t) * Color(1.0, 1.0, 1.0) + t * Color(0.5, 0.7, 1.0);
}

// Write color to buffer with gamma correction
void write_color(unsigned char* buffer, int index, Color pixel_color, int samples_per_pixel) {
    double r = pixel_color.r();
    double g = pixel_color.g();
    double b = pixel_color.b();
    
    // Divide by number of samples and gamma-correct (gamma=2.0)
    double scale = 1.0 / samples_per_pixel;
    r = std::sqrt(scale * r);
    g = std::sqrt(scale * g);
    b = std::sqrt(scale * b);
    
    // Clamp to [0, 1] and convert to 0-255
    buffer[index + 0] = static_cast<unsigned char>(256 * clamp(r, 0.0, 0.999));
    buffer[index + 1] = static_cast<unsigned char>(256 * clamp(g, 0.0, 0.999));
    buffer[index + 2] = static_cast<unsigned char>(256 * clamp(b, 0.0, 0.999));
}

int main() {
    // Image parameters
    const double aspect_ratio = 16.0 / 9.0;
    const int image_width = 400;
    const int image_height = static_cast<int>(image_width / aspect_ratio);
    const int samples_per_pixel = 100;  // Anti-aliasing samples
    const int max_depth = 50;           // Maximum ray bounce depth

    // World (scene setup) with different materials
    HittableList world;
    
    // Ground - large diffuse sphere
    auto material_ground = std::make_shared<Lambertian>(Color(0.8, 0.8, 0.0));
    world.add(std::make_shared<Sphere>(Point3(0, -100.5, -1), 100, material_ground));
    
    // Center sphere - diffuse (matte)
    auto material_center = std::make_shared<Lambertian>(Color(0.1, 0.2, 0.5));
    world.add(std::make_shared<Sphere>(Point3(0, 0, -1), 0.5, material_center));
    
    // Left sphere - metal
    auto material_left = std::make_shared<Metal>(Color(0.8, 0.8, 0.8), 0.3);
    world.add(std::make_shared<Sphere>(Point3(-1.0, 0, -1), 0.5, material_left));
    
    // Right sphere - glass
    auto material_right = std::make_shared<Dielectric>(1.5);
    world.add(std::make_shared<Sphere>(Point3(1.0, 0, -1), 0.5, material_right));

    // Camera setup
    double viewport_height = 2.0;
    double viewport_width = aspect_ratio * viewport_height;
    double focal_length = 1.0;

    Point3 camera_origin = Point3(0, 0, 0);
    Vec3 horizontal = Vec3(viewport_width, 0, 0);
    Vec3 vertical = Vec3(0, viewport_height, 0);
    Point3 lower_left_corner = camera_origin 
                              - horizontal/2 
                              - vertical/2 
                              - Vec3(0, 0, focal_length);

    std::cout << "==========================================" << std::endl;
    std::cout << "  C++ Path Tracer - Material System" << std::endl;
    std::cout << "==========================================" << std::endl;
    std::cout << "Rendering: " << image_width << "x" << image_height << " pixels" << std::endl;
    std::cout << "Samples per pixel: " << samples_per_pixel << std::endl;
    std::cout << "Max ray depth: " << max_depth << std::endl;
    std::cout << "Scene: 4 spheres with different materials" << std::endl;
    std::cout << "  - Ground: Yellow diffuse" << std::endl;
    std::cout << "  - Center: Blue diffuse" << std::endl;
    std::cout << "  - Left: Metal (slightly fuzzy)" << std::endl;
    std::cout << "  - Right: Glass (refractive)" << std::endl;
    std::cout << std::endl;

    // Seed random number generator
    std::srand(static_cast<unsigned int>(std::time(nullptr)));

    // Create image data (RGB format)
    unsigned char* image_data = new unsigned char[image_width * image_height * 3];

    // Render loop
    for (int j = image_height - 1; j >= 0; --j) {
        if (j % 20 == 0) {
            std::cout << "Scanlines remaining: " << j << std::endl;
        }
        
        for (int i = 0; i < image_width; ++i) {
            Color pixel_color(0, 0, 0);
            
            // Multi-sampling for anti-aliasing
            for (int s = 0; s < samples_per_pixel; ++s) {
                double u = (i + random_double()) / (image_width - 1);
                double v = (j + random_double()) / (image_height - 1);
                
                Ray r(camera_origin, lower_left_corner + u*horizontal + v*vertical - camera_origin);
                pixel_color += ray_color(r, world, max_depth);
            }
            
            // Write the pixel
            int index = ((image_height - 1 - j) * image_width + i) * 3;
            write_color(image_data, index, pixel_color, samples_per_pixel);
        }
    }

    std::cout << "\nWriting image files..." << std::endl;

    // Output PPM format
    std::ofstream ppm_file("output/path_traced.ppm");
    ppm_file << "P3\n" << image_width << ' ' << image_height << "\n255\n";
    
    for (int j = 0; j < image_height; j++) {
        for (int i = 0; i < image_width; i++) {
            int index = (j * image_width + i) * 3;
            ppm_file << static_cast<int>(image_data[index + 0]) << ' '
                     << static_cast<int>(image_data[index + 1]) << ' '
                     << static_cast<int>(image_data[index + 2]) << '\n';
        }
    }
    ppm_file.close();

    // Output PNG format
    stbi_write_png("output/path_traced.png", image_width, image_height, 3, image_data, image_width * 3);

    delete[] image_data;

    std::cout << "\n==========================================" << std::endl;
    std::cout << "  [SUCCESS] Render Complete!" << std::endl;
    std::cout << "==========================================" << std::endl;
    std::cout << "Images saved to:" << std::endl;
    std::cout << "  - output/path_traced.ppm" << std::endl;
    std::cout << "  - output/path_traced.png" << std::endl;
    std::cout << "\nYou should see photo-realistic spheres with:" << std::endl;
    std::cout << "  - Diffuse (matte) materials" << std::endl;
    std::cout << "  - Reflective metal" << std::endl;
    std::cout << "  - Transparent glass with refraction" << std::endl;
    std::cout << "  - Smooth anti-aliasing" << std::endl;
    std::cout << "\nThis is REAL path tracing!" << std::endl;

    return 0;
}
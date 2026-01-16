#ifndef UTILS_H
#define UTILS_H

#include <cmath>
#include <cstdlib>
#include <limits>
#include <memory>

// Constants
const double infinity = std::numeric_limits<double>::infinity();
const double pi = 3.1415926535897932385;

// Utility functions
inline double degrees_to_radians(double degrees) {
    return degrees * pi / 180.0;
}

inline double radians_to_degrees(double radians) {
    return radians * 180.0 / pi;
}

// Random number generation [0, 1)
inline double random_double() {
    return std::rand() / (RAND_MAX + 1.0);
}

// Random number in range [min, max)
inline double random_double(double min, double max) {
    return min + (max - min) * random_double();
}

// Clamp value between min and max
inline double clamp(double x, double min, double max) {
    if (x < min) return min;
    if (x > max) return max;
    return x;
}

#endif
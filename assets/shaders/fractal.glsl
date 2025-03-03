#version 330 core

uniform sampler2D base_surface;
uniform vec2 resolution;
uniform vec2 mouse_position;

in vec2 uv;
out vec4 out_colour;

const vec4 start_colour = vec4(0.35, 0.6, 0.65, 1.0);
const vec4 end_colour = vec4(0.65, 0.4, 0.35, 1.0);

vec2 compute_next(vec2 current, vec2 constant) {
    float zr = current.x * current.x - current.y * current.y;
    float zi = 2.0 * current.x * current.y;
    return vec2(zr, zi) + constant;
}

float mod2(vec2 z) {
    return z.x * z.x + z.y * z.y;
}

int compute_iterations(vec2 z0, vec2 constant, int max_iterations) {
    vec2 zn = z0;
    int iteration = 0;
    while (mod2(zn) < 4.0 && iteration < max_iterations) {
        zn = compute_next(zn, constant);
        iteration++;
    }
    return iteration;
}

void main() {
    vec2 new_uv = (uv - vec2(0.5)) * (7.5 - 7.5 * mouse_position.x / resolution.x);
    float iterations = compute_iterations(new_uv, vec2(1.0, -1.0), 50);
    out_colour = vec4(iterations / 10);
//    out_colour = mix(start_colour, end_colour, iterations / 5);
}

#version 330 core

uniform sampler2D base_surface;
uniform ivec2 resolution;
uniform float time;

in vec2 uv;
out vec4 out_colour;

vec3 palette(float t) {
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(2.0, 1.0, 0.0);
    vec3 d = vec3(0.5, 0.2, 0.25);
    return a + b * cos(6.28318 * (c * t + d));
}

void main() {
    vec2 new_uv = 2.0 * uv - 1;
    vec2 uv0 = new_uv;
    vec3 final_colour = vec3(0.0);

    for (float i = 0.0; i < 4.0; i++) {
        new_uv = fract(new_uv * 1.5) - 0.5;
        float d = length(new_uv) * exp(-length(uv0));
        vec3 colour = palette(length(uv0) + i / 2.0 + time / 2.0);
        d = sin(d * 8.0 + time) / 8.0;
        d = abs(d);
        d = pow(0.01 / d, 1.2);
        final_colour += colour * d;
    }

    out_colour = vec4(final_colour, 1.0);
}

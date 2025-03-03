#version 330 core

uniform sampler2D base_surface;
const int num_circles = 100;
uniform vec3 circles[num_circles];

in vec2 uv;
out vec4 out_colour;

void main() {
    float colour = 1.0;
    for (int i = 0; i < num_circles; i++) {
        float d = length(uv - circles[i].xy) - circles[i].z;
        d = smoothstep(0.0, 0.025, d);
        colour *= d;
    }
    out_colour = vec4(colour, colour, colour, 1.0);
}

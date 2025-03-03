#version 330 core

uniform sampler2D base_surface;
uniform sampler2D noise;
uniform ivec2 resolution;
uniform float time;

in vec2 uv;
out vec4 out_colour;

const float range = 0.1;
float threshold2 = time / 2;


void main() {
    vec4 base_colour = texture(base_surface, uv);
    float noise = texture(noise, uv).r;
    float t = smoothstep(threshold2 - range, threshold2 + range, noise);

    out_colour = mix(base_colour, vec4(0.1), t);
}

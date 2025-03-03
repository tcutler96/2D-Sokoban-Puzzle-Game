#version 330 core

uniform sampler2D base_surface;
uniform vec2 resolution;
uniform float time;

in vec2 uv;
out vec4 out_colour;

void main() {
    vec4 base_colour = texture(base_surface, uv);
    out_colour = base_colour;
}

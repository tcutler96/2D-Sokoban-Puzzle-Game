#version 330 core

uniform sampler2D base_surface;

in vec2 uv;
out vec4 out_colour;

void main() {
    vec4 base_colour = texture(base_surface, uv);
    out_colour = vec4(1.0 - base_colour.r, 1.0 - base_colour.g, 1.0 - base_colour.b, 1.0);
}

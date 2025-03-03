#version 330 core

uniform sampler2D base_surface;

in vec2 uv;
out vec4 out_colour;

void main() {
    vec2 new_uvs = vec2(fract(uv.x * 4), fract(uv.y * 2));
    out_colour = texture(base_surface, new_uvs);
}

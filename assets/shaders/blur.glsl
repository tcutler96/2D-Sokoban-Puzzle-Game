#version 330 core

uniform sampler2D base_surface;
uniform vec2 pixel_size;
uniform int blur_amount;
uniform vec2 blur_direction;

in vec2 uv;
out vec4 out_colour;

const int blur_length = blur_amount * 2 + 1;

void main() {
    out_colour = vec4(0.0);
    for (int i = 0; i < blur_length; i++) {
        vec2 new_uvs = vec2(uv + blur_direction * pixel_size * (i - blur_amount));
        out_colour += texture(base_surface, new_uvs);
    }
    out_colour /= blur_length;
}

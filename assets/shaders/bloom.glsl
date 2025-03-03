#version 330 core

uniform sampler2D base_surface;
uniform sampler2D extra1_texture;
uniform float time;
uniform float bloom_amount;
uniform bool bloom_time;

in vec2 uv;

out vec4 out_colour;

void main() {
    vec4 main_colour = texture(base_surface, uv);
    vec4 bloom_colour = texture(extra1_texture, uv);
    if (bloom_time) {
        out_colour = main_colour + bloom_colour * (max(sin(time), 0));
    } else {
        out_colour = main_colour + bloom_colour * bloom_amount;
    }

}

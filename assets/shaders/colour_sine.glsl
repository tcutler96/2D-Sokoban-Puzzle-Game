#version 330 core

uniform sampler2D base_surface;
uniform float time;

in vec2 uv;
out vec4 out_colour;

void main() {
    vec4 base_colour = texture(base_surface, uv);
    float colour = (sin(uv.x * 16 + time) + 1) / 2;
    out_colour = mix(base_colour, vec4(colour, 0.0, 1.0, 1.0), 0.25);
}

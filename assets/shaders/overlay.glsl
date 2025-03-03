#version 330 core

uniform sampler2D base_surface;
uniform sampler2D ui;
uniform vec2 resolution;
uniform float time;

in vec2 uv;
out vec4 out_colour;

void main() {
    vec4 base_colour = texture(base_surface, uv);
    vec4 ui_colour = texture(ui, uv);
    out_colour = out_colour * (1.0 - ui_colour.a) + ui_colour;
}

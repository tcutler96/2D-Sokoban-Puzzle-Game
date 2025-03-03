#version 330 core

uniform sampler2D base_surface;
uniform sampler2D ui_surface;
uniform sampler2D buffer_surface;

in vec2 uv;
out vec4 out_colour;



void main() {
    vec4 base_colour = texture(base_surface, uv);
    vec4 ui_colour = texture(ui_surface, uv);
    vec4 buffer_colour = texture(buffer_surface, vec2(uv.x, 1.0 - uv.y));

    out_colour = mix(base_colour, buffer_colour, 0.9);
    out_colour = out_colour * (1.0 - ui_colour.a) + ui_colour;
}

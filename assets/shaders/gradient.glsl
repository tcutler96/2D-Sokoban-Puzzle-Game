#version 330 core

uniform sampler2D base_surface;

in vec2 uv;
out vec4 out_colour;

void main() {
//    vec4 top_left = vec4(1.0, 1.0, 1.0, 1.0);
//    vec4 top_right = vec4(1.0, 0.0, 0.0, 1.0);
//    vec4 bottom_left = vec4(0.0, 1.0, 0.0, 1.0);
//    vec4 bottom_right = vec4(0.0, 0.0, 1.0, 1.0);
    vec4 top_left = vec4(0.5, 0.1, 0.9, 1.0);
    vec4 top_right = vec4(0.3, 1.0, 0.8, 1.0);
    vec4 bottom_left = vec4(0.8, 0.6, 0.1, 1.0);
    vec4 bottom_right = vec4(0.7, 0.1, 0.2, 1.0);

    vec4 top = mix(top_left, top_right, uv.x);
    vec4 bottom = mix(bottom_left, bottom_right, uv.x);

    vec4 gradient = mix(top, bottom, uv.y);
    vec4 base_colour = texture(base_surface, uv);
    out_colour = mix(base_colour, gradient, 0.5);
}

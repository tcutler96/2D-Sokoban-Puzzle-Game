#version 330 core

uniform sampler2D base_surface;

in vec2 uv;
out vec4 out_colour;

void main() {
    vec4 base_colour = texture(base_surface, uv);
    float brightness = base_colour.r * 0.2126 + base_colour.r * 0.7152 + base_colour.b * 0.0722;
    out_colour = vec4(vec3(brightness), 1.0);
}

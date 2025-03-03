#version 330 core

uniform sampler2D base_surface;
uniform vec3 fade_colour;
uniform float fade_scale;

in vec2 uv;
out vec4 out_colour;

void main() {
    vec4 base_colour = texture(base_surface, uv);
    out_colour = mix(base_colour, vec4(fade_colour, 1.0), clamp(fade_scale, 0, 1));
}

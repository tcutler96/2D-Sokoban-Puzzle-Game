#version 330 core

uniform sampler2D base_surface;
uniform vec2 resolution;
uniform vec2 mouse_position;

in vec2 uv;
out vec4 out_colour;

const vec4 start_colour = vec4(0.35, 0.6, 0.65, 1.0);
const vec4 end_colour = vec4(0.65, 0.4, 0.35, 1.0);

void main() {
    vec2 Z, R = vec2(2.0 + 2.0 * mouse_position.x / resolution.x, 1.0 + 50.0 * mouse_position.x / resolution.x);
    for (out_colour *= 0.0; out_colour.a++ < 1e2 && dot(Z,Z) < 4.0;
         Z = (uv + uv - R.xy) / R.y + mat2(Z, -Z.y, Z.x) * Z);
    out_colour += out_colour.a / 1e2;
    out_colour = mix(start_colour, end_colour, out_colour.r);
}

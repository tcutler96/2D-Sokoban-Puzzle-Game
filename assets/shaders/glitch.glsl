#version 330 core

uniform sampler2D base_surface;
uniform sampler2D ui;
uniform sampler2D noise;
uniform float time;

in vec2 uv;
out vec4 out_colour;

const float cutoff = 0.55;

float get_offset() {
    float v = texture(noise, vec2(sin(time / 100), sin(time / 100))).x;
    if (v < cutoff) {
        return 0;
    }
    v = pow((v - cutoff) * 1 / (1 - cutoff), 2);
    return v;
}

void main() {
    vec4 base_colour = texture(base_surface, uv);
    vec4 ui_colour = texture(ui, uv);
    vec2 offset = vec2(get_offset(), 0.0);
    base_colour.r = texture(base_surface, uv + offset).r;
    base_colour.b = texture(base_surface, uv - offset).b;
    ui_colour.r = texture(ui, uv + offset).r;
    ui_colour.b = texture(ui, uv - offset).b;

    out_colour = base_colour * (1.0 - ui_colour.a) + ui_colour;
}

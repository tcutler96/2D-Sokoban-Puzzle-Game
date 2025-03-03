#version 330 core

uniform sampler2D base_surface;
uniform sampler2D ui_surface;
uniform sampler2D buffer_surface;
uniform sampler2D noise;
uniform vec2 resolution;
uniform vec2 pixel;

in vec2 uv;
out vec4 out_colour;

const vec4 on_colour = vec4(0.96, 0.95, 0.76, 1.0);
const vec4 off_colour = vec4(0.19, 0.16, 0.24, 1.0);

bool check_colour(vec4 colour) {
    vec4 d = colour - on_colour;
    float a = abs(d.r) + abs(d.g) + abs(d.b);
    return a < 0.1;
}


void main() {
    vec4 base_colour = texture(base_surface, uv);
    vec4 ui_colour = texture(ui_surface, uv);
    vec2 uv_flipped = vec2(uv.x, 1.0 - uv.y);
    vec4 buffer_colour = texture(buffer_surface, uv_flipped);
    int current = int(check_colour(buffer_colour));
    int surround = -current;
    for (float i = -1.0; i < 2.0; i++) {
        for (float j = -1.0; j < 2.0; j++) {
            float x = uv_flipped.x + i * pixel.x;
            float y = uv_flipped.y + j * pixel.y;
            vec4 surround_colour = texture(buffer_surface, vec2(x, y));
            surround += int(check_colour(surround_colour));
        }
    }

    if (current == 1 && (surround < 1.5 || surround > 3.5)) {
        current = 0;
    } else if (surround > 2.5 && surround < 3.5) {
        current = 1;
    }
    out_colour = vec4((on_colour.r * current) + (off_colour.r * (1 - current)), (on_colour.g * current) + (off_colour.g * (1 - current)), (on_colour.b * current) + (off_colour.b * (1 - current)), 1.0);
    out_colour = mix(out_colour, base_colour, base_colour.a);
    out_colour = mix(out_colour, ui_colour, ui_colour.a);
}

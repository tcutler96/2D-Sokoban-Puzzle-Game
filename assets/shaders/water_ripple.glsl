#version 330 core

uniform sampler2D base_surface;
uniform sampler2D buffer_surface;
uniform vec2 resolution;
uniform vec2 mouse_position;

in vec2 uv;
out vec4 out_colour;

const float damping = 0.99;


void main() {
    vec2 pixel = 1.0 / resolution;
    float buffer_colour = texture(buffer_surface, vec2(uv.x, 1.0 - uv.y)).r;
    if (uv * pixel == vec2(544.0)) {
        buffer_colour = 1.0;
    }

    float u = texture(base_surface, uv + vec2(0.0, pixel.y)).r;
    float d = texture(base_surface, uv - vec2(0.0, pixel.y)).r;
    float l = texture(base_surface, uv + vec2(pixel.x, 0.0)).r;
    float r = texture(base_surface, uv  - vec2(pixel.x, 0.0)).r;

    float next = ((u + d + l + r) / 2.0) - buffer_colour;
    next *= damping;

    out_colour = vec4(next, next / 2.0 + 0.5, 1.0, 1.0);
    vec4 base_colour = texture(base_surface, uv);
    if (base_colour == vec4(1.0)) {
        out_colour = vec4(0.0);
    }






//    vec4 base_colour = texture(base_surface, uv);
//    vec2 uv_flip = vec2(uv.x, 1.0 - uv.y);
//    vec4 buffer_colour = texture(buffer_surface, uv_flip);
//    vec4 buffer_colour = texture(buffer_surface, uv_flip - vec2(0.0, 0.5));
//    float brightness = buffer_colour.r * 0.2126 + buffer_colour.r * 0.7152 + buffer_colour.b * 0.0722;
//    out_colour = base_colour;
//    out_colour = buffer_colour;  // doesnt display anything because we are looping over a blank/ black surface...
//    out_colour = mix(base_colour, buffer_colour, step(0.5, uv.y));
//    out_colour = mix(base_colour, vec4(brightness), uv.x);
}

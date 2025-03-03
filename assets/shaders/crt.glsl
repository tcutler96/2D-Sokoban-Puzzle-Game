#version 330 core

uniform sampler2D base_surface;

in vec2 uv;
out vec4 out_colour;

vec2 resolution = vec2(1088, 1088);
vec2 curvature = vec2(3.0, 3.0);
float opacity = 0.5;
float gamma = 2.2;

vec2 curve_remap(vec2 uv) {
    uv = vec2(2.0) * uv - vec2(1.0);
    vec2 offset = abs(uv.yx) / curvature;
    uv = uv + uv * offset * offset;
    uv = uv * 0.5 + 0.5;
    return uv;
}

vec4 scanline_intensity(float uv, float scale) {
    float intensity = sin(uv * scale * 3.1415926 * 2.0);
    intensity = ((0.5 * intensity) + 0.5) * 0.9 + 0.1;
    return vec4(vec3(pow(intensity, opacity)), 1.0);
}

vec4 gamma_correction(vec4 colour) {
    return vec4(pow(colour.rgb, vec3(1.0 / gamma)), 1.0);
}

void main() {
    vec2 new_uv = curve_remap(uv);
    if (new_uv.x > 1.0 || new_uv.x < 0.0 || new_uv.y > 1.0 || new_uv.y < 0.0) {
    out_colour = vec4(0.025, 0.05, 0.025, 1.0);
    } else {
        vec4 base_colour = texture(base_surface, new_uv);
        base_colour *= scanline_intensity(new_uv.x, resolution.x * 7.5);
        base_colour *= scanline_intensity(new_uv.y, 0);
        out_colour = gamma_correction(base_colour);
    }
}

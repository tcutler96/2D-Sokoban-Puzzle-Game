#version 330 core

uniform sampler2D base_surface;
uniform float time;

in vec2 uv;
out vec4 out_colour;

vec2 H2(vec2 p) {
    return 2.0 * fract(sin(p) * 4e4) - 1.0;
}

vec4 H4(vec4 p) {
    return 2.0 * fract(sin(p) * 4e4) - 1.0;
}

void main() {
    float t = time, a = 0.25, N = 123.0, j=0.0, i = j;
    vec2  r = vec2(1.0), p = 5.0 * (uv + uv - r) / r.y;
    for (; i < 3.0; i++)
        t *= 0.2, N += 135.0, p += cos(H2(N + vec2(0, 215.3)) + 0.9) * sin(t + sin(t * 0.3) * 0.5);
     for (out_colour = vec4(0.9); j++ < 8.0 ; a = -a)
        for(r = p, i = 1.0; i > 0.0; i -= 0.03) {
            vec4 P = vec4(i * 1.5 - 0.55, j * 0.5 + time * 0.15, i * 2.0 + 0.03, j / 4.0 + time * 0.5),
                 I = floor(P),
                 S = I.xxzz + I.yyww * 99.0 + vec2(0, 99).xyxy;
            P -= I, P *= P * (3.0 - P - P);
            S = mix(H4(S), H4(S + 1.0), P.xxzz);
            out_colour -= 0.002 / abs(i * 0.3 - length(r += a * mix(S.xz, S.yw, P.yw))) / exp(i * 0.3);
        }
}

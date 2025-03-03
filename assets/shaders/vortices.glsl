#version 330 core

uniform sampler2D base_surface;
uniform ivec2 resolution;
uniform float time;

in vec2 uv;
out vec4 out_colour;

float numOct  = 5.0;
float focus = 0.0;
float focus2 = 0.0;
#define pi  3.14159265

float random(vec2 p) {
    return fract(sin(dot(p, vec2(12.0, 90.0))) *  5e5);
}

mat2 rot2(float an) {
    float cc = cos(an), ss = sin(an);
    return mat2(cc, -ss, ss, cc);
}

float noise(vec3 p) {
    vec2 i = floor(p.yz);
    vec2 f = fract(p.yz);
    float a = random(i + vec2(0.0, 0.0));
    float b = random(i + vec2(1.0, 0.0));
    float c = random(i + vec2(0.0, 1.0));
    float d = random(i + vec2(1.0, 1.0));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

float fbm3d(vec3 p) {
    float v = 0.0;
    float a = 0.5;
    vec3 shift = vec3(focus - focus2);
    float angle = pi / 1.3 + 0.03 * focus;
    for (float i=0.0; i < numOct; i++) {
        v += a * noise(p);
        p.xz = rot2(-angle) * p.xz;
        p = 2.0 * p + shift;
        a *= 0.22 * (1.0 + focus + focus2);
    }
    return v;
}

void main() {
    vec2 uv = (uv - vec2(0.5)) * 7.5;

    float aspectRatio = resolution.x / resolution.y;

    vec3 rd = normalize(vec3(uv, -1.2));
    vec3 ro = vec3(0);

    float delta = time / 1.5;

    rd.yz *= rot2(-delta);
    rd.xz *= rot2(delta * 3.0);
    vec3 p = ro + rd;

    float bass = 1.8 + 0.8 * sin(time);

    vec2 nudge = vec2(aspectRatio * 2, 0.0);
//    vec2 nudge = vec2(aspectRatio * 2 * (1 - fract(time / 10)), 0.0);

    focus = length(uv + nudge);
    focus = 1.8 / (1.0 + focus) * bass;

    focus2 = length(uv - nudge);
    focus2 = 4.5 / (1.0 + focus2 * focus2) / bass;

    vec3 q = vec3(fbm3d(p), fbm3d(p.yzx), fbm3d(p.zxy));

    float f = fbm3d(p + q);

    vec3 cc = q;
    cc *= 20.0 * f;

    cc.r += 4.5 * focus;
    cc.g += 2.0 * focus;
    cc.b += 7.0 * focus2;
    cc.r -= 3.5 * focus2;
    cc /= 20.0;
//    cc /= 100.0 / fract(time / 10);

    out_colour = vec4( cc,1.0);
}

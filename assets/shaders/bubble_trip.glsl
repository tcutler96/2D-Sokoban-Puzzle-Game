#version 330 core

uniform sampler2D base_surface;
uniform ivec2 resolution;
uniform float time;

in vec2 uv;
out vec4 out_colour;

#define R(p, a, t) mix(a * dot(p, a), p, cos(t)) + sin(t) * cross(p, a)
#define H(h) (cos((h) * 6.3 + vec3(0, 23, 21)) * 0.5 + 0.5)

void main() {
    vec3 r = vec3(0.5), c = vec3(0), d = normalize(vec3(uv - 0.5 * r.xy, r.y));
    float i = 0.0, s, e, g = 0.0, t = time;
	for(;i++ < 99.0;) {
        vec4 p = vec4(g * d, 0.07);
        p.z -= 0.5;
        p.xyz = R(p.xyz, normalize(H(t * 0.05)), t * 0.2);
        s = 1.0;
        for(int j = 0; j++ < 7;)
            p = 0.04 - abs(p - 0.2), s *= e = max(1.0 / dot(p, p), 1.3), p = abs(p.x < p.y ? p.wzxy : p.wzyx) * e-1.0;
        e = abs(length(p.wz * p.x)) / s;
	    g += e + 5e-4;
	    c += mix(vec3(1), H(log(s)), 0.5) * 0.025 / exp(i * i * e);
	}
	c *= c;
  out_colour = vec4(c, 1.0);
}

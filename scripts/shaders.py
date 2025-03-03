import moderngl as mgl
from array import array


class Shaders:
    def __init__(self, main):
        self.main = main
        self.context = mgl.create_context()
        self.quad_buffer = self.context.buffer(data=array('f', [-1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, -1.0, -1.0, 0.0, 1.0, 1.0, -1.0, 1.0, 1.0]))
        self.vertex_shader, self.fragment_shader = self.main.assets.shaders['vertex'], self.main.assets.shaders['fragment']
        self.program = self.context.program(vertex_shader=self.vertex_shader, fragment_shader=self.fragment_shader)
        self.set_uniforms(uniforms={'fps': self.main.fps, 'resolution': self.main.display.size, 'pixel': (1 / self.main.display.width, 1 / self.main.display.height)})
        self.render_object = self.context.vertex_array(program=self.program, content=[(self.quad_buffer, '2f 2f', 'vert', 'texcoord')], mode=mgl.TRIANGLE_STRIP)
        self.textures = self.create_textures(names=['base_surface', 'overlay_surface', 'buffer_surface', 'noise'], size=self.main.display.size)
        self.buffer = self.context.buffer(data=self.textures['base_surface'].read())
        self.textures['buffer_surface'].write(data=self.buffer)

    def set_uniforms(self, uniforms):
        for uniform, value in uniforms.items():
            try:
                self.program[uniform] = value
            except KeyError:
                pass

    def create_textures(self, names, size):
        textures = {}
        for location, name in enumerate(names):
            texture = self.context.texture(size=size, components=4)
            texture.filter = (mgl.NEAREST, mgl.NEAREST)
            if name != 'buffer_surface':
                texture.swizzle = 'BGRA'
            texture.use(location=location)
            self.set_uniforms(uniforms={f'{name}': location})
            # if name == 'noise':
            #     texture.write(data=self.main.assets.images['other']['noise'].get_view('1'))
            textures[name] = texture
        return textures

    def update(self, mouse_position):
        self.set_uniforms(uniforms={'time': self.main.runtime_seconds, 'mouse_posistion': mouse_position, 'mouse_active': self.main.events.mouse_active})

    def draw(self, surface, overlay):
        self.textures['base_surface'].write(data=surface.get_view('1'))
        self.textures['overlay_surface'].write(data=overlay.get_view('1'))
        self.render_object.render()
        self.context.screen.read_into(buffer=self.buffer, components=4)
        self.textures['buffer_surface'].write(data=self.buffer)

    def clean_up(self):
        self.textures['base_surface'].release()
        self.textures['overlay_surface'].release()
        self.textures['buffer_surface'].release()

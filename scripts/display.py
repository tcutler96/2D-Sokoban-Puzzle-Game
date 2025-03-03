import pygame as pg


class Display:
    def __init__(self, main, size):
        self.main = main
        self.size = self.width, self.height = size
        self.centre = self.half_width, self.half_height = self.width // 2, self.height // 2
        self.display = pg.Surface(size=self.size, flags=pg.SRCALPHA)
        self.overlay = pg.Surface(size=self.size, flags=pg.SRCALPHA)
        self.window = pg.display.set_mode(size=self.size, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.cursor_type = None
        self.show_cursor = True
        self.cursor = 'default'
        self.cursors = None
        self.set_cursors = []
        self.cursor_offsets = {'arrow': 0, 'hand': 5}
        # add ability to change game resolution...
        # surface layeras: background, game, map, menu, mouse
        # want to be able to apply a shader to a specific surface layer...

    def load_cursors(self):
        self.cursor_type = self.main.assets.settings['video']['cursor_type']
        self.cursors = {'system': {'arrow': pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW), 'hand': pg.cursors.Cursor(pg.SYSTEM_CURSOR_HAND)}, 'sprite': {'default': {}, 'held': {}}}
        for cursor in ['arrow', 'hand']:
            surface = self.main.assets.images['other'][cursor + '_cursor'].copy()
            self.cursors['sprite']['default'][cursor] = surface
            self.cursors['sprite']['held'][cursor] = pg.transform.scale(surface=surface, size=(surface.get_size()[0] * 0.9, surface.get_size()[1] * 0.9))

    def set_cursor(self, cursor=None):
        self.set_cursors.append(cursor)


    def update(self):
        self.display.fill(color=(0, 0, 0, 0))
        self.overlay.fill(color=(0, 0, 0, 0))
        if None in self.set_cursors:
            self.cursor = None
            self.show_cursor = False
            pg.mouse.set_visible(False)
        else:
            if self.cursor_type == 'sprite':
                pg.mouse.set_visible(False)
                if 'hand' in self.set_cursors:
                    self.cursor = 'hand'
                    self.show_cursor = True
                elif 'arrow' in self.set_cursors:
                    self.cursor = 'arrow'
                    self.show_cursor = True
            elif self.cursor_type == 'system':
                pg.mouse.set_visible(True)
                if 'hand' in self.set_cursors:
                    pg.mouse.set_cursor(self.cursors['system']['hand'])
                elif 'arrow' in self.set_cursors:
                    pg.mouse.set_cursor(self.cursors['system']['arrow'])
        self.set_cursors = []

    def draw(self):
        if self.main.events.mouse_active and self.show_cursor and self.cursor_type == 'sprite':
            self.overlay.blit(source=self.cursors['sprite']['held' if self.main.events.check_key(key='mouse_1', action='held') else 'default'][self.cursor],
                              dest=(self.main.events.mouse_position[0] - self.cursor_offsets[self.cursor], self.main.events.mouse_position[1]))

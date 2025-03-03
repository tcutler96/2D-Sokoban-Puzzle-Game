import pygame as pg


class MapCell:
    def __init__(self, main, level_name, sprite, blit_position, cell_size, offset, discovered, icons, player):
        self.main = main
        self.level_name = level_name
        self.sprite = sprite
        self.blit_position = blit_position
        self.cell_size = cell_size
        self.rect = pg.Rect((self.blit_position[0] + offset[0], self.blit_position[1] + offset[1]), (self.cell_size, self.cell_size))
        self.discovered = discovered
        self.icons = icons
        self.player = player
        self.hovered = False
        self.level_text = self.main.text_handler.add_text(text=self.level_name, position='top_right', alignment=('r', 'c'))

    def update_rect(self, offset):
        self.rect = pg.Rect((self.blit_position[0] + offset[0], self.blit_position[1] + offset[1]), (self.cell_size, self.cell_size))

    def update(self, mouse_position, offset, interpolating):
        self.hovered = False
        if interpolating:
            self.update_rect(offset=offset)
        if mouse_position and (self.discovered or self.main.debug) and self.rect.collidepoint(mouse_position):
            self.hovered = True
            if self.icons['teleporter'] or self.main.debug:
                self.main.display.set_cursor(cursor='hand')
                if self.main.events.check_key(key='mouse_1'):
                    return True

    def draw(self, surface, offset):
        if self.discovered or self.main.debug:
            if self.main.assets.settings['video']['map_colour'] != 'disabled':
                pg.draw.rect(surface=surface, color=self.main.assets.colours[self.main.assets.settings['video']['map_colour']], rect=self.rect)
            if self.hovered:
                self.level_text.activate()
                pg.draw.rect(surface=surface, color=self.main.assets.colours['cream'], rect=self.rect)
            surface.blit(source=self.sprite, dest=(self.blit_position[0] + offset[0], self.blit_position[1] + offset[1]))
            if self.player:
                surface.blit(source=self.main.assets.images['map']['player'], dest=(self.blit_position[0] + offset[0], self.blit_position[1] + offset[1]))
            if self.icons['teleporter']:
                surface.blit(source=self.main.assets.images['map']['teleporter'], dest=(self.blit_position[0] + offset[0] + 32, self.blit_position[1] + offset[1]))
        if self.icons['silver keys'] and self.main.assets.data['game']['part_one']:
            surface.blit(source=self.main.assets.images['map']['silver key'], dest=(self.blit_position[0] + offset[0], self.blit_position[1] + offset[1] + 32))
        elif self.icons['gold keys'] and self.main.assets.data['game']['part_two']:
            surface.blit(source=self.main.assets.images['map']['gold key'], dest=(self.blit_position[0] + offset[0], self.blit_position[1] + offset[1] + 32))
        if self.icons['silver gems'] and self.main.assets.data['game']['part_one']:
            surface.blit(source=self.main.assets.images['map']['silver gem'], dest=(self.blit_position[0] + offset[0] + 32, self.blit_position[1] + offset[1] + 32))
        elif self.icons['gold gems'] and self.main.assets.data['game']['part_two']:
            surface.blit(source=self.main.assets.images['map']['gold gem'], dest=(self.blit_position[0] + offset[0] + 32, self.blit_position[1] + offset[1] + 32))
        elif self.icons['cheeses'] and self.main.assets.data['game']['part_two']:
            surface.blit(source=self.main.assets.images['map']['cheese'], dest=(self.blit_position[0] + offset[0] + 32, self.blit_position[1] + offset[1] + 32))

import pygame.freetype
import pygame as pg
import os


class Utilities:
    def __init__(self, main):
        self.main = main
        self.shadow_offset = (8, 6)  # shadow offset needs to be variable depending on font size...
        self.neighbour_offsets = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        self.neighbour_auto_tile_map = {tuple(sorted([])): 'single', tuple(sorted([(0, -1)])): 'down end', tuple(sorted([(1, 0)])): 'left end', tuple(sorted([(0, 1)])): 'up end',
                                        tuple(sorted([(-1, 0)])): 'right end', tuple(sorted([(-1, 0), (1, 0)])): 'left right', tuple(sorted([(0, -1), (0, 1)])): 'up down',
                                        tuple(sorted([(1, 0), (0, 1)])): 'top left', tuple(sorted([(-1, 0), (1, 0), (0, 1)])): 'top', tuple(sorted([(-1, 0), (0, 1)])): 'top right',
                                        tuple(sorted([(0, -1), (0, 1), (-1, 0)])): 'right', tuple(sorted([(0, -1), (-1, 0)])): 'bottom right', tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 'bottom',
                                        tuple(sorted([(0, -1), (1, 0)])): 'bottom left', tuple(sorted([(0, -1), (1, 0), (0, 1)])): 'left', tuple(sorted([(-1, 0), (0, -1), (1, 0), (0, 1)])): 'centre'}
        self.corner_offsets = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        self.corner_auto_tile_map = {(-1, -1): 'tl', (1, -1): 'tr', (1, 1): 'br', (-1, 1): 'bl'}

    def position_str_to_tuple(self, position):
        return tuple([int(number) for number in position.replace('(', '').replace(')', '').split(', ')])

    def level_and_position(self, level, position):
        return level + ' - ' + str(tuple(position))

    def get_opposite_movement(self, movement):
        return movement[0] * -1, movement[1] * -1

    def load_image(self, path):
        if path.endswith('.png') or path.endswith('jpg'):
            image = pg.image.load(path).convert()
            image.set_colorkey((0, 0, 0))
            return image

    def load_images(self, path):
        images = []
        for image_name in sorted(os.listdir(path=path)):
            images.append(self.load_image(path=path + '/' + image_name))
        return images

    def get_colour(self, colour, alpha=0):
        if colour in self.main.assets.colours:
            colour = self.main.assets.colours[colour]
        else:
            colour = self.main.assets.colours['white']
        if alpha:
            colour = (*colour, alpha)
        return colour

    def draw_text(self, text, surface=None, position=(0, 0), alignment=('c', 'c'), colour=(142, 184, 158), bg_colour=None, shadow_colour=(22, 13, 19), size=10, max_width=0, max_height=0, font='Kiwi Soda', style=None):
        # out option for outline, draw font in all four cardinal directions...
        if font not in self.main.assets.fonts:
            self.main.assets.fonts[font] = pg.freetype.SysFont(name=font, size=0, bold=False, italic=False)
        font_object = self.main.assets.fonts[font]
        font_object.underline = False
        font_object.oblique = False
        font_object.strong = False
        if style:
            if not isinstance(style, list):
                style = [style]
            if 'underline' in style:
                font_object.underline = True
            if 'itallic' in style:
                font_object.oblique = True
            if 'bold' in style:
                font_object.strong = True
        if max_width:
            while font_object.get_rect(text=text, size=size).width > max_width:
                size -= 1
        if max_height:
            while font_object.get_rect(text=text, size=size).height > max_height:
                size -= 1
        _, _, width, height = font_object.get_rect(text=text, size=size)
        if alignment:
            if alignment[0] == 'c':
                position = (position[0] - width // 2, position[1])
            elif alignment[0] == 'r':
                position = (position[0] - width, position[1])
            if alignment[1] == 'c':
                position = (position[0], position[1] - height // 2)
            elif alignment[1] == 'b':
                position = (position[0], position[1] - height)
        if surface:
            if shadow_colour:
                font_object.render_to(surf=surface, dest=(position[0] + self.shadow_offset[0], position[1] + self.shadow_offset[1]), text=text, fgcolor=shadow_colour, bgcolor=bg_colour, size=size)
            font_object.render_to(surf=surface, dest=position, text=text, fgcolor=colour, bgcolor=bg_colour if not shadow_colour else None, size=size)
            return pg.Rect(*position, width, height)
        else:
            if shadow_colour:
                main_surface = font_object.render(text=text, fgcolor=colour, size=size)[0]
                shadow_surface = font_object.render(text=text, fgcolor=shadow_colour, size=size)[0]
                surface = pg.Surface(size=(width + self.shadow_offset[0], height + self.shadow_offset[1]), flags=pg.SRCALPHA)
                surface.blit(source=shadow_surface, dest=self.shadow_offset)
                surface.blit(source=main_surface, dest=(0, 0))
                return surface
            else:
                return font_object.render(text=text, fgcolor=colour, bgcolor=bg_colour, size=size)[0]

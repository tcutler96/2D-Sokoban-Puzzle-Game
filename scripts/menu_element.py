import pygame as pg


class MenuElement:
    def __init__(self, main, name, position, element_data):
        self.main = main
        self.data = {'title_font': 'Mleitod', 'title_size': 128, 'button_font': 'Kiwi Soda', 'button_size': 64}
        self.name = name
        if isinstance(element_data, str):
            self.element_type = element_data
        else:
            self.element_type, self.button_type, self.button_response = element_data
        # draw text using text handler, so that is can handle fade in/ out and mouse collision...
        if self.element_type == 'title':
            self.surfaces = {'default': self.main.utilities.draw_text(text=self.name.upper(), size=self.data['title_size'], font=self.data['title_font'], style='underline')}
        elif self.element_type == 'button':
            self.surfaces = {'default': self.main.utilities.draw_text(text=self.name + (':' if self.button_type == 'option' else ''), size=self.data['button_size'], font=self.data['button_font']),
                             'hovered': self.main.utilities.draw_text(text=self.name + (':' if self.button_type == 'option' else ''),
                                                                      colour=self.main.assets.colours['green'], size=self.data['button_size'], font=self.data['button_font'])}
            if self.button_type == 'option':
                self.option_surfaces = {'default': [], 'hovered': []}
                for option in self.button_response:
                    self.option_surfaces['default'].append(self.main.utilities.draw_text(text=option, size=self.data['button_size'], font=self.data['button_font']))
                    self.option_surfaces['hovered'].append(self.main.utilities.draw_text(text=option, colour=self.main.assets.colours['green'], size=self.data['button_size'], font=self.data['button_font']))
                self.option_surface = None
        self.active_surface = 'default'
        self.surface = None
        self.alpha_start = 0
        self.alpha = self.alpha_start
        self.alpha_step = 25
        self.offset_start = 50
        self.offset = self.offset_start
        self.offset_step = 10
        self.width = self.surfaces[self.active_surface].get_width() - self.main.utilities.shadow_offset[0]
        self.height = self.surfaces[self.active_surface].get_height() - self.main.utilities.shadow_offset[1]
        self.option_width = int(self.main.display_size[0] * 0.7)
        self.position = (position[0] - (self.option_width // 2 if self.element_type == 'button' and self.button_type == 'option' else self.width // 2), position[1] - self.height // 2)
        if self.element_type == 'button' and self.button_type == 'option':
            max_height = self.height
            self.option_positions = []
            for option_surface in self.option_surfaces['default']:
                width, height = option_surface.get_size()
                max_height = max(max_height, height)
                self.option_positions.append((self.position[0] + self.option_width - width, self.position[1] - max(height, self.height) // 2 + self.height // 2))
            self.rect = pg.Rect(self.position[0], self.position[1] - max_height // 2 + self.height // 2, self.option_width, max_height)
        else:
            self.rect = pg.Rect(self.position[0], self.position[1], self.width, self.height)
        self.initial_rect = self.rect
        self.centre = self.rect.center

    def update_rect(self, scroll=None):
        if isinstance(scroll, int):
            self.rect = pg.Rect(self.position[0], self.position[1] - scroll, self.width, self.height)
        else:
            self.rect = self.initial_rect

    def update(self, mouse_position, scroll):
        if self.alpha < 255:
            self.alpha = min(self.alpha + self.alpha_step, 255)
        if self.offset:
            self.offset = max(self.offset - self.offset_step, 0)
        if self.alpha == 255 and self.offset == 0 and not self.main.transition.transitioning:
            if self.element_type == 'button':
                self.active_surface = 'default'
                if self.main.events.check_key(key=['mouse_3', 'escape']) and self.name in ['Back', 'Resume', 'No']:
                    self.main.events.remove_key(key='mouse_3')
                    self.main.events.remove_key(key='escape')
                    return self.button_type, self.button_response, self.name
                if isinstance(scroll, int):
                    self.update_rect(scroll=scroll)
                if self.rect.collidepoint(mouse_position):
                    self.active_surface = 'hovered'
                    self.main.display.set_cursor(cursor='hand')
                    if self.main.events.check_key(key='mouse_1'):
                        if self.button_type == 'option':
                            self.button_response.append(self.button_response.pop(0))
                            for _, a in self.option_surfaces.items():
                                a.append(a.pop(0))
                            self.option_positions.append(self.option_positions.pop(0))
                        return self.button_type, self.button_response, self.name

    def draw(self, overlay, scroll):
        if self.alpha:
            if self.element_type == 'title':
                self.surface = self.main.utilities.draw_text(text=self.name.upper(), size=self.data['title_size'], font=self.data['title_font'], style='underline')
            else:
                self.surface = self.surfaces[self.active_surface].copy()
            if self.alpha < 255:
                self.surface.set_alpha(self.alpha)
            overlay.blit(source=self.surface, dest=(self.position[0], self.position[1] - self.offset - scroll))
            if self.element_type == 'button' and self.button_type == 'option':
                self.option_surface = self.option_surfaces[self.active_surface][0].copy()
                if self.alpha < 255:
                    self.option_surface.set_alpha(self.alpha)
                overlay.blit(source=self.option_surface, dest=(self.option_positions[0][0], self.option_positions[0][1] - self.offset - scroll))

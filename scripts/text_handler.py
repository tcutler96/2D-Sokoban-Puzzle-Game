from scripts.text_element import TextElement


class TextHandler:
    def __init__(self, main):
        self.main = main
        self.text = {}
        # by storing text elements in text handler, we can choose not to set a position and instead pass position in when we activate text...
        self.text2 = {'menus': {},
                      'level_editor': {'toolbar': {}},
                      'game': {'reset level': self.add_text(text='move to reset', position='centre'), 'warp': self.add_text(text=f"press 'e' to warp", position='top'),
                               'set warp': self.add_text(text=f"press 'e' to set warp", position='top'), 'warp?': self.add_text(text=f"¡ ¿ ? !  press 'e' to warp  ! ? ¿ ¡", position='top'),
                               'steps': {steps: self.add_text(text=str(steps), position='top_left', alignment=('l', 'c')) for steps in range(9)},
                               'collectables': {collectable: self.add_text(text=f'{collectable[:-1]} collected!', position='bottom') for collectable in self.main.assets.data['game']['collectables']},
                               'locks': {},
                               'signs': {'(-2, 2) - (6, 8)': self.add_text(text='this is a sign text test', position=(self.main.display.half_width, 320))}}}

    def get_text_position(self, position):
        if position == 'top_left':
            position = (16, 32)
        elif position == 'top':
            position = (self.main.display.half_width, 32)
        elif position == 'top_right':
            position = (self.main.display.width - 16, 32)
        elif position == 'left':
            position = (16, self.main.display.half_height)
        elif position == 'centre':
            position = self.main.display.centre
        elif position == 'right':
            position = (self.main.display.width - 16, self.main.display.half_height)
        elif position == 'bottom_left':
            position = (16, self.main.display.height - 32)
        elif position == 'bottom':
            position = (self.main.display.half_width, self.main.display.height - 32)
        elif position == 'bottom_right':
            position = (self.main.display.width - 16, self.main.display.height - 32)
        else:
            position = (0, 0)
        return position

    def add_text(self, text, position, alignment=('c', 'c'), colour=(142, 184, 158), bg_colour=None, shadow_colour=(22, 13, 19),
                 size=48, max_width=0, max_height=0, font='Kiwi Soda', style=None, draw_onto='surface', active=False, delay=0, duration=0, interactable=False):
        if isinstance(position, str):
            position = self.get_text_position(position=position)
        if isinstance(colour, str):
            colour = self.main.assets.colours[colour]
        surface = self.main.utilities.draw_text(text=text, colour=colour, bg_colour=bg_colour, shadow_colour=shadow_colour, size=size, max_width=max_width, max_height=max_height, font=font, style=style)
        surface.set_alpha(0)
        if shadow_colour:
            position = (position[0] + self.main.utilities.shadow_offset[0] // 2, position[1] + self.main.utilities.shadow_offset[1] // 2)
        if alignment:
            if alignment[0] == 'c':
                position = (position[0] - surface.get_width() // 2, position[1])
            elif alignment[0] == 'r':
                position = (position[0] - surface.get_width(), position[1])
            if alignment[1] == 'c':
                position = (position[0], position[1] - surface.get_height() // 2)
            elif alignment[1] == 'b':
                position = (position[0], position[1] - surface.get_height())
        text_id = 0
        while text_id in self.text:
            text_id += 1
        text_element = TextElement(main=self.main, text=text, surface=surface, position=position, draw_onto=draw_onto, active=active, delay=delay * self.main.fps, duration=duration * self.main.fps, interactable=interactable)
        self.text[text_id] = text_element
        return text_element

    def update(self, mouse_position):
        delete_text = []
        for text_id, text_element in self.text.items():
            if text_element.delete:
                delete_text.append(text_id)
            else:
                text_element.update(mouse_position=mouse_position)
        for text_id in delete_text:
            del self.text[text_id]

    def draw(self, surface, overlay):
        for text_element in self.text.values():
            text_element.draw(surface=surface, overlay=overlay)

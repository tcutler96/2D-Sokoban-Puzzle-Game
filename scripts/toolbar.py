import pygame as pg


class Toolbar:
    def __init__(self, main):
        self.main = main
        self.sprite_size = 32
        self.text_position = (648, 32)
        self.element_choices = {'objects': {'no object': ['no object'], 'player': ['idle', 'dead'], 'permanent flag': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                                            'temporary flag': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], 'rock': ['rock'], 'statue': ['statue'],
                                            'collectable': ['silver key', 'silver gem', 'gold key', 'gold gem', 'cheese']},
                                'tiles': {'no tile': ['no tile'], 'wall': ['auto-tile'], 'ice': ['ice'], 'conveyor': ['up', 'right', 'down', 'left'], 'spike': ['spike'],
                                          'player spawner': ['player spawner'], 'splitter': ['vertical', 'horizontal'], 'barrier': ['vertical', 'horizontal'],
                                          'teleporter': ['reciever', 'sender', 'portal'], 'lock': ['lock'], 'sign': ['sign'], 'gem reseter': ['gem reseter']}}
        self.button_choices = {'top': {'Reset Level': 'reset', 'Toggle Grid': 'grid', 'Play Level': 'play'}, 'right': {'Save Level': 'save', 'Load Level': 'load', 'Quit to Main Menu': 'quit'}}
        self.cell_marker = self.main.assets.images['toolbar']['marker']
        self.toolbar = self.get_toolbar()
        self.hovered_element = [None, None]
        self.selected_object = ['no object', 0]
        self.selected_tile = ['no tile', 0]

    def get_toolbar(self):
        toolbar = {'background_rects': [pg.Rect(8, 8, 48 * (len(self.element_choices['objects']) + 1), 48),pg.Rect(8, 8, 48, 48 * (len(self.element_choices['tiles']) + 1)),
                                        pg.Rect(self.main.display.width - 8, 8, -48 * (len(self.button_choices['top']) + 1), 48),  pg.Rect(self.main.display.width - 8, 8, -48, 48 * (len(self.button_choices['top']) + 1))]}
        buttons = {}
        for button_type in self.button_choices:
            for button_count, button_name in enumerate(self.button_choices[button_type]):
                button_position = (self.main.display.width - 48 - (48 * (button_count + 1) if button_type == 'top' else 0), 16 + (48 * (button_count + 1) if button_type == 'right' else 0))
                buttons[button_name] = {'position': button_position, 'sprite': self.main.assets.images['toolbar'][self.button_choices[button_type][button_name]],
                                        'rect': pg.Rect(button_position[0] - 8, button_position[1] - 8, 48, 48),
                                        'text': self.main.text_handler.add_text(text=button_name, position=self.text_position, alignment=('c', 'c'))}
        toolbar['buttons'] = buttons
        elements = {}
        for element_type in self.element_choices:
            for name_count, element_name in enumerate(self.element_choices[element_type]):
                if element_name == 'no object':
                    element_data = {'position': [(64, 16)], 'sprites': [self.main.assets.images['toolbar']['empty']], 'rects': [pg.Rect(56, 8, 48, 48)],
                                    'text': [self.main.text_handler.add_text(text='no object', position=self.text_position, alignment=('c', 'c'))], 'num_choices': 1, 'element_type': 'object'}
                elif element_name == 'no tile':
                    element_data = {'position': [(16, 64)], 'sprites': [self.main.assets.images['toolbar']['empty']], 'rects': [pg.Rect(8, 56, 48, 48)],
                                    'text': [self.main.text_handler.add_text(text='no tile', position=self.text_position, alignment=('c', 'c'))], 'num_choices': 1, 'element_type': 'tile'}
                else:
                    element_data = {'position': [], 'sprites': [], 'rects': [], 'text': []}
                    for state_count, element_state in enumerate(self.element_choices[element_type][element_name]):
                        sprite_position = (16 + (48 * (name_count + 1) if element_type == 'objects' else 0) + (48 * state_count if element_type == 'tiles' else 0),
                                           16 + (48 * (name_count + 1) if element_type == 'tiles' else 0) + (48 * state_count if element_type == 'objects' else 0))
                        element_data['position'].append(sprite_position)
                        if element_name == 'player' and element_state == 'idle':
                            sprite = pg.transform.scale(surface=self.main.assets.get_sprite(name='player respawn', state='player respawn', sprite_size='default', animated=False), size=(self.sprite_size, self.sprite_size))
                            sprite.blit(source= pg.transform.scale(surface=self.main.assets.get_sprite(name='player', state='idle', sprite_size='default', animated=False), size=(self.sprite_size, self.sprite_size)), dest=(0, 0))
                        else:
                            sprite = pg.transform.scale(surface=self.main.assets.get_sprite(name=element_name, state=element_state, sprite_size='default', animated=False), size=(self.sprite_size, self.sprite_size))
                        element_data['sprites'].append(sprite)
                        element_data['rects'].append(pg.Rect(sprite_position[0] - 8, sprite_position[1] - 8, 48, 48))
                        element_data['text'].append(self.main.text_handler.add_text(text=element_name + (' - ' + element_state if element_state != element_name else ''),
                                                                                    position=self.text_position, alignment=('c', 'c')))
                    element_data['num_choices'] = len(element_data['position'])
                    element_data['element_type'] = element_type[:-1]
                elements[element_name] = element_data
        toolbar['elements'] = elements
        return toolbar

    def set_toolbar(self, elements):
        self.selected_object = ['no object', 0]
        self.selected_tile = ['no tile', 0]
        if elements['object']:
            self.selected_object = [elements['object']['name'], self.element_choices['objects'][elements['object']['name']].index(elements['object']['state'])]
        elif elements['player']:
            self.selected_object = [elements['player']['name'], self.element_choices['objects'][elements['player']['name']].index(elements['player']['state'])]
        if elements['tile']:
            self.selected_tile = [elements['tile']['name'], self.element_choices['tiles'][elements['tile']['name']].index(elements['tile']['state'])]
        elif elements['vertical_barrier']:
            self.selected_tile = [elements['vertical_barrier']['name'], self.element_choices['tiles'][elements['vertical_barrier']['name']].index(elements['vertical_barrier']['state'])]
        elif elements['horizontal_barrier']:
            self.selected_tile = [elements['horizontal_barrier']['name'], self.element_choices['tiles'][elements['horizontal_barrier']['name']].index(elements['horizontal_barrier']['state'])]


    def update(self, mouse_position):
        hovered_element = self.hovered_element
        selected_elememt = None
        self.hovered_element = [None, None]
        for button_name, button_data in self.toolbar['buttons'].items():
            button_data['text'].deactivate()
            if button_data['rect'].collidepoint(mouse_position):
                self.main.display.set_cursor(cursor='hand')
                self.hovered_element = button_name
                button_data['text'].activate()
                if self.main.events.check_key(key='mouse_1'):
                    selected_elememt = ['button', button_name]
                    button_data['text'].deactivate()
        if not selected_elememt:
            for element_name, element_data in self.toolbar['elements'].items():
                for count, (rect, text) in enumerate(zip(element_data['rects'], element_data['text'])):
                    if count and element_name != hovered_element[0]:
                        break
                    text.deactivate()
                    if rect.collidepoint(mouse_position):
                        self.hovered_element = [element_name, count]
                        self.main.display.set_cursor(cursor='hand')
                        text.activate()
                        if self.main.events.check_key(key='mouse_1'):
                            if element_data['element_type'] == 'object':
                                if [element_name, count] != self.selected_object:
                                    self.selected_object = [element_name, count]
                                    selected_elememt = [element_data['element_type'], self.selected_object[0], self.element_choices['objects'][self.selected_object[0]][self.selected_object[1]]]
                            elif element_data['element_type'] == 'tile':
                                if [element_name, count] != self.selected_tile:
                                    self.selected_tile = [element_name, count]
                                    selected_elememt = [element_data['element_type'], self.selected_tile[0], self.element_choices['tiles'][self.selected_tile[0]][self.selected_tile[1]]]
        return selected_elememt

    def draw(self, overlay):
        for background_rect in self.toolbar['background_rects']:
            pg.draw.rect(surface=overlay, color=self.main.assets.colours['dark_purple'], rect=background_rect, border_radius=5)
        for button_name, button_data in self.toolbar['buttons'].items():
            overlay.blit(source=button_data['sprite'], dest=button_data['position'])
            if button_name == self.hovered_element:
                overlay.blit(source=self.cell_marker, dest=(button_data['position'][0] - 8, button_data['position'][1] - 8))
        for element_name, element_data in self.toolbar['elements'].items():
            if element_name == self.hovered_element[0] and element_data['num_choices'] > 1:
                pg.draw.rect(surface=overlay, color=self.main.assets.colours['cream'],
                             rect=pg.Rect(element_data['rects'][0][0], element_data['rects'][0][1], 48 * element_data['num_choices'] if element_data['element_type'] == 'tile' else 48,
                                          48 * element_data['num_choices'] if element_data['element_type'] == 'object' else 48), border_radius=5)
            if element_name != self.hovered_element[0] and element_name == (self.selected_object[0] if element_data['element_type'] == 'object' else self.selected_tile[0]):
                pg.draw.rect(surface=overlay, color=self.main.assets.colours['bright_green'], rect=pg.Rect(element_data['position'][0][0] - 4, element_data['position'][0][1] - 4, 40, 40), border_radius=5)
                overlay.blit(source=element_data['sprites'][self.selected_object[1] if element_data['element_type'] == 'object' else self.selected_tile[1]],
                             dest=element_data['position'][0])
            else:
                for count, (position, sprite) in enumerate(zip(element_data['position'] if element_name == self.hovered_element[0] else [element_data['position'][0]],
                                            element_data['sprites'] if element_name == self.hovered_element[0] else [element_data['sprites'][0]])):
                    if [element_name, count] == (self.selected_object if element_data['element_type'] == 'object' else self.selected_tile):
                        pg.draw.rect(surface=overlay, color=self.main.assets.colours['bright_green'], rect=pg.Rect(position[0] - 4, position[1] - 4, 40, 40), border_radius=5)
                    overlay.blit(source=sprite, dest=position)
                    if element_name == self.hovered_element[0] and count == self.hovered_element[1]:
                        overlay.blit(source=self.cell_marker, dest=(position[0] - 8, position[1] - 8))

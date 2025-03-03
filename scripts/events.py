import pygame as pg


class Events:
    def __init__(self, main):
        self.main = main
        self.keys = {'pressed': [], 'held': [], 'unpressed': [], 'last_pressed': []}
        self.last_pressed_amount = 25
        self.modifier_keys = {'left shift': False, 'left ctrl': False, 'left alt': False}
        self.mouse_position = [0, 0]
        self.mouse_moved = False
        self.mouse_movement = [0, 0]
        self.mouse_active = False

    def update(self):
        self.keys['pressed'] = []
        self.keys['unpressed'] = []
        self.mouse_moved = False
        self.mouse_movement = (0, 0)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.main.transition.start(response=['game_state', 'quit'])
            if event.type == pg.KEYDOWN:
                input = pg.key.name(event.key)
                self.add_key(key=input, action='pressed')
                self.add_key(key=input, action='held')
            if event.type == pg.KEYUP:
                input = pg.key.name(event.key)
                self.add_key(key=input, action='unpressed')
                self.remove_key(key=input, action='held')
            if event.type == pg.MOUSEBUTTONDOWN:
                input = f'mouse_{event.button}'
                self.add_key(key=input, action='pressed')
                self.add_key(key=input, action='held')
            if event.type == pg.MOUSEBUTTONUP:
                input = f'mouse_{event.button}'
                self.add_key(key=input, action='unpressed')
                self.remove_key(key=input, action='held')
            if event.type == pg.MOUSEMOTION:
                mouse_position = list(pg.mouse.get_pos())
                self.mouse_moved = True
                self.mouse_movement = [mouse_position[0] - self.mouse_position[0], mouse_position[1] - self.mouse_position[1]]
                self.mouse_position = mouse_position
                self.mouse_active = pg.mouse.get_focused()

    def add_key(self, key, action='pressed'):
        if key in self.modifier_keys:
            self.modifier_keys[key] = True
        elif key not in self.keys[action]:
            self.keys[action].append(key)
            if action == 'pressed':
                self.keys['last_pressed'].append(key)
                if len(self.keys['last_pressed']) > self.last_pressed_amount:
                    self.keys['last_pressed'].pop(0)

    def remove_key(self, key, action='pressed'):
        if key in self.modifier_keys:
            self.modifier_keys[key] = False
        elif key in self.keys[action]:
            self.keys[action].remove(key)

    def check_key(self, key, action='pressed', modifier=None):
        if action == 'last_pressed':
            if ''.join(self.keys['last_pressed']).endswith(key):
                self.keys['last_pressed'] = []
                return True
        else:
            if modifier:
                if not isinstance(modifier, list):
                    modifier = [modifier]
                modifier_pressed = True
                for modifier_key in modifier:
                    modifier_key = f'left {modifier_key}'
                    if modifier_key in self.modifier_keys:
                        modifier_pressed = modifier_pressed and self.modifier_keys[modifier_key]
                    else:
                        return False
                if not modifier_pressed:
                    return False
            if isinstance(key, list):
                keys = list(set(key) & set(self.keys[action]))
                if keys:
                    return keys
            elif key in self.keys[action]:
                return True

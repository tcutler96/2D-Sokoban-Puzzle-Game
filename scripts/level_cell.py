import pygame as pg
from copy import deepcopy

class LevelCell:
    def __init__(self, main, position, elements=None, object_data=None):
        self.main = main
        self.position = position
        self.empty_elements = {'object': None, 'player': None, 'tile': None, 'vertical_barrier': None, 'horizontal_barrier': None}
        if not elements:
            self.elements = deepcopy(self.empty_elements)
        else:
            self.elements = elements
        self.default_object_data = {'facing_right': True, 'blit_position': [self.position], 'moved': False, 'last_moved': None, 'slid': False, 'last_slid': None,
                                    'conveyed': False, 'last_conveyed': None, 'split': False, 'last_split': None, 'bumped': False, 'original_position': self.position}
        self.object_data = object_data if object_data else {'object': {'name': self.elements['object']['name']} | deepcopy(self.default_object_data) if self.elements['object'] else None,
                                                            'player': {'name': self.elements['player']['name']} | deepcopy(self.default_object_data) if self.elements['player'] else None}
        self.exclusive_tiles = ['wall', 'teleporter', 'lock']
        self.conveyor_movements = {'up': (0, -1), 'right': (1, 0), 'down': (0, 1), 'left': (-1, 0)}
        self.conveyor_opposites = {'up': 'down', 'right': 'left', 'down': 'up', 'left': 'right'}
        self.splitter_movements = {'vertical': [(0, -1), (0, 1)], 'horizontal': [(-1, 0), (1, 0)]}
        self.adjacent_directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]

    def empty(self):
        self.elements = deepcopy(self.empty_elements)

    def is_empty(self, elements=None):
        if not elements:
            elements = self.elements
        if elements == self.empty_elements:
            return True

    def reset_object_data(self, object_type='object'):
        self.object_data[object_type] = {'name': self.elements[object_type]['name']} | deepcopy(self.default_object_data)

    def check_element(self, name, state=None):
        if not isinstance(name, list):
            name = [name]
        for element in self.elements.values():
            if element and element['name'] in name:
                if state:
                    if not isinstance(state, list):
                        state = [state]
                    if element['state'] in state:
                        return True
                else:
                    return True

    def add_element(self, element):
        element_type, element_name, element_state = element
        if element_name == 'no object':
            self.elements['object'] = None
            self.elements['player'] = None
        elif element_name == 'no tile':
            self.elements['tile'] = None
            self.elements['vertical_barrier'] = None
            self.elements['horizontal_barrier'] = None
        else:
            if element_type == 'object':
                self.elements['vertical_barrier'] = None
                self.elements['horizontal_barrier'] = None
                if self.check_element(name=self.exclusive_tiles):
                    self.elements['tile'] = None
                if element_name == 'player':
                    self.elements['object'] = None
                    self.elements['player'] = {'name': 'player', 'state': element_state}
                    if element_state == 'idle':
                        self.elements['tile'] = None
                else:
                    self.elements['object'] = {'name': element_name, 'state': element_state}
                    self.elements['player'] = None
            elif element_type == 'tile':
                self.elements['vertical_barrier'] = None
                self.elements['horizontal_barrier'] = None
                if element_name == 'wall':
                    self.elements['tile'] = {'name': 'wall', 'state': 'auto-tile'}
                    self.elements['object'] = None
                    self.elements['player'] = None
                elif element_name == 'teleporter':
                    self.elements['tile'] = {'name': 'teleporter', 'state': element_state}
                    self.elements['object'] = None
                    self.elements['player'] = None
                elif element_name == 'lock':
                    self.elements['tile'] = {'name': 'lock', 'state': 'lock'}
                    self.elements['object'] = None
                    self.elements['player'] = None
                elif element_name == 'barrier':
                    self.elements['tile'] = None
                    self.elements['object'] = None
                    self.elements['player'] = None
                    self.elements[element_state + '_' + element_name] = {'name': 'barrier', 'state': element_state}
                else:
                    self.elements['tile'] = {'name': element_name, 'state': element_state}
                    if self.check_element(name='player', state='idle'):
                        self.elements['player'] = None

    def set_elements(self, elements):
        if self.is_empty(elements=elements):
            self.elements = deepcopy(self.empty_elements)
        else:
            if elements['vertical_barrier']:
                self.elements['vertical_barrier'] = elements['vertical_barrier']
            elif elements['horizontal_barrier']:
                self.elements['horizontal_barrier'] = elements['horizontal_barrier']
            else:
                if elements['object']:
                    if self.check_element(name=self.exclusive_tiles):
                        self.elements['tile'] = None
                    self.elements['object'] = elements['object']
                    if self.check_element(name='player', state='idle'):
                        self.elements['player'] = None
                if elements['player']:
                    if self.check_element(name=self.exclusive_tiles):
                        self.elements['tile'] = None
                    self.elements['player'] = elements['player']
                    if self.check_element(name=['rock', 'statue']):
                        self.elements['object'] = None
                if elements['tile']:
                    self.elements['tile'] = elements['tile']
                    if elements['tile']['name'] in self.exclusive_tiles:
                        self.elements['object'] = None
                        self.elements['player'] = None
                    if self.check_element(name='player', state='idle'):
                        self.elements['player'] = None

    def check_movement(self, object_type, movement, new_cell, push_allowed=True, ignore_barriers=False):
        if new_cell:
            object_name = self.elements[object_type]['name']
            if self.main.debug:
                return True, None
            if not ignore_barriers:
                if movement[0] > 0 and self.elements['vertical_barrier']:
                    return False, 'barrier'
                if movement[0] < 0 and new_cell.elements['vertical_barrier']:
                    return False, 'barrier'
                if movement[1] > 0 and self.elements['horizontal_barrier']:
                    return False, 'barrier'
                if movement[1] < 0 and new_cell.elements['horizontal_barrier']:
                    return False, 'barrier'
            if new_cell.elements['tile'] and new_cell.elements['tile']['name'] == 'wall':
                return False, 'tile'
            if new_cell.elements['tile'] and new_cell.elements['tile']['name'] == 'lock':
                return False, 'tile'
            if new_cell.elements['object']:
                if new_cell.elements['object']['name'] == 'permanent flag' and object_name != 'player':
                    if not push_allowed or not self.main.game_states['game'].move_object(cell=new_cell, object_type='object', movement=movement):
                        return False, 'object'
                elif new_cell.elements['object']['name'] == 'temporary flag' and object_name != 'player':
                    if not push_allowed or not self.main.game_states['game'].move_object(cell=new_cell, object_type='object', movement=movement):
                        return False, 'object'
                elif new_cell.elements['object']['name'] == 'rock':
                    if not push_allowed or not self.main.game_states['game'].move_object(cell=new_cell, object_type='object', movement=movement):
                        return False, 'object'
                elif new_cell.elements['object']['name'] == 'statue':
                    if not push_allowed or not self.main.game_states['game'].move_object(cell=new_cell, object_type='object', movement=movement):
                        return False, 'object'
                elif new_cell.elements['object']['name'] == 'collectable' and object_name != 'player':
                    if not push_allowed or not self.main.game_states['game'].move_object(cell=new_cell, object_type='object', movement=movement):
                        return False, 'object'
            if new_cell.elements['player'] and object_name in ['player', 'rock', 'statue']:
                if not push_allowed or not self.main.game_states['game'].move_object(cell=new_cell, object_type='player', movement=movement):
                    return False, 'player'
            return True, None
        else:
            return False, 'edge'

    def split_cell(self, level, queue=None):  # move back into game class?
        # if three splitters attempt to split to the same cell, then the 'third' split succeeds when it shouldnt...
        # this method does not work in the case where we attempt to split an object to another splitter that has already split...
        # we dont take into account the object that was on the second splitter when determining whether the first shopuld split or not...
        # unaware of any levels that this directly impacts making them impossible to complete...
        # we could add an additional check whenever we are about to split something, look at the other two directions (that were not splitting in) and check if theres a splitter there
        # if there is and it has an object that has not already been split, then trigger it first...
        movements = self.splitter_movements[self.elements['tile']['state'].split(' ')[0]]
        new_cells = [level.get_new_cell(position=self.position, movement=movement) for movement in movements]
        if queue:
            queue.append(self.position)
        else:
            queue = [self.position]
        for object_type, object_data in self.object_data.items():
            if object_data and not object_data['split']:
                respawn_flag = False
                if object_type == 'object' and self.check_element(name='permanent flag') and self.position in level.current_respawn[1]:
                    respawn_flag = True
                    level.current_respawn[1].remove(self.position)
                for movement, new_cell in zip(movements, new_cells):
                    if new_cell:
                        check_movement = self.check_movement(object_type=object_type, movement=movement, new_cell=new_cell, push_allowed=False, ignore_barriers=True)
                        if (new_cell.position not in queue and new_cell.check_element(name='splitter') and
                                ((new_cell.elements['object'] and not new_cell.object_data['object']['split']) or
                                 (new_cell.elements['player'] and not new_cell.object_data['player']['split']))):
                            new_cell.split_cell(level=level, queue=queue)
                        if check_movement[0]:
                            new_cell.elements[object_type] = deepcopy(self.elements[object_type])
                            new_cell.object_data[object_type] = deepcopy(self.object_data[object_type])
                            new_cell.object_data[object_type]['blit_position'] = [new_cell.position]
                            new_cell.object_data[object_type]['split'] = True
                            new_cell.object_data[object_type]['last_split'] = movement
                            if respawn_flag:
                                level.current_respawn[1].append(new_cell.position)
                        elif check_movement[1] in new_cell.object_data and new_cell.object_data[check_movement[1]] and new_cell.object_data[check_movement[1]]['split']:
                                new_cell.elements[check_movement[1]] = None
                                new_cell.object_data[check_movement[1]] = None
                self.elements[object_type] = None
                self.object_data[object_type] = None
        return queue

    def draw(self, surface, animated, alpha=255, element_types=None):
        for element_type, element in self.elements.items():
            if element_type in element_types and element:
                sprite = self.main.assets.get_sprite(name=element['name'], state=element['state'], animated=animated)
                if sprite:
                    if alpha != 255:
                        sprite.set_alpha(alpha)
                    if element_type in ['object', 'player'] and self.object_data[element_type] and not self.object_data[element_type]['facing_right']:
                        sprite = pg.transform.flip(surface=sprite, flip_x=True, flip_y=False)
                    if element_type in self.object_data and self.object_data[element_type]:
                        position = self.object_data[element_type]['blit_position'][0]
                    else:
                        position = self.position
                    surface.blit(source=sprite, dest=(position[0] * self.main.sprite_size + (4 if element_type == 'vertical_barrier' else 0),
                                                      position[1] * self.main.sprite_size + (4 if element_type == 'horizontal_barrier' else 0)))

from scripts.level_cell import LevelCell
from copy import deepcopy
import pygame as pg
import json
import os


class Level:
    def __init__(self, main):
        self.main = main
        self.level_offset = (64, 64)
        self.sprite_size = self.main.sprite_size
        self.grid_size = 16
        self.level_size = (1024, 1024)
        self.animated = True
        self.show_grid = False
        self.mouse_cell_alpha = 100
        self.grid_rects = [pg.Rect(x * self.sprite_size, y * self.sprite_size, self.sprite_size, self.sprite_size) for x in range(self.sprite_size) for y in range(self.sprite_size)]
        self.name = None
        self.tilemap = None
        self.level = None
        self.steps = None
        self.orignal_respawn = None
        self.current_respawn = None
        self.collectables = None
        self.locks = None
        self.active_level = 0
        self.max_cached_levels = 100
        self.cached_levels = []
        self.undo_redo_delay = self.main.assets.settings['gameplay']['hold_to_undo/_redo']
        self.undo_redo_timer = 0
        self.save_level_text = self.main.text_handler.add_text(text='level saved', position='bottom')

    def get_cells(self):
        return [cell for cell in self.level.values() if not cell.is_empty()]

    def get_new_cell(self, position, movement):
        new_position = (position[0] + movement[0], position[1] + movement[1])
        if self.position_on_grid(position=new_position):
            return self.level[position[0] + movement[0], position[1] + movement[1]]

    def create_level(self, bump_player=None):
        game = True if self.main.game_state == 'game' else False
        self.level = {}
        for position, elements in self.tilemap.items():
            position = tuple(int(pos) for pos in position.split(':'))
            if game:
                if self.current_respawn and position in self.current_respawn[0]:
                    elements['player'] = {'name': 'player', 'state': 'idle'}
                    if not self.main.debug and (elements['object'] and elements['object']['name'] not in ['permanent flag', 'temporary flag']):
                        elements['object'] = None
                if ((elements['tile'] and elements['tile']['name'] == 'player spawner') and (not self.main.debug)
                        and ((not elements['object'] and not elements['player']) or (elements['object'] and elements['object']['name'] in ['permanent flag', 'temporary flag']))):
                        elements['player'] = {'name': 'player', 'state': 'idle'}
                if elements['tile'] and elements['tile']['name'] == 'teleporter' and elements['tile']['state'] == 'portal' and self.name + ' - ' + str(position) in self.main.assets.data['game']['active_portals']:
                    elements['tile']['state'] += ' animated'
            elif self.current_respawn and position in self.current_respawn[0]:
                elements['player'] = {'name': 'player', 'state': 'idle'}
            level_cell = LevelCell(main=self.main, position=position, elements=elements)
            if game and self.current_respawn and position in self.current_respawn[0] and level_cell.check_element(name='player', state='idle'):
                level_cell.object_data['player']['facing_right'] = self.current_respawn[2][self.current_respawn[0].index(position)]
                if bump_player:
                    self.main.game_states['game'].bump_object(cell=level_cell, object_type='player', movement=bump_player, bump_amount=3.5)
            self.level[position] = level_cell
        for collectable_name, collectable_data in self.collectables.items():  # set collectables before we create level cell object?
            if collectable_data:
                for position in collectable_data:
                    if not game or self.main.utilities.level_and_position(level=self.name, position=position) not in self.main.assets.data['game']['collectables'][collectable_name]:
                        self.level[tuple(position)].elements['object'] = {'name': 'collectable', 'state': collectable_name[:-1]}
                        self.level[tuple(position)].reset_object_data()
        for position in self.locks:
            level_and_position = self.main.utilities.level_and_position(level=self.name, position=position)
            if level_and_position in self.main.assets.data['locks']:
                lock_data =  self.main.assets.data['locks'][level_and_position]
                if game and (not lock_data['collectable_type'] or not lock_data['collectable_amount']):
                    print(f'lock {level_and_position} not set')
                elif (game and (lock_data['collectable_type'] and lock_data['collectable_amount']) and
                        (len(self.main.assets.data['game']['collectables'][lock_data['collectable_type']]) >= lock_data['collectable_amount'])):
                    pass
                else:
                    self.level[tuple(position)].elements['tile'] = {'name': 'lock', 'state': 'lock'}
        if game:
            self.main.game_states['game'].resolve_standing(new_level=True)

    def create_tilemap(self):
        self.tilemap = {}
        self.collectables = {'silver keys': [], 'silver gems': [], 'gold keys': [], 'gold gems': [], 'cheeses': []}
        self.locks = []
        if self.name in self.main.assets.data['teleporters']['recievers']:
            del self.main.assets.data['teleporters']['recievers'][self.name]
        for position, cell in self.level.items():
            elements = deepcopy(cell.elements)
            level_and_position = self.main.utilities.level_and_position(level=self.name, position=position)
            if cell.check_element(name='player', state='idle'):
                elements['player'] = None
            if cell.check_element(name='collectable'):
                collectable_type = cell.elements['object']['state'] + 's'
                if collectable_type in self.collectables:
                    elements['object'] = None
                    self.collectables[collectable_type].append(position)
            if self.name.startswith('(') and self.name.endswith(')'):
                if cell.check_element(name='lock'):
                    elements['tile'] = None
                    self.locks.append(position)
                    if (level_and_position in self.main.assets.data['locks'] and  self.main.assets.data['locks'][level_and_position] !=
                            {'position': position, 'collectable_type': None, 'collectable_amount': None}):
                        pass
                    else:
                        self.main.assets.data['locks'][level_and_position] = {'position': position, 'collectable_type': None, 'collectable_amount': None}
                elif level_and_position in self.main.assets.data['locks']:
                    del self.main.assets.data['locks'][level_and_position]
            self.tilemap[str(position[0]) + ':' + str(position[1])] = elements
            if self.name.startswith('(') and self.name.endswith(')'):
                teleporters = self.main.assets.data['teleporters']
                if cell.check_element(name='teleporter'):
                    state = cell.elements['tile']['state']
                    teleporters[state + 's'][level_and_position] = {'position': position, 'destination': level_and_position if state == 'reciever' else None}
                else:
                    if level_and_position in teleporters['senders']:
                        del teleporters['senders'][level_and_position]
                    if level_and_position in self.main.assets.data['teleporters']['portals']:
                        del teleporters['portals'][level_and_position]
                        empty_activations = []
                        for activation, activation_data in teleporters['activations'].items():
                            if level_and_position in activation_data['portals']:
                                activation_data['portals'].remove(level_and_position)
                                if not activation_data['portals']:
                                    empty_activations.append(activation)
                        for empty_activation in empty_activations:
                            del teleporters['activations'][empty_activation]
        return {'respawn': self.current_respawn, 'collectables': self.collectables, 'locks': self.locks, 'tilemap': self.tilemap}

    def load_level(self, name='empty', load_respawn=None, bump_player=None):
        if name not in self.main.assets.levels:
            name = '(4, 4)'
        self.name = name
        tilemap_data = deepcopy(self.main.assets.levels[name])
        self.tilemap = tilemap_data['tilemap']
        if load_respawn == 'level':
            self.orignal_respawn = [[tuple(tilemap_data['respawn'][0][0])], [tuple(tilemap_data['respawn'][1][0])], tilemap_data['respawn'][2]] if tilemap_data['respawn'] else None
        elif load_respawn == 'setting':
            if self.main.assets.data['game']['respawn']:
                self.orignal_respawn = [[tuple(position) for position in self.main.assets.data['game']['respawn'][0]],
                                        [tuple(position) for position in self.main.assets.data['game']['respawn'][1]], self.main.assets.data['game']['respawn'][2]]
        if not load_respawn == 'current':
            self.current_respawn = self.orignal_respawn
        elif self.current_respawn:
                self.current_respawn[1] = self.current_respawn[0].copy()
        self.collectables = tilemap_data['collectables']
        self.locks = tilemap_data['locks'] if 'locks' in tilemap_data else []
        self.create_level(bump_player=bump_player)
        self.cache_level()

    def save_level(self, name=None):
        if not name:
            name = self.name
        tilemap_data = self.create_tilemap()
        self.main.assets.levels[name] = tilemap_data
        self.main.update_choose_level_menu()
        with open(os.path.join('assets/levels', f'{name}.json'), 'w') as file_data:
            json.dump(obj=tilemap_data, fp=file_data, indent=2)
        self.save_level_text.activate(duration=2)

    def copy_level(self, level_data=None):
        level_data_copy = {'steps': deepcopy(level_data['steps']) if level_data else deepcopy(self.steps),
                           'respawn': deepcopy(level_data['respawn']) if level_data else deepcopy(self.current_respawn),
                           'name': level_data['name'] if level_data else self.name, 'level': {}}
        for position, cell in (level_data['level'] if level_data else self.level).items():
            object_data = deepcopy(cell.object_data)
            for data in object_data.values():
                if data:
                    data['blit_position'] = [data['blit_position'][-1]]
            level_data_copy['level'][position] = LevelCell(main=self.main, position=position, elements=deepcopy(cell.elements), object_data=object_data)
        return level_data_copy

    def compare_levels(self, level_data):
        if self.steps != level_data['steps'] or self.current_respawn != level_data['respawn']:
            return False
        for cell_1, cell_2 in zip(self.level.values(), level_data['level'].values()):
            if cell_1.elements != cell_2.elements:
                return False
        return True

    def clear_cache_redo(self):
        if self.active_level != len(self.cached_levels) - 1:
            self.cached_levels = self.cached_levels[:self.active_level + 1]

    def reset_cache(self):
        self.active_level = 0
        self.cached_levels = []

    def cache_level(self):
        if len(self.cached_levels):
            if self.active_level != len(self.cached_levels) - 1:
                self.cached_levels = self.cached_levels[:self.active_level + 1]
            if not self.compare_levels(level_data=self.cached_levels[-1]):
                self.cached_levels.append(self.copy_level())
                self.active_level += 1
                if len(self.cached_levels) > self.max_cached_levels:
                    self.cached_levels.pop(0)
                    self.active_level -= 1
        else:
            self.cached_levels.append(self.copy_level())

    def undo(self):  # combine these back again...
        if self.main.game_state == 'game' and self.main.game_states['game'].interpolating:
            self.undo_redo_timer = self.undo_redo_delay
            level_data = self.copy_level(level_data=self.cached_levels[self.active_level])
            self.steps = level_data['steps']
            self.current_respawn = level_data['respawn']
            self.name = level_data['name']
            self.level = level_data['level']
            return True
        elif self.active_level > 0:
            self.undo_redo_timer = self.undo_redo_delay
            self.active_level -= 1
            level_data = self.copy_level(level_data=self.cached_levels[self.active_level])
            self.steps = level_data['steps']
            self.current_respawn = level_data['respawn']
            self.name = level_data['name']
            self.level = level_data['level']
            return True

    def redo(self):
        if self.active_level < len(self.cached_levels) - 1:
            self.undo_redo_timer = self.undo_redo_delay
            self.active_level += 1
            level_data = self.copy_level(level_data=self.cached_levels[self.active_level])
            self.steps = level_data['steps']
            self.current_respawn = level_data['respawn']
            self.name = level_data['name']
            self.level = level_data['level']
            return True

    def position_on_grid(self, position):
        if 0 <= position[0] < self.grid_size and 0 <= position[1] < self.grid_size:
            return True

    def display_to_grid(self, position):
        return int(position[0] - self.level_offset[0]) // self.sprite_size, int(position[1] - self.level_offset[1]) // self.sprite_size

    def grid_to_display(self, position, centre=False):
        return (self.level_offset[0] + position[0] * self.sprite_size + (self.sprite_size // 2) if centre else 0,
                self.level_offset[1] + position[1] * self.sprite_size + (self.sprite_size // 2) if centre else 0)

    def update(self):
        undo_redo = False
        if self.undo_redo_timer:
            self.undo_redo_timer -= 1
        else:
            if self.main.events.check_key(key='z', action='held'):
                undo_redo = self.undo()
            elif self.main.events.check_key(key='y', action='held'):
                undo_redo = self.redo()
        if self.main.events.check_key(key=['z', 'y'], action='unpressed'):
            self.undo_redo_timer = 0
        return undo_redo

    def draw(self, surface, overlay, mouse_cell=None):
        if self.level:
            level_surface = pg.Surface(size=self.level_size, flags=pg.SRCALPHA)
            level_surface.fill(color=self.main.assets.colours['dark_purple'])
            if self.show_grid:
                for grid_rect in self.grid_rects:
                    pg.draw.rect(surface=level_surface, color=self.main.assets.colours['white'], rect=grid_rect, width=1)
            if self.current_respawn:
                for position in self.current_respawn[1]:
                    level_surface.blit(source=self.main.assets.get_sprite(name='player respawn'),
                                       dest=(position[0] * self.main.sprite_size, position[1] * self.main.sprite_size))
            cells = self.get_cells()
            for cell in cells:
                cell.draw(surface=level_surface, animated=self.animated, element_types=['tile'])
            for cell in cells:
                cell.draw(surface=level_surface, animated=self.animated, element_types=['object', 'vertical_barrier', 'horizontal_barrier'])
            for cell in cells:
                cell.draw(surface=level_surface, animated=self.animated, element_types=['player'])
            if mouse_cell:
                if mouse_cell.check_element(name='player', state='idle'):
                    sprite = self.main.assets.get_sprite(name='player respawn', state='player respawn')
                    sprite.set_alpha(self.mouse_cell_alpha)
                    level_surface.blit(source=sprite, dest=(mouse_cell.position[0] * self.main.sprite_size, mouse_cell.position[1] * self.main.sprite_size))
                mouse_cell.draw(surface=level_surface, animated=self.animated, alpha=self.mouse_cell_alpha, element_types=['tile'])
                mouse_cell.draw(surface=level_surface, animated=self.animated, alpha=self.mouse_cell_alpha,
                                element_types=['object', 'player', 'vertical_barrier', 'horizontal_barrier'])
                level_surface.blit(source=self.main.assets.images['other']['cell_marker'],
                                   dest=(mouse_cell.position[0] * self.main.sprite_size, mouse_cell.position[1] * self.main.sprite_size))
            surface.blit(source=level_surface, dest=self.level_offset)

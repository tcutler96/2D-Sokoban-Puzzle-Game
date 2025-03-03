from scripts.map_cell import MapCell
import pygame as pg


class Map:
    def __init__(self, main):
        self.main = main
        self.show_map = False
        self.show_text = True
        self.cell_size = 64
        part_one_offset = (768, 384)
        part_two_offset = (576, 1280)
        target = self.get_target(level=self.main.assets.data['game']['level'])
        self.offset_dict = {'1': part_one_offset, '2': part_two_offset, 'current': part_one_offset if target == '1' else part_two_offset, 'target': target,
                            'step': (abs(part_one_offset[0] - part_two_offset[0]) // self.cell_size, abs(part_one_offset[1] - part_two_offset[1]) // self.cell_size)}
        self.levels = self.load_levels()
        self.map = self.load_map()
        # need to move collectables to make room for cheeses...
        self.collectables = {'surface': pg.Surface(size=(0, 0), flags=pg.SRCALPHA), 'size': (224, 128), 'position': (840, 960), 'types': list(self.main.assets.data['game']['collectables'])}
        self.toggle_map_text = self.main.text_handler.add_text(text="toggle map: 'tab'", position=(1088, 1120), alignment=('r', 'c'), interactable=True)
        self.switch_map_text = self.main.text_handler.add_text(text="switch maps: 'space'", position=(64, 1120), alignment=('l', 'c'), interactable=True)
        # invert game surface colours when map is open...
        # only display cryptids/ cheeses on map once one has been collected?

    def load_levels(self):
        levels = {}
        for level_name, level_data in self.main.assets.levels.items():
            if level_name.startswith('(') and level_name.endswith(')'):
                levels[level_name] = level_data
        return levels

    def load_map(self):
        map_cells = {}
        for level_name, level_data in self.levels.items():
            level_position = self.main.utilities.position_str_to_tuple(position=level_name)
            if level_name in self.main.assets.data['map'] and self.main.assets.data['map'][level_name] in self.main.assets.images['map']:
                sprite = self.main.assets.images['map'][self.main.assets.data['map'][level_name]]
            else:
                neighbours = set()
                for neighbour in self.main.utilities.neighbour_offsets:
                    neighbour_position = str((level_position[0] + neighbour[0], level_position[1] + neighbour[1]))
                    if neighbour_position in self.levels:
                        neighbours.add(neighbour)
                variant = self.main.utilities.neighbour_auto_tile_map[tuple(sorted(neighbours))]
                self.main.assets.data['map'][level_name] = variant
                sprite = self.main.assets.images['map'][variant]
                print(f'{level_name} map data updated...')
            teleporter = False
            for reciever in self.main.assets.data['teleporters']['recievers']:
                if level_name in reciever:
                    teleporter = True
            map_cells[level_name] = MapCell(main=self.main, level_name=level_name, sprite=sprite, blit_position=(level_position[0] * self.cell_size, level_position[1] * self.cell_size),
                                            cell_size=self.cell_size, offset=self.offset_dict['current'], discovered=level_name in self.main.assets.data['game']['discovered_levels'],
                                            player=level_name == self.main.assets.data['game']['level'],
                                            icons={'silver keys': [], 'silver gems': [], 'gold keys': [], 'gold gems': [], 'teleporter': teleporter})
        return map_cells

    def reset_map(self):
        self.show_map = False
        for level_name, map_cell in self.map.items():
            map_cell.discovered = level_name in self.main.assets.data['game']['discovered_levels']
            map_cell.player = level_name == self.main.assets.data['game']['level']
        self.update_collectables_surface()
        for level_name, level_data in self.levels.items():
            for collectable_type in self.collectables['types']:
                collectable = []
                if level_data['collectables'][collectable_type]:
                    for position in level_data['collectables'][collectable_type]:
                        if self.main.utilities.level_and_position(level=level_name, position=position) not in self.main.assets.data['game']['collectables'][collectable_type]:
                            collectable.append(tuple(position))
                self.map[level_name].icons[collectable_type] = collectable

    def get_target(self, level):
        return '1' if self.main.utilities.position_str_to_tuple(position=level)[1] > -4 else '2'

    def set_target(self, target):
        if self.offset_dict['current'] != self.offset_dict[target]:
            self.offset_dict['target'] = target
            self.offset_dict['current'] = self.offset_dict[self.offset_dict['target']]
            for map_cell in self.map.values():
                map_cell.update_rect(self.offset_dict['current'])

    def transition_level(self, old_level, new_level):
        self.map[old_level].player = False
        self.map[new_level].player = True
        if not self.map[new_level].discovered:
            self.map[new_level].discovered = True
            self.main.assets.data['game']['discovered_levels'].append(new_level)

    def update_player(self, level_name):
        for map_cell in self.map.values():
            map_cell.player = False
            if map_cell.level_name == level_name:
                map_cell.player = True

    def update_collectables(self, collectable_type, level_name, position):
        if collectable_type in self.collectables['types']:
            self.update_collectables_surface()
            if level_name != 'custom' and position in self.map[level_name].icons[collectable_type]:
                self.map[level_name].icons[collectable_type].remove(position)

    def update_collectables_surface(self):
        surface = pg.Surface(size=self.collectables['size'], flags=pg.SRCALPHA)
        for y, (collectable_type, collectable_count) in enumerate(self.main.assets.data['game']['collectables'].items()):
            for x in range(len(collectable_count)):
                surface.blit(source=self.main.assets.images['map'][collectable_type[:-1]], dest=(x * 8, 96 - y * 32))
        self.collectables['surface'] = surface

    def update(self, mouse_position, active_cutscene):
        if not active_cutscene and (self.toggle_map_text.selected or self.main.events.check_key(key='tab')):
            self.show_map = not self.show_map
            if not self.show_map:
                self.set_target(target=self.offset_dict['target'])
        if self.show_map and (self.switch_map_text.selected or self.main.events.check_key(key='space')):
            self.offset_dict['target'] = '1' if self.offset_dict['target'] == '2' else '2'
            mouse_position = None
        interpolating = False
        if self.offset_dict['current'] != self.offset_dict[self.offset_dict['target']]:
            if self.show_map:
                interpolating = True
                step = (self.offset_dict['step'][0] * (1 if self.offset_dict['current'][0] < self.offset_dict[self.offset_dict['target']][0] else -1),
                        self.offset_dict['step'][1] * (1 if self.offset_dict['current'][1] < self.offset_dict[self.offset_dict['target']][1] else -1))
                self.offset_dict['current'] = (self.offset_dict['current'][0] + step[0], self.offset_dict['current'][1] + step[1])
            else:
                self.offset_dict['current'] = self.offset_dict[self.offset_dict['target']]
        selected_level = None
        for level_name, map_cell in self.map.items():
            if map_cell.update(mouse_position=mouse_position, offset=self.offset_dict['current'], interpolating=interpolating):
                selected_level = level_name
        if selected_level:
            self.set_target(target=self.get_target(level=selected_level))
            return selected_level

    def draw(self, surface):
        for map_cell in self.map.values():
            map_cell.draw(surface=surface, offset=self.offset_dict['current'])
        surface.blit(source=self.collectables['surface'], dest=self.collectables['position'])
        if self.show_text:
            self.toggle_map_text.activate()
            if self.main.assets.data['game']['part_two']:
                self.switch_map_text.activate()

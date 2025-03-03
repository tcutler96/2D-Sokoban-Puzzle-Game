from scripts.toolbar import Toolbar
from scripts.level import Level
from scripts.level_cell import LevelCell
from copy import deepcopy


class LevelEditor:
    def __init__(self, main):
        self.main = main
        self.previous = None
        self.level = Level(main=self.main)
        self.mouse_cell = LevelCell(main=self.main, position=(-1, -1))
        self.toolbar = Toolbar(main=self.main)
        self.reset_level_text = self.main.text_handler.add_text(text='level reset', position='bottom')

    def reset_toolbar(self, hovered=False, selected=False):
        if hovered:
            self.toolbar.hovered_element = [None, None]
        if selected:
            self.toolbar.selected_tile = ['no tile', 0]
            self.toolbar.selected_object = ['no object', 0]
            self.mouse_cell.elements = {'object': None, 'player': None, 'tile': None, 'vertical_barrier': None, 'horizontal_barrier': None}

    def auto_tile(self):
        for _, cell in self.level.level.items():
            position = cell.position
            tile = cell.elements['tile']
            if tile and tile['name'] == 'wall':
                neighbours = set()
                for neighbour in self.main.utilities.neighbour_offsets:
                    neighbour_position = (position[0] + neighbour[0], position[1] + neighbour[1])
                    if neighbour_position in self.level.level:
                        neighbour_tile_data = self.level.level[neighbour_position].elements['tile']
                        if neighbour_tile_data and neighbour_tile_data['name'] == tile['name']:
                            neighbours.add(neighbour)
                    else:
                        neighbours.add(neighbour)
                neighbours = tuple(sorted(neighbours))
                state = self.main.utilities.neighbour_auto_tile_map[neighbours]
                for corner in self.main.utilities.corner_offsets:
                    if (corner[0], 0) in neighbours and (0, corner[1]) in neighbours:
                        corner_position = (position[0] + corner[0], position[1] + corner[1])
                        if corner_position in self.level.level:
                            corner_tile_data = self.level.level[corner_position].elements['tile']
                            if corner_tile_data and corner_tile_data['name'] == tile['name']:
                                pass
                            else:
                                state += f'-{self.main.utilities.corner_auto_tile_map[corner]}'
                tile['state'] = state

    def temp_save_tilemap(self):
        level_data = {'respawn': self.level.current_respawn, 'collectables': {'silver keys': [], 'silver gems': [], 'gold keys': [], 'gold gems': [], 'cheeses': []}, 'tilemap': {}}
        for position, cell in self.level.level.items():
            elements = deepcopy(cell.elements)
            if cell.check_element(name='player', state='idle'):
                elements['player'] = None
            for collectable_name in self.level.collectables:
                if cell.check_element(name='collectable', state=collectable_name[:-1]):
                    elements['tile'] = None
                    level_data['collectables'][collectable_name].append(position)
            level_data['tilemap'][str(position[0]) + ':' + str(position[1])] = elements
        self.main.assets.levels['custom'] = level_data

    def check_unique_elements(self, cell):
        element_type, name, state = None, None, None
        if cell.check_element(name='player', state='idle'):
            element_type = 'player'
            name = 'player'
            state = 'idle'
        elif cell.check_element(name='teleporter', state='reciever'):
            element_type = 'tile'
            name = 'teleporter'
            state = 'reciever'
        if element_type:
            for cell in self.level.get_cells():
                if cell.check_element(name=name, state=state):
                    cell.elements[element_type] = None

    def clear_cell(self, position):
        if self.level.position_on_grid(position=position):
            cell = self.level.level[position]
            if not cell.is_empty():
                cell.elements = {'object': None, 'player': None, 'tile': None, 'vertical_barrier': None, 'horizontal_barrier': None}
            if self.level.current_respawn and cell.position in self.level.current_respawn[0]:
                self.level.current_respawn = None

    def set_cell(self, cell):
        if self.level.position_on_grid(position=cell.position):
            if cell.check_element(name='player', state='idle'):
                self.level.current_respawn = [[cell.position], [cell.position], [True]]
            elif self.level.current_respawn and cell.position in self.level.current_respawn[0]:
                self.level.current_respawn = None
            if self.level.level[cell.position].elements != cell.elements:
                if cell.is_empty():
                    self.clear_cell(position=cell.position)
                else:
                    self.check_unique_elements(cell=cell)
                    self.level.level[cell.position].set_elements(elements=deepcopy(cell.elements))
            elif cell.is_empty() and self.level.current_respawn and cell.position in self.level.current_respawn[0]:
                self.level.current_respawn = None

    def start_up(self, previous_game_state=None):
        if previous_game_state == 'main_menu':
            self.main.change_menu_state(menu_state='choose_level')
            self.reset_toolbar(hovered=True, selected=True)
        elif previous_game_state == 'game':
            self.main.change_menu_state(menu_state=None)
            del self.main.assets.levels['custom']

    def update(self, mouse_position):
        self.main.display.set_cursor(cursor='arrow')
        if not self.main.menu_state and not self.main.transition.transitioning:
            self.level.update()
            self.mouse_cell.position = self.level.display_to_grid(position=mouse_position)
            selected_element = self.toolbar.update(mouse_position=mouse_position)
            if selected_element:
                if selected_element[0] == 'button':
                    if selected_element[1] == 'Play Level':
                        self.reset_toolbar(hovered=True, selected=True)
                        self.main.menu_states['game_paused'].menu['Quit'].button_type = 'game_state'
                        self.main.menu_states['game_paused'].menu['Quit'].button_response = 'level_editor'
                        self.temp_save_tilemap()
                        self.main.change_game_state(game_state='game')
                    if selected_element[1] == 'Toggle Grid':
                        self.level.show_grid = not self.level.show_grid
                    elif selected_element[1] == 'Reset Level':
                        self.reset_level_text.activate(duration=2)
                        self.level.load_level(name='filled' if self.level.name == 'empty' else 'empty', load_respawn='level')
                    elif selected_element[1] == 'Save Level':
                        self.level.save_level(name=None if self.main.events.check_key(key='mouse_1', modifier='ctrl') else 'saved')
                    elif selected_element[1] == 'Load Level':
                        self.reset_toolbar(hovered=True, selected=True)
                        self.main.menu_states['choose_level'].menu['Back'].button_type = 'menu_state'
                        self.main.menu_states['choose_level'].menu['Back'].button_response = None
                        self.level.save_level_text.deactivate()
                        self.main.change_menu_state(menu_state='choose_level')
                    elif selected_element[1] == 'Quit to Main Menu':
                        self.reset_toolbar(hovered=True)
                        self.main.transition.start(response=['game_state', 'main_menu'], queue=(True, 'fade', (0, 0), 1))
                else:
                    self.mouse_cell.add_element(element=selected_element)
                    if selected_element[0] == 'tile' and not self.mouse_cell.elements['object'] and not self.mouse_cell.elements['player'] :
                        self.toolbar.selected_object = ['no object', 0]
                    elif selected_element[0] == 'object' and not self.mouse_cell.elements['tile'] and not self.mouse_cell.elements['vertical_barrier'] and not self.mouse_cell.elements['horizontal_barrier']:
                        self.toolbar.selected_tile = ['no tile', 0]
            if not self.toolbar.hovered_element[0]:
                if self.main.events.check_key(key='mouse_2'):
                    if self.level.position_on_grid(position=self.mouse_cell.position):
                        self.mouse_cell.empty()
                        if self.level.current_respawn and self.mouse_cell.position in self.level.current_respawn[0]:
                            self.mouse_cell.elements['player'] = {'name': 'player', 'state': 'idle'}
                        else:
                            for element_type, element_data in reversed(self.level.level[self.mouse_cell.position].elements.items()):
                                if element_data:
                                    self.mouse_cell.add_element(element=['object' if element_type in ['object', 'player'] else 'tile', element_data['name'], element_data['state']])
                        self.toolbar.set_toolbar(elements=self.mouse_cell.elements)
                if self.main.events.check_key(key='mouse_3', action='held'):
                    self.clear_cell(position=self.mouse_cell.position)
                    self.auto_tile()
                elif self.main.events.check_key(key='mouse_1', action='held'):
                    self.set_cell(cell=self.mouse_cell)
                    self.auto_tile()
                elif self.main.events.check_key(key=['mouse_1', 'mouse_3'], action='unpressed'):
                    self.level.cache_level()

    def draw(self, surface, overlay):
        if not self.main.menu_state:
            self.toolbar.draw(overlay=overlay)
            self.level.draw(surface=surface, overlay=overlay, mouse_cell=self.mouse_cell if (not self.main.transition.transitioning and self.level.position_on_grid(position=self.mouse_cell.position)
                                                                                             and not self.toolbar.hovered_element[0]) else None)

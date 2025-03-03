from scripts.menu_element import MenuElement
from math import ceil


class Menu:
    def __init__(self, main, menu_name, menu_data):
        self.main = main
        self.menu_name = menu_name
        self.max_rows = 9
        self.column_positions = {1: {0: 0}, 2: {0: -self.main.display.half_width * 0.2, 1: self.main.display.half_width * 0.2},
                                 3: {0: -self.main.display.half_width * 0.4, 1: 0, 2: self.main.display.half_width * 0.4},
                                 4: {0: -self.main.display.half_width * 0.6, 1: -self.main.display.half_width * 0.2, 2: self.main.display.half_width * 0.2, 3: self.main.display.half_width * 0.6},
                                 5: {0: -self.main.display.half_width * 0.8, 1: -self.main.display.half_width * 0.4, 2: 0, 3: self.main.display.half_width * 0.4, 4: self.main.display.half_width * 0.8}}
        self.menu, self.max_scroll = self.get_menu(menu_data=menu_data)
        self.scroll = 0
        self.scroll_amount = 64

    def get_menu(self, menu_data):
        menu = {}
        columns, rows = 1, len(menu_data) - 1 - (1 if 'Back' in menu_data else 0)
        column, row = 0, 0
        max_scroll = 0
        for count, (element_name, element_data) in enumerate(menu_data.items()):
            if element_data == 'title':
                if element_name == 'Choose Level':
                    columns, rows = 5, ceil(rows / 5)
                    if rows > self.max_rows:
                        max_scroll = (rows - self.max_rows) * 64
                position = (self.main.display.half_width, self.main.display.half_height - 176)
            elif element_name == 'Back':
                position = (self.main.display.half_width, self.main.display.half_height + 64 * (rows - 1))
            else:
                position = (self.main.display.half_width + self.column_positions[columns][column], self.main.display.half_height + 64 * (row - 1))
                column += 1
                if column == columns:
                    column = 0
                    row += 1
            menu[element_name] = MenuElement(main=self.main, name=element_name, position=position, element_data=element_data)
        return menu, max_scroll

    def start_up(self):
        self.scroll = 0
        for _, element in self.menu.items():
            element.active_surface = 'default'
            element.alpha = element.alpha_start
            element.offset = element.offset_start
            element.update_rect()

    def update(self, mouse_position):
        scroll = None
        if self.max_scroll:
            if self.main.events.check_key(key='mouse_4'):
                self.scroll = max(0, self.scroll - self.scroll_amount)
                scroll = self.scroll
            if self.main.events.check_key(key='mouse_5'):
                self.scroll = min(self.max_scroll, self.scroll + self.scroll_amount)
                scroll = self.scroll
        for _, element in self.menu.items():
            selected_element = element.update(mouse_position=mouse_position, scroll=scroll)
            if selected_element and not self.main.transition.transitioning:
                if selected_element[0] == 'game_state':
                    if self.main.game_state == 'main_menu' and selected_element[1] == 'quit':
                        self.main.transition.start(response=['game_state', 'quit'], queue=(True, 'fade', (0, 0), 1))
                    elif self.main.game_state == 'main_menu' and selected_element[1] == 'game':
                        if selected_element[2] == 'Yes':
                            self.main.assets.reset_game_data()
                        self.main.menu_states['game_paused'].menu['Quit'].button_type = 'game_state'
                        self.main.menu_states['game_paused'].menu['Quit'].button_response = 'main_menu'
                        self.main.transition.start(style='circle', centre=element.centre, response=['game_state', 'game'], queue=(True, 'circle', 'player', 1))
                    elif self.main.game_state == 'main_menu' and selected_element[1] == 'level_editor':
                        self.main.menu_states['choose_level'].menu['Back'].button_type = 'game_state'
                        self.main.menu_states['choose_level'].menu['Back'].button_response = 'main_menu'
                        self.main.change_game_state(game_state='level_editor')
                    elif self.main.game_state == 'game' and selected_element[1] == 'main_menu':
                        self.main.transition.start(response=['game_state', 'main_menu'], queue=(True, 'fade', (0, 0), 1))
                    elif self.main.game_state == 'game' and selected_element[1] == 'level_editor':
                        self.main.transition.start(response=['game_state', 'level_editor'], queue=(True, 'fade', (0, 0), 1))
                    else:
                        self.main.change_game_state(game_state=selected_element[1])
                elif selected_element[0] == 'menu_state':
                    if selected_element[1] == 'options':
                        if self.main.game_state == 'main_menu':
                            self.main.menu_states['options'].menu['Back'].button_type = 'menu_state'
                            self.main.menu_states['options'].menu['Back'].button_response = 'title_screen'
                        elif self.main.game_state == 'game':
                            self.main.menu_states['options'].menu['Back'].button_type = 'menu_state'
                            self.main.menu_states['options'].menu['Back'].button_response = 'game_paused'
                    self.main.change_menu_state(menu_state=selected_element[1])
                elif selected_element[0] == 'option':
                    self.main.assets.change_setting(group=self.menu_name, name=selected_element[2].lower().replace(' ', '_'), option=selected_element[1][0].lower().replace(' ', '_'))
                elif selected_element[0] == 'level':
                    if self.main.game_state == 'game' and selected_element[2] == 'Restart Level':
                        self.main.transition.start(style='circle', centre=element.centre, response=['level', self.main.game_states['game'].level.name, 'original', None, None], queue=(True, 'circle', 'player', 1))
                    elif self.main.game_state == 'level_editor':
                        self.main.transition.start(response=['level', selected_element[1], 'level', None, None], queue=(True, 'fade', (0, 0), 1))

    def draw(self, overlay):
        for _, element in self.menu.items():
            element.draw(overlay=overlay, scroll=self.scroll)

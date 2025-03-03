import pygame as pg


class MainMenu:
    def __init__(self, main):
        self.main = main
        self.draw_circle = False
        self.clear_background = False

    def start_up(self, previous_game_state=None):
        self.main.change_menu_state(menu_state='title_screen')


    def update(self, mouse_position):
        self.main.display.set_cursor(cursor='arrow')
        if self.main.menu_state == 'title_screen':
            self.draw_circle = self.main.events.check_key(key='mouse_3', action='held')
            self.clear_background  = self.main.events.check_key(key='escape')
            if self.main.events.check_key(key='space'):
                self.main.menu_states['game_paused'].menu['Quit'].button_type = 'game_state'
                self.main.menu_states['game_paused'].menu['Quit'].button_response = 'main_menu'
                self.main.change_game_state(game_state='game')

    def draw(self, surface, overlay):
        if self.clear_background:
            surface.fill(color=self.main.assets.colours['purple'])
        if self.draw_circle:
                pg.draw.circle(surface=surface, color=self.main.assets.colours['cream'], center=self.main.events.mouse_position, radius=50, width=1)

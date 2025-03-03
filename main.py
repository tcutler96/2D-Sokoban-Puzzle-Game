from scripts.assets import Assets
from scripts.display import Display
from scripts.events import Events
from scripts.shaders import Shaders
from scripts.text_handler import TextHandler
from scripts.transition import Transition
from scripts.utilities import Utilities
from scripts.menu import Menu
from game_states.main_menu import MainMenu
from game_states.game import Game
from game_states.level_editor import LevelEditor
import pygame as pg
import sys
import math
import json
import os


# add glow effect to hud layer
# add animation to 'other' images such as cell marker
# look into loop hero noise transition shader...
# add option for resolution, just scale final display surface to set window size (whether bigger or small than normal render size)...
# make text shadow bounce/ sway, toggle shadow offset gradually...

class Main:
    def __init__(self):
        pg.init()
        self.fps = 60
        self.true_fps = self.fps
        self.clock = pg.time.Clock()
        self.runtime_frames = 0
        self.runtime_seconds = 0
        self.display_size = (1152, 1152)
        self.sprite_size = 64
        self.display = Display(self, size=self.display_size)
        self.utilities = Utilities(main=self)
        self.assets = Assets(main=self)
        self.display.load_cursors()
        self.events = Events(main=self)
        self.shaders = Shaders(main=self)
        self.transition = Transition(main=self)
        self.text_handler = TextHandler(main=self)
        pg.display.set_caption(f'N Step Steve')
        pg.display.set_icon(self.assets.images['other']['game_icon'])
        self.menu_state = 'title_screen'
        self.menu_states = {menu_name: Menu(main=self, menu_name=menu_name, menu_data=menu_data) for menu_name, menu_data in self.assets.settings['menus'].items()}
        self.game_state = 'main_menu'
        self.game_states = {'main_menu': MainMenu(main=self), 'game': Game(main=self), 'level_editor': LevelEditor(main=self)}
        self.game_states[self.game_state].start_up()
        self.debug = False
        self.debug_text = self.text_handler.add_text(text='debug mode', position='bottom', draw_onto='overlay')
        # self.update_levels()


    def update_levels(self):
        for level_name, level_data in self.assets.levels.items():
            collectables = level_data['collectables'] | {'cheeses': []}
            level_data['collectables'] = collectables
            with open(os.path.join('assets/levels', f'{level_name}.json'), 'w') as file_data:
                json.dump(obj=level_data, fp=file_data, indent=2)

    def change_game_state(self, game_state):
        if game_state != self.game_state:
            if game_state == 'quit':
                self.quit()
            elif game_state in self.game_states:
                previous_game_state = self.game_state
                self.game_state = game_state
                self.game_states[game_state].start_up(previous_game_state=previous_game_state)

    def change_menu_state(self, menu_state):
        if menu_state != self.menu_state:
            if menu_state is None or menu_state in self.menu_states:
                self.menu_state = menu_state
                if self.menu_state in self.menu_states:
                    self.menu_states[self.menu_state].start_up()

    def update_choose_level_menu(self):
        self.assets.update_choose_level_menu()
        self.menu_states['choose_level'] = Menu(main=self, menu_name='choose_level', menu_data=self.assets.settings['menus']['choose_level'])

    def run(self):
        while True:
            self.update()
            self.draw()
            self.clock.tick(self.fps)

    def update(self):
        self.true_fps = self.clock.get_fps()
        if self.true_fps:
            self.runtime_frames += 1
            self.runtime_seconds = self.runtime_seconds + 1 / self.true_fps
        pg.display.set_caption(f'N Step Steve - running at {round(self.true_fps)} fps for {round(self.runtime_seconds, 2)}s' if self.debug else 'N Step Steve')
        self.events.update()
        mouse_position = self.events.mouse_position
        if self.events.check_key(key='w', modifier='ctrl'):
            self.quit()
        if self.events.check_key(key='b', modifier='ctrl'):
            self.debug = not self.debug
        if self.menu_state:
            self.menu_states[self.menu_state].update(mouse_position=mouse_position)
        elif self.game_state in ['game', 'level_editor']:
            self.assets.update()
        self.game_states[self.game_state].update(mouse_position=mouse_position)
        self.text_handler.update(mouse_position=mouse_position)
        self.display.update()
        self.transition.update()
        self.shaders.update(mouse_position=mouse_position)
        self.utilities.shadow_offset = (12 + 6 * math.sin(self.runtime_seconds * 2), 8 + 4 * math.sin(self.runtime_seconds * 2))

    def draw(self):
        if self.debug:
            self.debug_text.activate()
        self.game_states[self.game_state].draw(surface=self.display.display, overlay=self.display.overlay)
        if self.menu_state:
            self.menu_states[self.menu_state].draw(overlay=self.display.overlay)
        self.text_handler.draw(surface=self.display.display, overlay=self.display.overlay)
        self.display.draw()
        self.transition.draw(overlay=self.display.overlay)
        self.shaders.draw(surface=self.display.display, overlay=self.display.overlay)
        pg.display.flip()

    def quit(self):
        self.assets.quit()
        self.shaders.clean_up()
        pg.quit()
        sys.exit()


if __name__ == '__main__':
    Main().run()

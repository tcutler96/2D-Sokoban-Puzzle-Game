import pygame as pg
import math


class Transition:
    def __init__(self, main):
        self.main = main
        self.transition_surface = pg.Surface(size=self.main.display.size, flags=pg.SRCALPHA)
        self.transition_surface2 = pg.Surface(size=self.main.display.size)
        self.transitioning = False
        self.transition_style = 'fade'
        self.transition_centre = (0, 0)
        self.max_distance = 0
        self.transition_current = 0
        self.transition_step = 0
        self.transition_length = 0
        self.transition_ratio = 0
        self.response = None
        self.queue = None
        self.start(fade_in=True)

    def start(self, fade_in=False, style='fade', centre=(0, 0), length=1, response=None, queue=None):
        if not self.transitioning:
            self.transitioning = True
            self.transition_style = style
            if centre == 'player':
                self.transition_centre = self.main.game_states['game'].level.grid_to_display(position=self.main.game_states['game'].level.current_respawn[0][0],
                                                                                             centre=True) if self.main.game_states['game'].level.current_respawn else self.main.display.centre
            else:
                self.transition_centre = centre
            self.max_distance = (max(self.transition_centre[0], self.main.display.width - self.transition_centre[0]), max(self.transition_centre[1], self.main.display.height - self.transition_centre[1]))
            self.max_distance = math.sqrt(self.max_distance[0] ** 2 + self.max_distance[1] ** 2)
            self.transition_length = length * self.main.fps
            if fade_in:
                self.transition_current = 0
                self.transition_step = 1
                self.transition_ratio = 0
            else:
                self.transition_current = self.transition_length
                self.transition_step = -1
                self.transition_ratio = 1
            self.response = response
            self.queue = queue

    def update(self):
        if self.transitioning:
            self.main.display.set_cursor(cursor=None)
            self.transition_current += self.transition_step
            self.transition_ratio = (self.transition_current / self.transition_length) ** 4
            if self.transition_current in [0, self.transition_length]:
                self.transitioning = False
                if self.response:
                    if self.response[0] == 'game_state':
                        self.main.change_game_state(game_state=self.response[1])
                    if self.response[0] == 'menu_state':
                        self.main.change_menu_state(menu_state=self.response[1])
                    elif self.response[0] == 'level':
                        self.main.menu_state = None
                        self.main.game_states[self.main.game_state].level.load_level(name=self.response[1], load_respawn=self.response[2], bump_player=self.response[3])
                    self.response = None
                if self.queue:
                    self.start(*self.queue)
                    self.queue = None

    def draw(self, overlay):  # add another transition style that is a black square moves from one side of the screen to the other relative to player movement, triggered whenever we exit/ enter a new level...
        if self.transitioning:
            if self.transition_style == 'fade':
                self.transition_surface.fill(self.main.assets.colours['dark_purple'])
                self.transition_surface.set_alpha(275 - 275 * self.transition_ratio)
                overlay.blit(source=self.transition_surface, dest=(0, 0))
            elif self.transition_style == 'circle':
                self.transition_surface.fill(self.main.assets.colours['purple'])
                self.transition_surface.set_alpha(255 - 255 * self.transition_ratio)
                overlay.blit(source=self.transition_surface, dest=(0, 0))
                self.transition_surface2.fill(self.main.assets.colours['dark_purple'])
                pg.draw.circle(surface=self.transition_surface2, color=(255, 255, 255), center=self.transition_centre, radius=self.max_distance * self.transition_ratio)
                self.transition_surface2.set_colorkey((255, 255, 255))
                overlay.blit(source=self.transition_surface2, dest=(0, 0))

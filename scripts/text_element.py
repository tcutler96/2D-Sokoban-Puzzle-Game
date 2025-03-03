import pygame as pg


class TextElement:
    def __init__(self, main, text, surface, position, draw_onto, active, delay, duration, interactable):
        self.main = main
        self.text = text
        self.surface = surface
        self.alpha = 0
        self.alpha_step = 25
        self.position = position
        self.rect = pg.Rect(self.position, self.surface.get_size())
        self.draw_onto = draw_onto
        self.active = active
        self.timer = 0
        self.delay = delay
        self.duration = duration
        self.interactable = interactable
        self.hovered = False
        self.selected = False
        self.delete = False

    def activate(self, delay=0, duration=0):
        if not self.active:
            self.active = True
            self.timer = 0
            self.delay = delay * self.main.fps
            self.duration = duration * self.main.fps

    def deactivate(self):  # all text elements automatically deactivate each turn unless they have a set duration/ are constantly activated...
        self.active = False

    def delete(self):
        self.delete = True

    def update(self, mouse_position):
        self.hovered = False
        self.selected = False
        if self.active:  # if not delay or duration, then set active to False each update...
            if self.delay:
                self.timer += 1
            if self.timer == self.delay:
                self.timer = 0
                self.delay = 0
            if not self.delay:
                if self.alpha < 255:
                    self.alpha += self.alpha_step
                    self.surface.set_alpha(self.alpha)
                else:
                    if self.interactable:
                        if self.main.display.cursor and self.rect.collidepoint(mouse_position):
                            self.hovered = True
                            self.main.display.set_cursor(cursor='hand')
                            if self.main.events.check_key(key='mouse_1'):
                                self.selected = True
                if self.duration:
                    self.timer += 1
                    if self.timer == self.duration:
                        self.active = False
                else:
                    self.active = False  # if text element active with no delay or duration, then automatically turn off... needs to be turned on each loop from correspsonding class...
        else:
            if self.alpha:
                self.alpha -= self.alpha_step
                self.surface.set_alpha(self.alpha)



    def draw(self, surface, overlay):
        # self.alpha = 255
        if self.alpha:
            draw_surface = surface if self.draw_onto == 'surface' else overlay
            draw_surface.blit(source=self.surface, dest=self.position)

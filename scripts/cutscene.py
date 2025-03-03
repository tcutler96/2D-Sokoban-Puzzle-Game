

class Cutscene:
    def __init__(self, main):
        self.main = main
        self.active_cutscene = False
        self.timer = 0
        self.cutscene_data = {'part_one': {'type': 'level', 'triggered': self.main.assets.data['game']['part_one'], 'trigger': '(0, 0)', 'length': 6, 'position': (832, 192)},
                              'part_two': {'type': 'level', 'triggered': self.main.assets.data['game']['part_two'], 'trigger': '(-1, -5)', 'length': 6, 'position': (256, 768)},
                              'collectable': {'type': 'collectable', 'triggered': False, 'trigger': 'collectable', 'length': 3, 'position': None}}

    def reset(self):
        self.cutscene_data['part_one']['triggered'] = self.main.assets.data['game']['part_one']
        self.cutscene_data['part_two']['triggered'] = self.main.assets.data['game']['part_two']

    def start(self, collectable_type, position):
        if collectable_type in self.main.assets.data['game']['collectables']:
            cutscene_data = self.cutscene_data['collectable']
            self.active_cutscene = 'collectable'
            self.timer = cutscene_data['length'] * self.main.fps
            cutscene_data['position'] = position
            self.main.text_handler.text2['game']['collectables'][collectable_type].activate(duration=3)

    def update(self, level):
        if self.active_cutscene:
            self.timer -= 1
            if self.timer == 0:
                self.active_cutscene = None
            if self.active_cutscene == 'part_one':
                if self.timer == 240:
                    return 'show_map'
                elif self.timer == 120:
                    return 'show_collectables_one'
                elif self.timer == 1:
                    return 'show_map_text'
            elif self.active_cutscene == 'part_two':
                if self.timer == 240:
                    return 'show_map'
                elif self.timer == 120:
                    return 'show_collectables_two'
                elif self.timer == 1:
                    return 'show_map_text'
            elif self.active_cutscene == 'collectable':
                pass
        else:
            for name, data in self.cutscene_data.items():  # how/ where do we trigger collectable cutscene?
                if data['type'] == 'level' and not data['triggered']:
                    if level.name == data['trigger']:
                        self.active_cutscene = name
                        self.timer = data['length'] * self.main.fps
                        data['triggered'] = True
                    if self.active_cutscene == 'part_one':
                        return 'map_target_one'
                    elif self.active_cutscene == 'part_two':
                        return 'map_target_two'

    def draw(self, surface):
        if self.active_cutscene in ['part_one', 'part_two']:  # can add interesting sprite/ particles around player
            surface.blit(source=self.main.assets.images['other']['cell_marker'], dest=self.cutscene_data[self.active_cutscene]['position'])
        elif self.active_cutscene == 'collectable': # collectable spirals around player while shrinking
            pass

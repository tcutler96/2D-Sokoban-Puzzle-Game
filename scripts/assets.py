import pygame.freetype
import pygame as pg
import json
import os


class Assets:
    def __init__(self, main):
        self.main = main
        self.assets_path = os.path.join(os.path.abspath(os.curdir), 'assets')
        self.fonts = self.load_fonts()
        self.images = self.load_images()
        self.levels = self.load_levels()
        self.shaders = self.load_shaders()
        self.sounds = self.load_sounds()
        self.data = self.load_data()
        # have copy of default settings and add ability to reset a page of settings to default...
        # self.settings = {'video': {'background': None, 'button_prompt': True, 'cursor_type': 'sprite', 'hrt_shader': True, 'particles': True, 'screen_shake': True},
        #                  'audio': {'master_volume': 1.0, 'music_volume': 1.0, 'sound_volume': 1.0},
        #                  'gameplay': {'hold_to_move': 5, 'hold_to_undo/_redo': 5}}
        self.settings = self.load_settings()
        self.update_choose_level_menu()
        self.colours = {'white': (230, 230, 230),
                        'black': (25, 25, 25),
                        'true_white': (255, 255, 255),
                        'true_black': (0, 0, 0),
                        'cream': (246, 242, 195),
                        'purple': (49, 41, 62),
                        'light_purple': (195, 199, 246),
                        'dark_purple': (22, 13, 19),
                        'green': (77, 102, 96),
                        'light_green': (142, 184, 158),
                        'bright_green': (127, 255, 127)
                        }
        self.option_to_setting = {'video': {'button_prompt': {'enabled': True, 'disabled': False}, 'hrt_shader': {'enabled': True, 'disabled': False},
                                            'particles': {'enabled': True, 'disabled': False}, 'screen_shake': {'enabled': True, 'disabled': False}},
                                 'audio': {'master_volume': {'100%': 1.0, '75%': 0.75, '50%': 0.5, '25%': 0.25, 'disabled': 0.0}, 'music_volume': {'100%': 1.0, '75%': 0.75, '50%': 0.5, '25%': 0.25, 'disabled': 0.0},
                                           'sound_volume': {'100%': 1.0, '75%': 0.75, '50%': 0.5, '25%': 0.25, 'disabled': 0.0}},
                                 'gameplay': {'hold_to_move': {'fast': 5, 'slow': 15, 'disabled': -1}, 'hold_to_undo/_redo': {'fast': 5, 'slow': 15, 'disabled': -1}}}

    def load_fonts(self):
        path = os.path.join(self.assets_path, 'fonts')
        fonts = {}
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            fonts[file.split('.')[0]] = pg.freetype.Font(file=file_path, size=0)
        return fonts

    def load_images(self):
        path = os.path.join(self.assets_path, 'images')
        images = {}
        default_sprite_size = self.main.sprite_size
        for folder in os.listdir(path):
            folder_path = os.path.join(path, folder)
            if os.path.isdir(folder_path):
                if folder == 'other':
                    other = {}
                    for image in os.listdir(folder_path):
                        other[image.split('.')[0]] = self.main.utilities.load_image(path=os.path.join(folder_path, image))
                    images['other'] = other
                elif folder == 'toolbar':
                    toolbar = {}
                    for image in os.listdir(folder_path):
                        toolbar[image.split('.')[0]] = self.main.utilities.load_image(path=os.path.join(folder_path, image))
                    images['toolbar'] = toolbar
                elif folder == 'map':
                    maps = {}
                    for image in os.listdir(folder_path):
                        maps[image.split('.')[0]] = self.main.utilities.load_image(path=os.path.join(folder_path, image))
                    images['map'] = maps
                elif folder == 'sprites':
                    sprites_default = {}
                    sprites_scaled = {}
                    sprites_data = {}
                    for sprite_type in os.listdir(folder_path):
                        sprite_type_path = os.path.join(folder_path, sprite_type)
                        for sprite_folder_name in os.listdir(sprite_type_path):
                            sprite_name = sprite_folder_name.split('_')[-1]
                            sprite_name_path = os.path.join(sprite_type_path, sprite_folder_name)
                            if os.path.isdir(sprite_name_path):
                                sprite_default = {}
                                sprite_scaled = {}
                                frame_data = {}
                                for sprite_file in os.listdir(sprite_name_path):
                                    frames_default = []
                                    frames_scaled = []
                                    sprite_info = sprite_file[:-4].split(' - ')
                                    sprite_sheet = self.main.utilities.load_image(path=os.path.join(sprite_name_path, sprite_file))
                                    sprite_size = sprite_sheet.get_height()
                                    num_frames = sprite_sheet.get_width() // sprite_size
                                    if len(sprite_info) > 1:
                                        frames_counts = [int(frame_count) for frame_count in sprite_info[1].split(', ')]
                                        if len(frames_counts) != num_frames:
                                            frames_counts = frames_counts + [frames_counts[-1]] * (num_frames - len(frames_counts))
                                    else:
                                        frames_counts = None
                                    for frame in range(num_frames):
                                        frames_default.append(sprite_sheet.subsurface(pg.Rect((frame * sprite_size, 0), (sprite_size, sprite_size))))
                                        frames_scaled.append(pg.transform.scale(surface=sprite_sheet.subsurface(pg.Rect((frame * sprite_size, 0), (sprite_size, sprite_size))),
                                                                         size=(default_sprite_size, default_sprite_size)))
                                    sprite_info = sprite_info[0].split('_')[-1]
                                    sprite_default[sprite_info] = frames_default
                                    sprite_scaled[sprite_info] = frames_scaled
                                    frame_data[sprite_info] = {'frame_counts': frames_counts, 'num_frames': num_frames, 'frame_count': 0, 'frame_index': 0, 'loops': 0}
                                sprites_default[sprite_name] = sprite_default
                                sprites_scaled[sprite_name] = sprite_scaled
                                sprites_data[sprite_name] = {'frame_data': frame_data, 'state_list': list(sprite_default), 'num_states': len(list(sprite_default)), 'sprite_type': sprite_type[:-1]}
                    images['sprites'] = {'default': sprites_default, default_sprite_size: sprites_scaled}
                    images['sprites_data'] = sprites_data
                    images['sprite_list'] = list(sprites_data)
        return images

    def load_levels(self):
        path = os.path.join(self.assets_path, 'levels')
        levels = {}
        for file in os.listdir(path):
            if file.endswith('.json'):
                file_path = os.path.join(path, file)
                with open(file_path, 'r') as file_data:
                    levels[file.split('.')[0]] = json.load(file_data)
        return levels

    def load_shaders(self):
        path = os.path.join(self.assets_path, 'shaders')
        shaders = {}
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            with open(file_path, 'r') as file_data:
                shaders[file.split('.')[0]] = file_data.read()
        return shaders

    def load_sounds(self):
        path = os.path.join(self.assets_path, 'sounds')
        sounds = {}
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            sounds[file.split('.')[0]] = pg.mixer.Sound(file=file_path)
        return sounds

    def load_settings(self):
        path = os.path.join(self.assets_path, 'settings.json')
        with open(path, 'r') as file_data:
            settings = json.load(file_data)
        return settings

    def load_data(self):
        path = os.path.join(self.assets_path, 'data.json')
        with open(path, 'r') as file_data:
            data = json.load(file_data)
        return data

    def change_setting(self, group, name, option):
        if name in self.option_to_setting[group] and option in self.option_to_setting[group][name]:
            option = self.option_to_setting[group][name][option]
        self.settings[group][name] = option
        if group == 'video':
            if name == 'background':
                # self.main.shaders.background = option
                pass
            elif name == 'button_prompt':
                # self.main.game_states['game'].show_button_prompt = option
                pass
            elif name == 'cursor_type':
                self.main.display.cursor_type = option
            elif name == 'hrt_shader':
                # self.main.shaders.hrt_shader = option
                pass
            elif name == 'particles':  # reference main/ particle handler...
                pass
            elif name == 'screen_shake':  # reference game class
                pass
        elif group == 'audio':  # change audio volumes straightaway
            # self.main.audio.change_volume(audio_type=name, volume=option)
            pass
        elif group == 'gameplay':
            if name == 'hold_to_move':
                self.main.game_states['game'].move_delay = option
            elif name == 'hold_to_undo/_redo':
                self.main.game_states['game'].level.undo_redo_delay = option
                self.main.game_states['level_editor'].level.undo_redo_delay = option

    def reset_game_data(self):
        self.data['game'] = {'level': '(0, 0)', 'respawn': [[[12, 2]], [[12, 2]], [False]], 'part_one': False, 'part_two': False,
                             'collectables': {'silver keys': [], 'silver gems': [], 'gold keys': [], 'gold gems': [], 'cheeses': []}, 'discovered_levels': ['(0, 0)'], 'active_portals': []}
        # self.data['game'] = {'level': '(-2, 2)', 'respawn': [[[15, 12]], [[15, 12]], [False]], 'part_one': False, 'part_two': False,
        #                      'collectables': {'silver keys': [], 'silver gems': [], 'gold keys': [], 'gold gems': [], 'cheeses': []}, 'discovered_levels': ['(0, 0)'], 'active_portals': []}

    def update_choose_level_menu(self):
        self.settings['menus']['choose_level'] = {'Choose Level': 'title', 'empty': None, 'filled': None, 'saved': None}
        for level in list(self.levels.keys()):
            self.settings['menus']['choose_level'][level] = ['button', 'level', level]
        if not self.settings['menus']['choose_level']['saved']:
            del self.settings['menus']['choose_level']['saved']
        self.settings['menus']['choose_level']['Back'] = ['button', 'game_state', 'main_menu']

    def get_sprite(self, name, state=None, sprite_size='main', animated=True):
        if not state:
            state = name
        if sprite_size == 'main':
            sprite_size = self.main.sprite_size
        if name in self.images['sprite_list'] and state in self.images['sprites_data'][name]['state_list']:
            return self.images['sprites'][sprite_size][name][state][self.images['sprites_data'][name]['frame_data'][state]['frame_index'] if animated else 0].copy()

    def reset_sprite(self, name):
        for state, frame_data in self.main.assets.images['sprites_data'][name]['frame_data'].items():
            if state.endswith(' animated'):
                frame_data['frame_count'] = 0
                frame_data['frame_index'] = 0
                frame_data['loops'] = 0

    def update(self):
        for sprite_name, sprite_data in self.images['sprites_data'].items():
            for sprite_state, state_data in self.images['sprites_data'][sprite_name]['frame_data'].items():
                if sprite_state not in ['states', 'num_states', 'sprite_type']:
                    if state_data['num_frames'] > 1:
                        state_data['frame_count'] += 1
                        if state_data['frame_count'] >= state_data['frame_counts'][state_data['frame_index']]:
                            state_data['frame_count'] = 0
                            state_data['frame_index'] += 1
                            if state_data['frame_index'] >= state_data['num_frames']:
                                state_data['frame_index'] = 0
                                state_data['loops'] += 1

    def quit(self):
        del self.settings['menus']['choose_level']
        with open(os.path.join(self.assets_path, 'settings.json'), 'w') as file:
            json.dump(obj=self.settings, fp=file, indent=2)
        with open(os.path.join(self.assets_path, 'data.json'), 'w') as file:
            json.dump(obj=self.data, fp=file, indent=2)

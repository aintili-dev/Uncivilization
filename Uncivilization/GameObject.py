import pygame as pg
import numpy as np
import copy
import json
import pickle
import random

# from Uncivilization.Camera import *
from Uncivilization.MapNameToInstructions import *

NUM_MAPS = 6
NUM_CHARACTERS = 6


class GameObject:
    def __init__(self, player_input, game_state, renderer, audio_mixer):
        self.eps = 0.005
        self.dt = 2 ** 31
        self.TARGET_FPS = 60
        self.MAX_FPS = 60
        self.drawDiagnostic = False
        self.cleanDiagnostic = False
        self.PlayerInput = player_input
        self.GameState = game_state
        self.Renderer = renderer
        self.AudioMixer = audio_mixer

    def calc_fps(self):
        return 1 / self.dt


class PlayerInput:
    def __init__(self):
        self.events = None
        self.keyboard_dictionary = None
        self.prevEvents = None
        self.scroll_dir = 0
        self.mc_pos = None
        self.m_pos = None
        self.lc_held0 = None
        self.lc_held1 = None
        self.scrolling = False
        self.custom_inputs = {}


class GameState:
    def __init__(self):
        self.isPaused = False
        self.rows = 25
        self.cols = 50
        self.grid_size = (self.rows, self.cols)
        self.board = {}
        self.inMainMenu = True
        self.inMapSelect = False
        self.inSettingsMenu = False
        self.start_game = False
        self.map_type = None
        self.skip_animation = False


class AudioMixer:
    def __init__(self, sounds):
        self.sounds_dict = sounds

    def stop_all(self):
        for sound in self.sounds_dict.values():
            sound.stop()

    def stop_all_except(self, exception_list):
        for name, sound in self.sounds_dict.items():
            if name not in exception_list:
                sound.stop()

    def fadeout_all(self, fadeout_time=750):
        for sound in self.sounds_dict.values():
            sound.fadeout(fadeout_time)

    def fadeout_all_except(self, exception_list, fadeout_time=750):
        for name, sound in self.sounds_dict.items():
            if name not in exception_list:
                sound.fadeout(fadeout_time)


class Renderer:
    def __init__(self, screen, assets, n_max=14, n_min=4):
        self.assets = assets
        self.n_max = n_max
        self.n_min = n_min
        self.defaultColor = (0, 0, 0)
        self.extraLargeText = pg.font.SysFont("ubuntucondensed", 60)
        self.largeText = pg.font.SysFont("ubuntucondensed", 30)
        self.smallText = pg.font.SysFont("ubuntucondensed", 20)
        self.coordText = pg.font.SysFont("ubuntucondensed", 40)
        self.screen = screen
        self.width = pg.display.get_surface().get_width()
        self.height = pg.display.get_surface().get_height()
        self.origin = (self.width // 2, self.height // 2)
        self.to_update = []
        self.camera = None
        self.full_redraw = True
        self.mainMenuBoxes = self.getMainMenuBoxes()
        self.mapSelectBoxes = self.getMapSelectBoxes()
        self.defaultTextColor = (255, 255, 255)
        self.settingsBoxFormatting = self.setSettingsBoxFormatting()
        self.settingsMenuBoxes = self.getSettingsMenuBoxes()
        self.mapSelectRedraw = None


    def getMainMenuBoxes(
        self,
        text_color=(255, 255, 255),
        background_color_1=(0, 0, 0),
        background_color_2=(0, 0, 0),
        center_1=None,
    ):
        title_string_1 = "UN"
        title_string_2 = "Civilization"
        game_string = "Play Game"
        settings = "Settings"

        w = self.width
        h = self.height

        largeText = self.largeText
        extraLargeText = self.extraLargeText

        TextSurfA = extraLargeText.render(title_string_1, True, (255, 0, 0), (0, 0, 0))
        TextSurfB = extraLargeText.render(title_string_2, True, text_color, (0, 0, 0))

        sa, _ = TextSurfA.get_size()
        sb, _ = TextSurfB.get_size()
        centerax = (w - sb) / 2
        centeray = h // 2 if (center_1 is None or center_1 > h // 2) else center_1
        centerbx = (w + sa) / 2

        text_rectA = TextSurfA.get_rect(center=(centerax, centeray))
        text_rectB = TextSurfB.get_rect(center=(centerbx, h // 2))

        TextSurf1 = largeText.render(game_string, True, text_color, background_color_1)
        text_rect1 = TextSurf1.get_rect(center=(w // 2 - w // 10, h // 2 + h // 10))

        TextSurf2 = largeText.render(settings, True, text_color, background_color_2)
        text_rect2 = TextSurf2.get_rect(center=(w // 2 + w // 10, h // 2 + h // 10))

        return [
            [TextSurfA, text_rectA],
            [TextSurfB, text_rectB],
            [TextSurf1, text_rect1],
            [TextSurf2, text_rect2],
        ]

    def updateMainMenuBoxes(
        self, background_color_1=(0, 0, 0), background_color_2=(0, 0, 0), center_1=None
    ):
        self.mainMenuBoxes = self.getMainMenuBoxes(
            background_color_1=background_color_1,
            background_color_2=background_color_2,
            center_1=center_1,
        )

    def setSettingsBoxFormatting(self):
        w = self.width
        h = self.height

        arrow_right = self.assets["initial_screen"]["right_arrow.png"]
        arrow_left = pg.transform.flip(arrow_right, True, False)
        self.assets["initial_screen"]["left_arrow.png"] = arrow_left

        title_string_1 = "Settings"

        largeText = self.largeText
        extraLargeText = self.extraLargeText

        TextSurf1 = extraLargeText.render(title_string_1, True, self.defaultTextColor, (0, 0, 0))
        text_rect1 = TextSurf1.get_rect(center=(w // 5, h // 10))

        formatting_info = {"title_box_and_rect": [TextSurf1, text_rect1]}

        d_strings = ["Resolution", "These", "Do", "Nothing", "for now :("]
        surfaces = []
        largest_rect_width = 0
        largest_rect_height = 0
        for d in d_strings:
            TextSurf = largeText.render(d, True, self.defaultTextColor, (0, 0, 0))
            surfaces.append(TextSurf)
            rw, rh = TextSurf.get_rect().size
            if rw > largest_rect_width:
                largest_rect_width = rw

            if rh > largest_rect_height:
                largest_rect_height = rh

        formatting_info.update(
            {
                "largest_display_rect_width": 1.3 * largest_rect_width,
                "largest_display_rect_height": largest_rect_height,
                "display_strings": d_strings,
                "rows": len(d_strings),
                "display_surfaces": surfaces,
            }
        )

        value_strings = ["9999 X 9999", "More", "Useless", "Strings", "!!!!!!!"]
        largest_rect_width = 0
        largest_rect_height = 0
        for v in value_strings:
            rw, rh = largeText.size(v)
            if rw > largest_rect_width:
                largest_rect_width = rw

            if rh > largest_rect_height:
                largest_rect_height = rh

        formatting_info.update(
            {
                "largest_value_rect_width": 3 * largest_rect_width,
                "largest_value_rect_height": largest_rect_height,
                "place_holder_strings": value_strings,
            }
        )
        return formatting_info

    def settings_Descriptors(self):

        w = self.width
        h = self.height
        largeText = self.largeText

        formatting_info = self.settingsBoxFormatting
        largest_rect_width = formatting_info["largest_display_rect_width"]
        largest_rect_height = formatting_info["largest_display_rect_height"]

        rows = formatting_info["rows"]
        cols = 1

        x0 = formatting_info["title_box_and_rect"][1].topleft[0]
        y0 = h // 5

        w_takeup = largest_rect_width
        h_takeup = (3 * h / 5) * 1.01
        desc_rects = []
        surfaces = formatting_info["display_surfaces"]
        for i in range(len(surfaces)):
            surface = surfaces[i]

            row_num = i
            col_num = 0
            rect = self.generate_rect_for_plot(
                (rows, cols), (x0, y0), (w_takeup, h_takeup), (row_num, col_num), x_buff=0
            )
            desc_rects.append([surface, rect])
        
        self.settingsBoxFormatting["display_surround_box"] = desc_rects[0]

        return desc_rects

    def settings_Interactables(self):
        w = self.width
        h = self.height
        largeText = self.largeText

        formatting_info = self.settingsBoxFormatting

        arrow_right = self.assets["initial_screen"]["right_arrow.png"]
        arrow_left = self.assets["initial_screen"]["left_arrow.png"]

        arrow_size = arrow_right.get_size()
        
        largest_rect_width = formatting_info["largest_value_rect_width"]
        largest_rect_height = formatting_info["largest_value_rect_height"]

        largest_arrow_size = (int(largest_rect_width / 10), int(largest_rect_height))
        if arrow_size != largest_arrow_size:
            arrow_right = pg.transform.scale(arrow_right, largest_arrow_size)
            self.assets["initial_screen"]["right_arrow.png"] = arrow_right
            arrow_left = pg.transform.flip(arrow_right, True, False)
            self.assets["initial_screen"]["left_arrow.png"] = arrow_left

        
        first_setting_box = formatting_info["display_surround_box"]

        x0 = first_setting_box[1].bottomright[0] + w / 4
        y0 = first_setting_box[1].topleft[1] - max(w//50,1)

        rows = formatting_info["rows"]
        cols = 1

        w_takeup = largest_rect_width
        h_takeup = (3 * h / 5) * 1.01
        interact_rects = []
        interact_strings = formatting_info["place_holder_strings"]
        for i in range(len(interact_strings)):
            interact_string = interact_strings[i]
            TextSurf = largeText.render(interact_string, True, self.defaultTextColor, (0, 0, 0))

            row_num = i
            col_num = 0
            rect = self.generate_rect_for_plot(
                (rows, cols), (x0, y0), (w_takeup, h_takeup), (row_num, col_num), x_buff=0
            )
            interact_rects.append([TextSurf, rect])
        
        ref_rect = interact_rects[0][1]

        x0 = ref_rect.bottomright[0]
        y0 = ref_rect.topleft[1]
        size = arrow_right.get_size()
        x0 -= size[0]
        nw = size[0]
        nh = ref_rect.height
        new_rect = pg.Rect((x0,y0),(nw,nh))

        interact_rects.append([arrow_right,new_rect])

        x0 = ref_rect.topleft[0]
        y0 = ref_rect.topleft[1]
        size = arrow_left.get_size()
        nw = size[0]
        nh = ref_rect.height
        new_rect = pg.Rect((x0,y0),(nw,nh))

        interact_rects.append([arrow_left,new_rect])


        return interact_rects

    def getSettingsMenuBoxes(
        self,
        background_color_1=(0, 0, 0),
        background_color_2=(0, 0, 0),
        center_1=None,
    ):
        title_box_info = self.settingsBoxFormatting["title_box_and_rect"]
        descriptors = self.settings_Descriptors()
        interactables = self.settings_Interactables()

        descriptors.insert(0,title_box_info)

        return [descriptors, interactables]

    def updateSettingsMenuBoxes(
        self, background_color_1=(0, 0, 0), background_color_2=(0, 0, 0), center_1=None
    ):
        self.settingsMenuBoxes = self.getSettingsMenuBoxes(
            background_color_1=background_color_1,
            background_color_2=background_color_2,
            center_1=center_1,
        )

    def generate_rect_for_plot(
        self,
        size,
        start_tl,
        takeup,
        plot_coord,
        x_buff=None,
        y_buff=None,
    ):
        w = self.width
        h = self.height

        x_buff = x_buff if x_buff is not None else max(w // 50, 1)
        y_buff = y_buff if y_buff is not None else max(w // 50, 1)

        rows, cols = size
        x0, y0 = start_tl
        w_takeup, h_takeup = takeup

        space_xbuff = (cols + 1) * x_buff
        space_ybuff = (rows + 1) * y_buff

        r_w = (w_takeup - space_xbuff) // cols
        r_h = (h_takeup - space_ybuff) // rows
        wh = (r_w, r_h)

        row_num, col_num = plot_coord

        tl_point = (
            x0 + col_num * r_w + (col_num + 1) * x_buff,
            y0 + row_num * r_h + (row_num + 1) * y_buff,
        )
        return pg.Rect(tl_point, wh)

    def getMapSelectBoxes(self):
        w = self.width
        h = self.height

        rows = 2
        cols = NUM_MAPS // rows

        x0 = w // 8
        y0 = h // 16

        w_takeup = (3 * w) // 4
        h_takeup = h // 2

        rects = []
        for i in range(NUM_MAPS):
            row_num = i // (rows + 1)
            col_num = i % (rows + 1)
            rect = self.generate_rect_for_plot(
                (rows, cols), (x0, y0), (w_takeup, h_takeup), (row_num, col_num)
            )
            rects.append(rect)

        rows = 1
        cols = 1

        x0 = w // 8
        y0 = (8 * h) // 15

        w_takeup = (3 * w) // 4
        h_takeup = h // 4

        row_num = 0
        col_num = 0
        rect = self.generate_rect_for_plot(
            (rows, cols), (x0, y0), (w_takeup, h_takeup), (row_num, col_num)
        )
        rects.append(rect)

        rows = 1
        cols = NUM_CHARACTERS

        x0 = w // 8
        y0 = (3 * h) // 4

        w_takeup = (3 * w) // 4
        h_takeup = h // 5

        row_num = 0
        for i in range(NUM_CHARACTERS):
            col_num = i
            rect = self.generate_rect_for_plot(
                (rows, cols), (x0, y0), (w_takeup, h_takeup), (row_num, col_num)
            )
            rects.append(rect)

        return rects

    def updateMapSelectBoxes(self):
        self.mapSelectBoxes = self.getMapSelectBoxes()

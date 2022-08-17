import pygame as pg
import numpy as np

from Uncivilization.Hex import *


def updateInputs(game):
    inputs = game.PlayerInput
    inputs.events = pg.event.get()
    inputs.keyboard_dictionary = pg.key.get_pressed()
    inputs.m_pos = pg.mouse.get_pos()


def basicUserInputUpdateState(game):
    r = game.Renderer
    inputs = game.PlayerInput
    gamestate = game.GameState
    cam = r.camera
    events = inputs.events
    for event in events:
        if event.type == pg.QUIT:
            quit()

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                gamestate.isPaused = not gamestate.isPaused

                if gamestate.isPaused:
                    # trigger load pause screen
                    a = 1

                else:
                    # trigger clean pause screen
                    # resume game
                    a = 2

        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 3:
                if game.drawDiagnostic:
                    game.cleanDiagnostic = True
                game.drawDiagnostic = not game.drawDiagnostic
            elif event.button == 1:
                m_pos = pg.mouse.get_pos()
                inputs.mc_pos = m_pos

        elif event.type == pg.MOUSEWHEEL:
            if inputs.scrolling is False:
                inputs.scroll_dir = event.y
                inputs.scrolling = True

        elif event.type == pg.VIDEORESIZE:
            r.width = event.w
            r.height = event.h

    if pg.mouse.get_pressed()[0]:
        inputs.lc_held0 = inputs.lc_held1
        inputs.lc_held1 = pg.mouse.get_pos()
    else:
        inputs.lc_held0 = None
        inputs.lc_held1 = None


def basicUserInputUpdateState_MainMenu(game):
    r = game.Renderer
    inputs = game.PlayerInput
    gamestate = game.GameState
    events = inputs.events
    for event in events:
        if event.type == pg.QUIT:
            quit()
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                m_pos = pg.mouse.get_pos()
                inputs.mc_pos = m_pos
            if event.button == 3:
                if game.drawDiagnostic:
                    game.cleanDiagnostic = True
                game.drawDiagnostic = not game.drawDiagnostic
        elif event.type == pg.VIDEORESIZE:
            r.width = event.w
            r.height = event.h


def basicUserInputUpdateState_MapSelectMenu(game):
    r = game.Renderer
    inputs = game.PlayerInput
    gamestate = game.GameState
    events = inputs.events
    for event in events:
        if event.type == pg.QUIT:
            quit()
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                m_pos = pg.mouse.get_pos()
                inputs.mc_pos = m_pos
            if event.button == 3:
                if game.drawDiagnostic:
                    game.cleanDiagnostic = True
                game.drawDiagnostic = not game.drawDiagnostic
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                gamestate.inMapSelect = False
                gamestate.inMainMenu = True
                gamestate.skip_animation = True

        elif event.type == pg.VIDEORESIZE:
            r.width = event.w
            r.height = event.h


def basicUserInputLogic(game):
    rend = game.Renderer
    gs = game.GameState
    inputs = game.PlayerInput
    mc_pos = inputs.mc_pos
    cam = rend.camera
    scale_factor = 1 / cam.screen_to_display_ratio

    if mc_pos:
        v = screen_pixel_to_axial(game, mc_pos)
        col, row = axial_to_doubled(v)
        q, r = v
        print(f"{q},{r} | {col},{row}\n")

    if inputs.scrolling:
        cam.zoom_and_recenter(game)
        inputs.scrolling = False
        rend.full_redraw = True

    if inputs.lc_held1 is not None and inputs.lc_held0 is not None:
        x0, y0 = inputs.lc_held0
        x1, y1 = inputs.lc_held1

        diffx = x1 - x0
        diffy = y1 - y0
        diff = (-scale_factor * diffx, -scale_factor * diffy)
        # diff = (-diffx/scale_factor,-diffy/scale_factor)

        cam.add_to_center(diff)

        rend.full_redraw = True
        if inputs.lc_held1 == inputs.lc_held0:
            rend.full_redraw = False


def basicUserInputLogic_MainMenu(game):
    rend = game.Renderer
    gs = game.GameState
    inputs = game.PlayerInput
    mc_pos = inputs.mc_pos
    m_pos = inputs.m_pos
    _, _, play_game_info, settings_info = rend.mainMenuBoxes
    _, rect_play = play_game_info
    _, rect_settings = settings_info

    if mc_pos is not None:
        if rect_play.collidepoint(mc_pos):
            # We have hit play_game
            gs.inMainMenu = False
            gs.inMapSelect = True

        elif rect_settings.collidepoint(mc_pos):
            # We have hit setting
            gs.inSettingsMenu = True

    if m_pos is not None:
        if rect_play.collidepoint(m_pos):
            rend.updateMainMenuBoxes(background_color_1=(50, 50, 50))
        elif rect_settings.collidepoint(m_pos):
            rend.updateMainMenuBoxes(background_color_2=(50, 50, 50))
        else:
            rend.updateMainMenuBoxes()
    else:
        rend.updateMainMenuBoxes()


def basicUserInputLogic_MapSelectMenu(game):
    rend = game.Renderer
    gs = game.GameState
    inputs = game.PlayerInput
    mc_pos = inputs.mc_pos
    m_pos = inputs.m_pos
    boxes = rend.mapSelectBoxes
    box = boxes[0]

    if mc_pos is not None:
        if box.collidepoint(mc_pos):
            gs.inMapSelect = False
            gs.start_game = True
            gs.map_type = "random"

    rend.updateMapSelectBoxes()


def basicUserInputUpdateState_SettingsMenu(game):
    r = game.Renderer
    inputs = game.PlayerInput
    gamestate = game.GameState
    events = inputs.events
    for event in events:
        if event.type == pg.QUIT:
            quit()
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                m_pos = pg.mouse.get_pos()
                inputs.mc_pos = m_pos
            if event.button == 3:
                if game.drawDiagnostic:
                    game.cleanDiagnostic = True
                game.drawDiagnostic = not game.drawDiagnostic
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                gamestate.inSettingsMenu = False
                gamestate.skip_animation = True

        elif event.type == pg.VIDEORESIZE:
            r.width = event.w
            r.height = event.h


def basicUserInputLogic_SettingsMenu(game):
    rend = game.Renderer
    gs = game.GameState
    inputs = game.PlayerInput
    mc_pos = inputs.mc_pos
    m_pos = inputs.m_pos
    boxes = rend.settingsMenuBoxes

    rend.updateSettingsMenuBoxes()

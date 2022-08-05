import pygame as pg
import numpy as np
import random
import sys
import time

from Uncivilization.Hex import *
from Uncivilization.Camera import *
from Uncivilization.MapNameToInstructions import *


def draw_board(game):
    state = game.GameState
    board = state.board
    rend = game.Renderer
    screen = rend.screen
    cam = rend.camera

    cam.update_display_as_world_section()
    display = cam.surface

    w = rend.width
    h = rend.height

    display = pg.transform.scale(display, (w, h))
    screen.blit(display, (0, 0))


def diagnosticsDraw(game):
    render = game.Renderer
    w = render.width
    h = render.height
    screen = render.screen
    largeText = render.largeText

    dt_string = "dt: " + format(1000 * game.dt, "4.0f") + "ms"
    fps_string = "FPS: " + format(game.calc_fps(), "4.0f")

    dt_mock = "  dt:  999ms"
    fps_mock = "  FPS:  9999"

    TextSurfMock = largeText.render(fps_mock, False, (255, 255, 255))
    text_rect_mock = TextSurfMock.get_rect(center=(12 * w // 17, 30))

    TextSurf = largeText.render(fps_string, False, (255, 255, 255))
    text_rect = TextSurf.get_rect(center=(12 * w // 17, 30))

    pg.draw.rect(screen, (0, 0, 0), text_rect_mock)
    screen.blit(TextSurf, text_rect)

    TextSurfMock = largeText.render(dt_mock, False, (255, 255, 255))
    text_rect_mock = TextSurfMock.get_rect(center=(9 * w // 10, 30))

    TextSurf = largeText.render(dt_string, False, (255, 255, 255))
    text_rect = TextSurf.get_rect(center=(9 * w // 10, 30))

    pg.draw.rect(screen, (0, 0, 0), text_rect_mock)
    screen.blit(TextSurf, text_rect)

    pg.draw.line(screen, (0, 0, 255), (w // 2, 0), (w // 2, h))
    pg.draw.line(screen, (0, 0, 255), (0, h // 2), (w, h // 2))

    pg.display.update()


def cleanDiagnosticDraw(game):
    if game.cleanDiagnostic:
        # print("clean")
        screen = game.Renderer.screen
        screen.fill(game.Renderer.defaultColor)
        if game.GameState.start_game:
            draw_board(game)
        game.cleanDiagnostic = False
        pg.display.update()


def draw(game):
    r = game.Renderer
    screen = r.screen

    if r.full_redraw:
        r.full_redraw = False
        screen.fill((200, 200, 200))
        draw_board(game)
        pg.display.update()

    diagnosticsDraw(game) if game.drawDiagnostic else cleanDiagnosticDraw(game)


def drawSettingsMenu(game):
    r = game.Renderer
    screen = r.screen
    screen.fill((0, 0, 0))

    boxes_disp, boxes_interact = r.settingsMenuBoxes
    title_box = boxes_disp[0]
    surf, rect = title_box
    pg.draw.rect(screen, (0, 0, 0), rect)
    screen.blit(surf, rect)

    boxes = boxes_disp[1:]
    for box_info in boxes:
        surf, rect = box_info
        sx, sy = surf.get_size()
        centerx, centery = rect.center

        centerx -= sx // 2
        centery -= sy // 2

        pg.draw.rect(screen, (100, 100, 100), rect, width=3)
        screen.blit(surf, (centerx, centery))
         
    for box_info in boxes_interact:
        surf, rect = box_info
        sx, sy = surf.get_size()
        centerx, centery = rect.center

        centerx -= sx // 2
        centery -= sy // 2

        #pg.draw.rect(screen, (100, 100, 100), rect, width=3)
        screen.blit(surf, (centerx, centery))


    pg.display.update()
    diagnosticsDraw(game) if game.drawDiagnostic else cleanDiagnosticDraw(game)


def drawMenu(game):
    r = game.Renderer
    screen = r.screen
    screen.fill((0, 0, 0))
    boxes = r.mainMenuBoxes
    for box_info in boxes:
        surf, rect = box_info
        pg.draw.rect(screen, (0, 0, 0), rect)
        screen.blit(surf, rect)

    pg.display.update()
    diagnosticsDraw(game) if game.drawDiagnostic else cleanDiagnosticDraw(game)


def drawMapSelect(game, timer):
    r = game.Renderer
    screen = r.screen
    screen.fill((0, 0, 0))
    rects = r.mapSelectBoxes
    for rect in rects:
        c = (100, 100, 100)
        pg.draw.rect(screen, c, rect)

    drawEffect = MAP_TO_DISPLAY["random"]
    drawEffect(game, rects[0], c, timer)

    pg.display.update()
    diagnosticsDraw(game) if game.drawDiagnostic else cleanDiagnosticDraw(game)


def distance_to_extrema_rows(n_rows, size):
    return size * (1.5 * n_rows + 1)


def init_world_render(game):
    t_load = time.time()
    gamestate = game.GameState
    rows, cols = gamestate.grid_size

    board = gamestate.board
    rend = game.Renderer
    cam = rend.camera
    s = cam.hex_asset_size[1] / 2

    w_world = cam.world_size[0]
    d_from_bottom = cam.d_from_bottom

    cols_right = (
        len([None for key in board.keys() if key.split(",")[1] == "0" and "-" not in key]) - 1
    )
    origin_x = w_world - (cols_right + 0.5) * cam.hex_asset_size[0]
    origin_y = d_from_bottom
    cam.AXIAL_ORIGIN_PIXEL = (origin_x, origin_y)

    for tile in board.values():
        tile.draw_tile_images_to_world(game)
        tile.draw_coords(game, ctype="both")

    dt = time.time() - t_load
    dt = format(dt, "0.2f")
    byte_size_row = cam.WORLD_SURFACE.get_pitch()
    byte_size = byte_size_row * cam.WORLD_SURFACE.get_size()[1]
    byte_size /= 1024 * 1024 * 1024
    byte_size = format(byte_size, "0.2f")
    print(f"Finished initializing world in {dt}s.\nIt is ~{byte_size} GB (using pitch * height)")

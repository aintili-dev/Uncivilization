import pygame as pg
import numpy as np
import random
import time

from Uncivilization.Hex import *
from Uncivilization.Camera import *


def convert_alphas(r):
    t0 = time.time()
    items = r.assets["base_hexes"].items()

    r.assets["base_hexes"].update({img_name: img.convert_alpha() for img_name, img in items})

    dt = time.time() - t0
    dt = format(1000 * dt, "0.2f")
    print(f"Finished converting {len(items)} assets in {dt}ms")
    return r.assets["base_hex_size"]


def convert_hexes_and_set_camera(game):
    t0 = time.time()
    r = game.Renderer
    play_rows, play_cols = game.GameState.playable_grid_size
    rows, cols = game.GameState.grid_size

    convert_alphas(r)

    hex_asset_size = r.assets["base_hex_size"]
    game.Renderer.camera = Camera(
        hex_asset_size, 
        r.width,
        r.height,
        rows,
        cols,
        play_rows,
        play_cols,
        n_max=14,
        n_min=4
    )

    dt = time.time() - t0
    dt = format(1000 * dt, "0.2f")
    print(f"Finished Setting Camera surfaces in {dt}ms")


def get_random_dots_info(game, rect, rect_color, background_color, text_rect, redraw_list):
    rend = game.Renderer
    screen = rend.screen

    x0, y0 = rect.topleft
    x1, y1 = rect.bottomright

    buffx = (x1 - x0) / 10
    buffy = (y1 - y0) / 10

    dots_to_draw = np.random.randint(20, 30)
    r = min(buffx, buffy) // 2

    xtr, ytr = text_rect.topleft
    xtr = xtr - r
    ytr = ytr - r
    wtr = text_rect.width + 2 * r
    htr = text_rect.height + 2 * r
    logical_rect = pg.rect.Rect((xtr, ytr), (wtr, htr))

    if rect.collidepoint(pg.mouse.get_pos()) or redraw_list is None:
        redraw_list = []
        for i in range(dots_to_draw):
            color = random.choice(
                [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255), (255, 255, 0)]
            )
            rx = np.random.uniform(x0 + buffx, x1 - buffx)
            ry = np.random.uniform(y0 + buffy, y1 - buffy)
            while logical_rect.collidepoint((rx, ry)):
                rx = np.random.uniform(x0 + buffx, x1 - buffx)
                ry = np.random.uniform(y0 + buffy, y1 - buffy)
            redraw_list.append([rx, ry, color, r])
    return redraw_list


def draw_random_dots(game, rect, rect_color, timer, background_color=(0, 0, 0)):
    rend = game.Renderer
    screen = rend.screen

    title_string = "Random"
    largeText = rend.largeText
    TextSurf = largeText.render(title_string, True, (0, 0, 0))
    text_rect = TextSurf.get_rect(center=rect.center)

    redraw = rend.mapSelectRedraw
    if redraw is None:
        game.Renderer.mapSelectRedraw = get_random_dots_info(
            game, rect, rect_color, background_color, text_rect, redraw
        )

    if timer.smart_peek_timer() > 0.333333:
        timer.end_timer()
        game.Renderer.mapSelectRedraw = get_random_dots_info(
            game, rect, rect_color, background_color, text_rect, redraw
        )
        timer.start_timer()

    to_draw = rend.mapSelectRedraw
    for draw_info in to_draw:
        rx, ry, color, r = draw_info
        pg.draw.circle(screen, color, (rx, ry), r)

    screen.blit(TextSurf, text_rect)


def random_tiles(game):
    state = game.GameState
    original_rows, original_cols = state.playable_grid_size
    rows,cols = state.grid_size

    imgs = [
        "red",
        "dark_green",
        "light_green",
        "yellow",
        "dark_blue",
        "light_blue",
        "white",
    ]

    # up grid_height//2 and down grid_height // 2
    # same, left and right
    r_0 = -(rows // 2)
    for r in range(rows):
        row = r_0 + r
        col_0 = -cols + 1 if row % 2 == 0 else -cols
        for c in range(cols):
            col = col_0 + 2 * c
            cube = doubled_to_cube(row, col)
            img = random.choice(imgs)
            img = f"{img}_hex_and_border.png"
            tile = Hex(cube=cube, images=[img])
            # tile = Hex(cube=cube, images=["red_hex_and_border.png"])
            q, r = tile.v
            tile.is_void = True if abs(row) > original_rows or abs(col) > original_cols else False
            state.board.update({f"{q},{r}": tile})

MAP_TO_FUNC = {"random": random_tiles}

MAP_TO_DISPLAY = {"random": draw_random_dots}

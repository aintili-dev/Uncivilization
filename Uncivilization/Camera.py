import pygame as pg
from Uncivilization.Hex import *

S3 = 3 ** (1 / 2)
INV_S3 = S3 * (1 / 3)


class Camera:
    def __init__(self, hex_asset_size, w_scr, h_scr, rows, cols, n_max=14, n_min=4):
        self.n_min = n_min
        self.n_max = n_max
        self.hex_asset_size = hex_asset_size
        self.hex_size = 0.5 * self.hex_asset_size[1]
        self.w_scr = w_scr
        self.h_scr = h_scr
        self.screen_ratio = h_scr / w_scr
        self.n_mid = (n_max + n_min) // 2
        w = int(self.n_mid * hex_asset_size[0])
        h = int(w * self.screen_ratio)
        self.surface = pg.Surface((w, h))
        self.w_max = n_max * hex_asset_size[0]
        self.h_max = self.w_max * self.screen_ratio
        self.w_min = n_min * hex_asset_size[0]
        self.h_min = self.w_min * self.screen_ratio
        self.center = (0, 0)
        self.screen_to_display_ratio = self.w_scr / w
        self.is_stationary = True
        self.reverse = False
        self.zoom_level = 1

        size = self.hex_asset_size[1] / 2
        rows_bot = -(-rows // 2) if rows % 2 == 0 else -(-rows // 2) - 1
        rows_top = rows // 2 if rows % 2 == 1 else (rows // 2) - 1

        self.d_from_top = size * (1.5 * rows_top + 1)
        self.d_from_bottom = size * (1.5 * rows_bot + 1)
        w_world = (cols + 0.5) * self.hex_asset_size[0]
        h_world = self.d_from_top + self.d_from_bottom

        self.world_size = (w_world, h_world)
        self.WORLD_SURFACE = pg.Surface(self.world_size)
        self.AXIAL_ORIGIN_PIXEL = None

    def get_surface_center(self):
        w, h = self.surface.get_size()
        return (w / 2, h / 2)

    def get_bottom_right_and_top_left(self, center=None):
        cx, cy = self.center if center is None else center
        hw, hh = [s / 2 for s in self.surface.get_size()]
        br = (cx + hw, cy + hh)
        tl = (cx - hw, cy - hh)
        return br, tl

    def get_camera_offset(self, game):
        return self.center

    def update_zoom_level(self, zl, game):
        cw, ch = self.surface.get_size()
        nw, nh = (cw * zl, ch * zl)

        if nw > self.w_max or nh > self.h_max:
            nw = self.w_max
            nh = self.h_max

        elif nw < self.w_min or nh < self.h_min:
            nw = self.w_min
            nh = self.h_min

        self.surface = pg.Surface((nw, nh))
        self.screen_to_display_ratio = self.w_scr / nw

    def zoom(self, incr, game):
        new_zoom = self.zoom_level + incr
        self.update_zoom_level(new_zoom, game)

    def update_center(self, cen, game):
        gs = game.GameState
        board = gs.board

        cx, cy = cen
        row, col = game.GameState.grid_size

        w, h = self.surface.get_size()
        world_size = self.world_size
        origin = self.AXIAL_ORIGIN_PIXEL

        max_x = world_size[0]
        min_x = 0
        max_y = world_size[1]
        min_y = 0

        br, tl = self.get_bottom_right_and_top_left(center=cen)

        br_worldx = br[0] + origin[0]
        br_worldy = br[1] + origin[1]

        tl_worldx = tl[0] + origin[0]
        tl_worldy = tl[1] + origin[1]

        cx_worldx = cx + origin[0]
        cy_worldy = cy + origin[1]

        # # Overshot right
        if br_worldx > max_x:
            cx_worldx = max_x - w / 2

        # # Overshot left
        if tl_worldx < min_x:
            cx_worldx = min_x + w / 2

        # # Overshot up
        if tl_worldy < min_y:
            cy_worldy = min_y + h / 2

        # # Overshot down
        if br_worldy > max_y:
            cy_worldy = max_y - h / 2

        cx = cx_worldx - origin[0]
        cy = cy_worldy - origin[1]
        self.center = (cx, cy)

    def add_to_center(self, incr, game):
        x1, y1 = incr
        x0, y0 = self.center
        new_center = (x1 + x0, y1 + y0)
        self.update_center(new_center, game)

    def zoom_and_recenter(self, game):
        inputs = game.PlayerInput
        scroll_sp = 0.3
        scroll_amt = -1 * inputs.scroll_dir * game.dt * game.TARGET_FPS * scroll_sp
        self.zoom(scroll_amt, game)
        self.update_center(self.center, game)  # probably not necessary

    def update_display_as_world_section(self):
        origin = self.AXIAL_ORIGIN_PIXEL
        world = self.WORLD_SURFACE

        _, tl = self.get_bottom_right_and_top_left()
        tlx, tly = tl
        tlx += origin[0]
        tly += origin[1]

        proper_rect = pg.Rect((tlx, tly), self.surface.get_size())
        new_surface = world.subsurface(proper_rect)
        self.surface = new_surface

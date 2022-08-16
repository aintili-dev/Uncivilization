import numpy as np
import pygame as pg

ONE_THIRD = 1 / 3
S3 = np.sqrt(3)
INV_S3 = S3 * ONE_THIRD
TO_PIXEL = np.array([[S3, 0.5 * S3], [0, 1.5]])
TO_AXIAL = np.array([[0.57735027, -1 * ONE_THIRD], [0.0, 2 * ONE_THIRD]])


def doubled_to_axial(row, col):
    return cube_to_axial(doubled_to_cube(row, col))


def axial_to_doubled(ax):
    return cube_to_doubled(axial_to_cube(ax))


def doubled_to_cube(row, col):
    x = (col - row) // 2
    z = row
    y = -x - z
    return x, y, z


def cube_to_doubled(cube):
    x, y, z = cube
    col = 2 * x + z
    row = z
    return col, row


def hex_round(ax):
    return cube_to_axial(cube_round(axial_to_cube(ax)))


def axial_to_cube_rounded(ax):
    return cube_round(axial_to_cube(ax))


def cube_to_axial(cube):
    return cube[0], cube[2]


def cube_round(cube):
    x, y, z = cube
    rx = round(x)
    ry = round(y)
    rz = round(z)

    x_diff = abs(rx - x)
    y_diff = abs(ry - y)
    z_diff = abs(rz - z)

    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry - rz
    elif y_diff > z_diff:
        ry = -rx - rz
    else:
        rz = -rx - ry

    return int(rx), int(ry), int(rz)


def axial_to_cube(ax):
    x, z = ax
    return x, -x - z, z


def pixel_to_axial(game, pixel):
    """
    Returns correct axial coord given an unrestricted pixel
    """
    r = game.Renderer
    cam = r.camera

    size = cam.hex_asset_size[1] / 2
    v = (1 / size) * np.matmul(TO_AXIAL, pixel)
    return hex_round(v)


def axial_to_pixel(game, v):
    """
    Given an axial coordinate, return an unrestricted pixel
    """
    r = game.Renderer
    cam = r.camera
    size = cam.hex_asset_size[1] / 2

    x, y = size * np.matmul(TO_PIXEL, v)
    return x, y


def axial_to_display_pixel(game, v):
    """
    Given an axial coordinate, return the center pixel for the display
    """
    r = game.Renderer
    cam = r.camera
    size = cam.hex_asset_size[1] / 2

    offx, offy = cam.get_camera_offset(game)

    x, y = size * np.matmul(TO_PIXEL, v)
    surf_cen = cam.get_surface_center()
    x = x - offx + surf_cen[0]
    y = y - offy + surf_cen[1]
    return x, y


def display_pixel_to_axial(game, pixel):
    """
    Returns correct axial coord given a pixel restricted to [[0,w],[0,h]],
    considers camera's location
    """

    r = game.Renderer
    cam = r.camera
    size = cam.hex_asset_size[1] / 2
    offx, offy = cam.get_camera_offset(game)
    surf_cen = cam.get_surface_center()

    x, y = pixel
    pixel = [x - surf_cen[0] + offx, y - surf_cen[1] + offy]
    pixel = np.array(pixel)

    v = (1 / size) * np.matmul(TO_AXIAL, pixel)
    return hex_round(v)


def screen_pixel_to_axial(game, screen_pixel):
    """
    Returns correct axial coord given a pixel restricted to [[0,w],[0,h]],
    considers camera's location
    """

    r = game.Renderer
    x0, y0 = r.origin
    cam = r.camera
    offx, offy = cam.get_camera_offset(game)
    R = cam.screen_to_display_ratio

    x, y = screen_pixel
    x /= R
    y /= R

    pixel = np.array([x, y])
    return display_pixel_to_axial(game, pixel)


class Hex:
    def __init__(self, cube=None, q=None, r=None, images=[]):
        if cube is None:
            assert q is not None and r is not None
            self.v = np.array([q, r])
            self.cube = axial_to_cube(self.v)

        elif q is None or r is None:
            assert cube is not None
            self.v = np.array(cube_to_axial(cube))
            self.cube = cube
        self.images = images
        self.boarder_img = "outline_hex.png"

    def get_corner(self, center, size, index):
        angle_deg = 60 * index - 30
        angle_rad = np.pi / 180 * angle_deg
        return (center[0] + size * np.cos(angle_rad), center[1] + size * np.sin(angle_rad))

    def get_edge(self, center, size, indeces):
        start, end = indeces
        return self.get_corner(center, size, start), self.get_corner(center, size, end)

    def draw_coords(self, game, ctype="axial"):
        q, r = self.v
        render = game.Renderer
        cam = render.camera
        origin = cam.AXIAL_ORIGIN_PIXEL

        x, y = axial_to_pixel(game, self.v)
        x = x + origin[0]
        y = y + origin[1]
        coord_s = ""
        if ctype == "axial" or ctype == "both":
            coord_s += "{q} , {r}".format(q=int(q), r=int(r))

        if ctype == "both":
            coord_s += "  |  "

        if ctype == "doubled" or ctype == "both":

            col, row = axial_to_doubled([q, r])
            coord_s += f"{col} , {row}"

        TextSurf = render.coordText.render(coord_s, False, (1, 1, 1))
        text_rect = TextSurf.get_rect(center=(x, y))

        
        tl = text_rect.topleft
        imgw,imgh = TextSurf.get_size()
        tlx,tly = tl
        brx = tlx + imgw
        wc = 0
        ctlx = tlx
        prev_w = 0
        for surface in cam.WORLD_SURFACES:
            w_surf, _ = surface.get_size()
            xf = wc + w_surf
            cbrx = min(xf,brx)
            if ctlx != cbrx and ctlx <= xf:
                tlx_p = ctlx - wc

                w_sub_img = min(xf-ctlx,brx-ctlx)
                proper_rect = pg.Rect((prev_w, 0),(w_sub_img,imgh))
                sub_surf = TextSurf.subsurface(proper_rect)

                surface.blit(sub_surf,(tlx_p,tly))

                prev_w += w_sub_img
                ctlx = cbrx
            wc = xf

       # cam.WORLD_SURFACES.blit(TextSurf, text_rect)

    def get_image_for_display(self, game, img="dark_blue_hex_and_border.png"):
        r = game.Renderer
        assets = r.assets["base_hexes"]

        loaded_image = assets[img]
        img_w, img_h = loaded_image.get_size()
        x0, y0 = axial_to_display_pixel(game, self.v)
        dest = (x0 - img_w / 2, y0 - img_h / 2)

        return loaded_image, dest


    def get_image_for_world(self, game, img="dark_blue_hex_and_border.png"):
        r = game.Renderer
        assets = r.assets["base_hexes"]
        cam = r.camera

        origin = cam.AXIAL_ORIGIN_PIXEL

        loaded_image = assets[img]
        img_w, img_h = loaded_image.get_size()
        x0, y0 = axial_to_pixel(game, self.v)

        x_new = x0 + origin[0] - (img_w / 2)
        y_new = y0 + origin[1] - (img_h / 2)

        return loaded_image, (x_new, y_new)

    def draw_tile_images_to_world(self, game):
        rend = game.Renderer
        camera = rend.camera
        surfaces = camera.WORLD_SURFACES

        # TODO, switch loop to do blits instead of blit
        for image in self.images:
            img, tl = self.get_image_for_world(game,img=image)
            imgw,imgh = img.get_size()
            tlx,tly = tl
            brx = tlx + imgw
            wc = 0
            ctlx = tlx
            prev_w = 0
            for surface in surfaces:
                w_surf, _ = surface.get_size()
                xf = wc + w_surf
                cbrx = min(xf,brx)
                if ctlx != cbrx and ctlx <= xf:
                    tlx_p = ctlx - wc

                    w_sub_img = min(xf-ctlx,brx-ctlx)
                    proper_rect = pg.Rect((prev_w, 0),(w_sub_img,imgh))
                    sub_surf = img.subsurface(proper_rect)

                    surface.blit(sub_surf,(tlx_p,tly))

                    prev_w += w_sub_img
                    ctlx = cbrx
                wc = xf

        #asset_dest_pairs = [self.get_image_for_world(game,img=image) for image in self.images]
        #camera.WORLD_SURFACES.blits(asset_dest_pairs)

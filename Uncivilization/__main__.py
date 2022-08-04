import os
import configparser
import pkg_resources
import pygame as pg
import time

from Uncivilization import InitializerFunctions as IF

IMAGES_DIR = pkg_resources.resource_filename("Uncivilization", "images/")
# IMAGES_DIR = pkg_resources.resource_filename("Uncivilization", "test_imgs/")
SOUNDS_DIR = pkg_resources.resource_filename("Uncivilization", "sounds/")
CONFIG_DIR = pkg_resources.resource_filename("Uncivilization", "config/")


def main():
    # pip install -e path/to/Uncivilization will install
    # this as a package. Command Unciv will call this function
    print()
    assets = load_assets()
    sounds = load_sounds()
    player_config = load_player_config()
    IF.initialize_game_object(assets, sounds, player_config)


def load_assets():
    # Load assets
    t0 = time.time()
    n_assets = 0
    assets = {"base_hexes": {}, "initial_screen": {}, "base_hex_size": (-1, -1)}
    cur_size = (-1, -1)
    for img in os.listdir(IMAGES_DIR):
        loaded_img = pg.image.load(os.path.join(IMAGES_DIR, img))
        size = loaded_img.get_size()
        img_category = "base_hexes" if "hex" in img and "and_border" in img else "initial_screen"
        if img_category == "base_hexes":
            if size != cur_size:
                if cur_size == (-1, -1):
                    cur_size = size
                    assets["base_hex_size"] = size
                else:
                    raise Exception(f"Size {size} =/= {cur_size}")
        assets[img_category].update({img: loaded_img})
        n_assets += 1

    dt = time.time() - t0
    dt = format(1000 * dt, "0.2f")
    print(f"Found {n_assets} raw assets in {dt} ms")
    return assets


def load_sounds():
    # Load sounds
    pg.mixer.init()
    t0 = time.time()
    sounds = {
        sound: pg.mixer.Sound(os.path.join(SOUNDS_DIR, sound)) for sound in os.listdir(SOUNDS_DIR)
    }
    dt = time.time() - t0
    dt = format(dt, "0.2f")
    print(f"Found {len(sounds.keys())} wavs in {dt} s\n")
    return sounds


def load_player_config():
    cp = configparser.ConfigParser()
    config_file = os.path.join(CONFIG_DIR, "config.ini")
    cp.read(config_file)
    return cp


main()

import pygame as pg
import numpy as np
import time

from Uncivilization.HandleInputs import *
from Uncivilization.Hex import *


def updatePositions(game):
    pass


def checkCollision(game):
    pass


def handleCollisions(game):
    pass


def updateState(game):
    gamestate = game.GameState
    inputs = game.PlayerInput
    basicUserInputUpdateState(game)
    basicUserInputLogic(game)
    if not gamestate.isPaused:
        updatePositions(game)
        checkCollision(game)
        handleCollisions(game)
    inputs.mc_pos = None


def updateStateMenu(game):
    inputs = game.PlayerInput
    basicUserInputUpdateState_MainMenu(game)
    basicUserInputLogic_MainMenu(game)
    inputs.mc_pos = None


def updateStateSettingsMenu(game):
    inputs = game.PlayerInput
    basicUserInputUpdateState_SettingsMenu(game)
    basicUserInputLogic_SettingsMenu(game)
    inputs.mc_pos = None


def updateStateMapSelect(game):
    inputs = game.PlayerInput
    basicUserInputUpdateState_MapSelectMenu(game)
    basicUserInputLogic_MapSelectMenu(game)
    inputs.mc_pos = None

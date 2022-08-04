import pygame as pg
import time


def play_animation(game, clock):
    gamestate = game.GameState
    if not gamestate.skip_animation:
        execute_animation(game, clock)


def execute_animation(game, clock):
    gamestate = game.GameState
    r = game.Renderer
    tfps = game.TARGET_FPS

    screen = r.screen
    h = r.height
    box, _, _, _ = r.mainMenuBoxes

    surf, _ = box
    center_y = -surf.get_size()[1] / 2

    audio_mixer = game.AudioMixer

    sounds = audio_mixer.sounds_dict
    violin = sounds["violin.wav"]
    record = sounds["record.wav"]
    fall = sounds["fall.wav"]
    crash = sounds["crash.wav"]
    doom = sounds["doom.wav"]

    violin.play()

    violin_needs_stop = True
    record_needs_play = True
    fall_needs_play = True

    t0 = time.time()
    timer = 0
    while center_y <= h // 2:
        clock.tick(tfps)
        r.updateMainMenuBoxes()
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()
            if event.type == pg.KEYDOWN:
                unicode_bool = event.unicode in "abcdefghijklmnopqrstuvwxyz" and event.unicode != ""
                if unicode_bool or event.key == pg.K_ESCAPE:
                    screen.fill((0, 0, 0))
                    center_y = h // 2
                    audio_mixer.stop_all()
                    doom.play()
                    gamestate.skip_animation = True

            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1 or event.button == 3:
                    screen.fill((0, 0, 0))
                    center_y = h // 2
                    audio_mixer.stop_all()
                    doom.play()
                    gamestate.skip_animation = True

        if gamestate.skip_animation:
            break

        t1 = time.time()
        dt = t1 - t0
        t0 = t1
        game.dt = dt
        timer += dt

        if timer > 6:
            if violin_needs_stop:
                violin.stop()
                violin_needs_stop = False
            if record_needs_play:
                record.play()
                record_needs_play = False

        if timer > 7:
            if fall_needs_play:
                fall.play()
                fall_needs_play = False
            r.updateMainMenuBoxes(center_1=center_y)
            boxes = [r.mainMenuBoxes[0], r.mainMenuBoxes[1]]
            center_y += game.dt * tfps * max(h / 200, 1)
        else:
            boxes = [r.mainMenuBoxes[1]]

        for box_info in boxes:
            surf, rect = box_info
            pg.draw.rect(screen, (0, 0, 0), rect)
            screen.blit(surf, rect)

        pg.display.update()

    r.updateMainMenuBoxes(center_1=h // 2)
    boxes = [r.mainMenuBoxes[0], r.mainMenuBoxes[1]]
    for box_info in boxes:
        surf, rect = box_info
        pg.draw.rect(screen, (0, 0, 0), rect)
        screen.blit(surf, rect)

    if not gamestate.skip_animation:
        crash.play()
        audio_mixer.stop_all_except(["crash.wav"])
        # This delay before stopping seems pretty good!
        crash.stop()

        # Doom as soon as we update
        pg.display.update()
        doom.play()

    else:
        pg.display.update()

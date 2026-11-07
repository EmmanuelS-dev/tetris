import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
from src.effects import Effects
from src.game import Game, Screen
from src.renderer import Renderer

def test_each_screen_renders_to_a_software_surface():
    pygame.init()
    surface=pygame.display.set_mode((1000,720))
    renderer=Renderer(surface);effects=Effects();game=Game(seed=1)
    for screen in (Screen.MENU,Screen.CONTROLS,Screen.PLAYING,Screen.PAUSED,Screen.GAME_OVER):
        game.state=screen
        renderer.draw(game,effects,1.0,False)
        assert surface.get_at((500,350)).a==255
    pygame.quit()

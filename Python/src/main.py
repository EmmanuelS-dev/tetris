"""Run with `python -m src.main` from the Python directory."""
import pygame
from .audio import Audio
from .config import FPS,MIN_WINDOW_SIZE,WINDOW_SIZE,high_score_path
from .effects import Effects
from .game import Game
from .input_handler import InputHandler
from .renderer import Renderer

def load_best(path):
    try:return max(0,int(path.read_text(encoding="utf8").strip()))
    except (OSError,ValueError):return 0
def save_best(path,value):
    try:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(f"{value}\n",encoding="utf8")
    except OSError:pass
def handle_events(g,effects,audio):
    mapping={"move":"move","soft_drop":"soft_drop","rotate":"rotate","lock":"lock","hard_drop":"hard_drop","clear":"clear","tetris":"tetris","level":"level","game_over":"game_over"}
    for name,value in g.events:
        if name=="score":effects.scored()
        elif name=="clear":effects.clear_rows(value)
        if name in mapping:audio.play(mapping[name])
    g.events.clear()
def main():
    pygame.init();pygame.font.init();surface=pygame.display.set_mode(WINDOW_SIZE,pygame.RESIZABLE);pygame.display.set_caption("Tetris — Minimal Edition")
    try:
        from pygame._sdl2.video import Window
        Window.from_display_module().min_size=MIN_WINDOW_SIZE
    except (ImportError,AttributeError,pygame.error):pass
    path=high_score_path();g=Game(high_score=load_best(path));effects=Effects();audio=Audio();renderer=Renderer(surface);controls=InputHandler(renderer,audio,effects);clock=pygame.time.Clock();elapsed=0.;best=g.high_score
    while controls.running:
        dt=clock.tick(FPS)/1000.;elapsed+=dt;events=pygame.event.get()
        for e in events:
            if e.type==pygame.VIDEORESIZE:
                surface=pygame.display.set_mode((max(MIN_WINDOW_SIZE[0],e.w),max(MIN_WINDOW_SIZE[1],e.h)),pygame.RESIZABLE);renderer.resize(surface)
        if not controls.process(events,g):break
        controls.update(dt,g);g.update(dt);effects.update(dt);handle_events(g,effects,audio)
        if g.high_score>best:best=g.high_score;save_best(path,best)
        renderer.draw(g,effects,elapsed,audio.muted);pygame.display.flip()
    save_best(path,g.high_score);audio.close();pygame.quit();return 0
if __name__=="__main__":raise SystemExit(main())

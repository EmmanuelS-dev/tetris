"""Optional synthesized sound, disabled automatically if mixer is unavailable."""
import math
from array import array
import pygame

class Audio:
    tones={"move":(340,.035),"soft_drop":(230,.035),"rotate":(510,.055),"lock":(160,.075),"hard_drop":(115,.13),"clear":(680,.16),"tetris":(880,.28),"level":(760,.19),"game_over":(95,.4)}
    def __init__(self):
        self.sounds={};self.available=False;self.muted=False
        try:
            if not pygame.mixer.get_init():pygame.mixer.init(frequency=22050,size=-16,channels=1,buffer=256)
            for name,(freq,duration) in self.tones.items():
                count=int(22050*duration);samples=array('h',(int(math.sin(2*math.pi*freq*i/22050)*(1-i/count)*6000) for i in range(count)))
                self.sounds[name]=pygame.mixer.Sound(buffer=samples.tobytes());self.sounds[name].set_volume(.14)
            self.available=True
        except pygame.error:self.sounds.clear()
    def play(self,name):
        if self.available and not self.muted and name in self.sounds:self.sounds[name].play()
    def toggle(self):self.muted=not self.muted
    def close(self):
        if self.available and pygame.mixer.get_init():pygame.mixer.stop();pygame.mixer.quit()
        self.available=False

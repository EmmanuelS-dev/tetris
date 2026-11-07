from dataclasses import dataclass
import random

@dataclass
class Particle:
    x:float;y:float;vx:float;vy:float;life:float;duration:float;color:tuple[int,int,int]

class Effects:
    def __init__(self,seed=None):self.random=random.Random(seed);self.particles=[];self.score_pulse=0.0
    def clear_rows(self,rows):
        colors=((91,174,186),(151,123,178),(113,166,132),(220,177,91))
        for row in rows:
            for col in range(10):
                for _ in range(2):
                    d=self.random.uniform(.3,.7);self.particles.append(Particle(col+.5,row+.5,self.random.uniform(-2.8,2.8),self.random.uniform(-4.5,-1),d,d,self.random.choice(colors)))
        self.particles=self.particles[-180:]
    def scored(self):self.score_pulse=.28
    def update(self,dt):
        dt=max(0,min(dt,.1));self.score_pulse=max(0,self.score_pulse-dt);alive=[]
        for p in self.particles:
            p.life-=dt
            if p.life>0:p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=7*dt;alive.append(p)
        self.particles=alive

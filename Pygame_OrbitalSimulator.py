# -*- coding: utf-8 -*-
"""
Spyder Editor

Orbital Mechanics Tester

F = (GMm)/r^2

This is a temporary script file.
"""

import pygame,sys
import random
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D








random.seed(time.time())
pygame.init()
CLOCK = pygame.time.Clock()

SCREEN_W, SCREEN_H = 1000,1000
#BG_COLOR = (255,255,255)
#BG_COLOR = (0,0,0)
BG_COLOR = (255/2, 255/2, 255/2)
TIMETICKER = 60
#TIMETICKER = 15


MAXFRAMES = -1
MASS_RADIUS_SCALE = 0.5


GRAV_CONST = 6.67408 # Guessing right now lol


def vect(B1,B2):
    return ((B2.x-B1.x),(B2.y-B1.y))

def dist(B1,B2):
    dx = B2.x - B1.x
    dy = B2.y - B1.y
    return np.sqrt(dx**2 + dy**2)


def GetRandomVelocity(Body,Sun):
    v = vect(Body,Sun)
    init_angle = np.arctan2(v[1],v[0])
    angle = init_angle + (np.pi/2)
    vmax = 7
    
    v_mag = vmax*random.random()
    vx = v_mag*np.cos(angle)
    vy = v_mag*np.sin(angle)
    return (vx,vy)



class TrajectoryMarker:
    def __init__(self,master,radius=2,nframes=100):
        self.master = master
        self.radius = radius
        self.nframes = nframes
        
        self.x = master.x
        self.y = master.y
        
        self.color = master.color
        
        self.master.master.BLITLIST.append(self)
    
    def destroyself(self):
        self.master.master.BLITLIST.remove(self)
        return
    
    def onloop(self):
        self.nframes -= 1
        if self.nframes == 0:
            self.destroyself()
        return
    
    def blitme(self):
        x = int(self.x*self.master.master.ZOOM_FACTOR + self.master.master.X_OFFSET)
        y = int(self.y*self.master.master.ZOOM_FACTOR + self.master.master.Y_OFFSET)
        if self.radius > 1:
            r = int(self.radius*self.master.masterZOOM_FACTOR)
            pygame.draw.circle(self.master.master.DISPLAYSURF,self.color,(x,y),r)
        else:
            self.master.master.DISPLAYSURF.set_at((x,y),self.color)
        return



class Body:
    def __init__(self,master,mass,radius,x0,y0,vx0=0,vy0=0,fixed=False,name='',color=None):
        self.name = name
        self.master = master
        self.mass = mass
        self.radius = radius
        self.fixed = fixed
        self.x = x0
        self.y = y0
        self.vx = vx0
        self.vy = vy0
        if color == None:
            self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        else:
            self.color = color
        
        self.master.BLITLIST.append(self)
        self.master.BODYLIST.append(self)
        self.HX = []
        self.HY = []
        
    def plothistory(self):
        fig = plt.figure(figsize=(8,8))
        ax = fig.add_subplot(111,projection='3d')
        ax.plot(self.HX,self.HY)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        plt.show()
        
        
    def destroy(self):
        try:
            self.master.BLITLIST.remove(self)
            self.master.BODYLIST.remove(self)
        except ValueError:
            pass
        return
        
        
    def onloop(self):
        
        self.HX.append(self.x)
        self.HY.append(self.y)
        
        if not self.fixed:
            self.x += self.vx
            self.y += self.vy
            
            
            
            for body in self.master.BODYLIST:
                if body == self:
                    continue
                v = vect(self,body)
                r = dist(self,body)
                m1 = self.mass
                m2 = body.mass
                F = (GRAV_CONST*m1*m2)/(r**2)
                
                if self.name == 'Foo':
                    print("%0.4f %0.4f"%(self.vx,self.vy))
                    
                    
                if r <= (self.radius + body.radius): # Handle collisions by taking average
                    if body.name != 'Sun':
                        mtot = m1 + m2
                        vxtot = (1/mtot)*(m1*self.vx + m2*body.vx)
                        vytot = (1/mtot)*(m1*self.vy + m2*body.vy)
                        c1 = (m1/mtot)*np.array(self.color)
                        c2 = (m2/mtot)*np.array(body.color)
                        newcolor = tuple(np.mean([c1,c2],axis=0))
                        
                        newx = (self.x + body.x)/2
                        newy = (self.y + body.y)/2
                        
                        newradius = max([self.radius,body.radius])
                        name1 = str(self.name.split(' ')[-1])
                        name2 = str(body.name.split(' ')[-1])
                        newname = "Planet %s+%s"%(name1,name2)
                        
                        
                        new_body = Body(self.master,mtot,newradius,newx,newy,vx0=vxtot,vy0=vytot,name=newname,color=newcolor)
                        self.destroy()
                        body.destroy()
                        print("%s and %s merged."%(self.name,body.name))
                        
                    else: # If self hits the sun, body is destroyed!
                        self.destroy()
                        print("%s fell into the sun."%(self.name))
                    
                
                
                self.vx += (F*(v[0]/r))/m1
                self.vy += (F*(v[1]/r))/m1
        
        
    def blitme(self):
        x = int(self.x*self.master.ZOOM_FACTOR + self.master.X_OFFSET)
        y = int(self.y*self.master.ZOOM_FACTOR + self.master.Y_OFFSET)
        r = int(self.radius*self.master.ZOOM_FACTOR)
        pygame.draw.circle(self.master.DISPLAYSURF,self.color,(x,y),r)
        return














"""
=========================================================================================================================
=========================================================================================================================
"""

class Game:
    def __init__(self):
        print("="*50)
        self.nframes = 0
        self.is_running = True
        self.refresh_background = 1
        self.DISPLAYSURF = pygame.display.set_mode((SCREEN_W,SCREEN_H))
        pygame.display.set_caption("Test")
        
        self.TIMETICKER = TIMETICKER
        
        self.ZOOM_FACTOR = 1
        self.X_OFFSET = 0
        self.Y_OFFSET = 0
        
        self.BLITLIST = []
        self.BODYLIST = []
        
        self.LOOPCOUNTER = 0
        self.TRAJMARKERCOUNTER = 1
        
        # Body(master,mass,radius,x0,y0,vx0,vy0,name)
        
        SUN_FIXED = 1
        
        self.B1 = Body(self,500,20,
                       500,500,
                       0,0,
                       fixed=SUN_FIXED,name='Sun',color=(255,255,0))
        
        nbodies = 20
        vmax = 4
        mmax = 15
        for i in range(nbodies):
            mass = random.randint(1,mmax)
            radius = int(np.ceil(mass*MASS_RADIUS_SCALE))
            x = random.randint(0,1000)
            y = random.randint(0,1000)
            #vx = random.randint(-vmax,vmax)
            #vy = random.randint(-vmax,vmax)
            
            #vx = -vmax + 2*vmax*random.random()
            #vy = -vmax + 2*vmax*random.random()
            
            
            name = "Planet %d"%(i+1)
            body = Body(self,mass,radius,x,y,name=name)
            vel = GetRandomVelocity(body,self.B1)
            vx, vy = vel[0],vel[1]
            body.vx = vx
            body.vy = vy
        
        
    def ModSpeed(self,d):
        self.TIMETICKER += d
        print("TIMETICKER is now %d"%(self.TIMETICKER))
        return
        
    def ModZoom(self,d):
        self.ZOOM_FACTOR += d
        new_screen_w = SCREEN_W * (self.ZOOM_FACTOR)
        new_screen_h = SCREEN_H * (self.ZOOM_FACTOR)
        
        self.X_OFFSET = (SCREEN_W - new_screen_w)/2
        self.Y_OFFSET = (SCREEN_H - new_screen_h)/2
        
        return
        
    def Reinitialize(self):
        #self.PlotHistories()
        self.__init__()
        return
        
    def PlotHistories(self):
        nframes = len(self.BODYLIST[0].HX)
        zs = np.linspace(0,1,nframes)
        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(111,projection='3d')
        plt.grid()
        plt.title("Simulation")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Frame #")
        
        for i,B in enumerate(self.BODYLIST):
            
            #print("Hx Length: %d\nHy Length: %d\nZs Length: %d"%(len(B.HX),len(B.HY),len(zs)))
            
            c = [float(x/255) for x in B.color]
            if B.name != '':
                labelstr = B.name
            else:
                labelstr = "Body %d"%(i)
            ax.plot(B.HX,[-y for y in B.HY],zs,color=c,label=labelstr)
            
            
        plt.legend()
            
        plt.show()
        
        
        
        
        return
        
        
    def on_event(self,event):
        if event.type == pygame.QUIT:
            self.on_cleanup()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.on_cleanup()
            elif event.key == pygame.K_r:
                self.Reinitialize()
            elif event.key == pygame.K_c:
                print("- There are %d remaining bodies."%(len(self.BODYLIST)))
            elif event.key == pygame.K_UP:
                self.ModZoom(0.1)
                print("Zoom Factor: %f"%(self.ZOOM_FACTOR))
            elif event.key == pygame.K_DOWN:
                self.ModZoom(-0.1)
                print("Zoom Factor: %f"%(self.ZOOM_FACTOR))
            elif event.key == pygame.K_RIGHT:
                self.ModSpeed(5)
            elif event.key == pygame.K_LEFT:
                self.ModSpeed(-5)
            
            
            
            
            
            
    def on_loop(self):
        CLOCK.tick(self.TIMETICKER)
        for B in self.BLITLIST:
            B.onloop()
        
        self.LOOPCOUNTER += 1
        if self.LOOPCOUNTER == self.TRAJMARKERCOUNTER:
            for B in self.BODYLIST:
               TrajectoryMarker(B,radius=1,nframes=200)
            self.LOOPCOUNTER = 0
        
        if MAXFRAMES != -1:
            if self.nframes >= MAXFRAMES:
                self.on_cleanup()
        
        
    def on_render(self):
        self.nframes += 1
        if self.refresh_background: self.DISPLAYSURF.fill(BG_COLOR)
        for B in self.BLITLIST:
            B.blitme()
            #continue
            
            
        pygame.display.flip()
        
        
        
        
    def on_cleanup(self):
        self.is_running = False
        #self.PlotHistories()
        pygame.quit()
        sys.exit()
        return
        
    def on_execute(self):
        while self.is_running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()
        
        
if __name__ == '__main__':
    G = Game()
    G.on_execute()
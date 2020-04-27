# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 07:42:03 2020

@author: Philip du Toit
"""

import numpy as np
import pygame, sys
from random import randint
from pygame.locals import *

import random

import gym

WIDTH = 500
HEIGHT = 500

class Ball(pygame.sprite.Sprite):    
    def __init__(self, color, x, y):
        super().__init__()
        
        self.r = 6

        # Set the background color and set it to be transparent
        self.image = pygame.Surface([self.r*2, self.r*2])
        self.image.fill(0)                # RGB 24-bit color... 0 is Black
        self.image.set_colorkey(0)

        pygame.draw.rect(self.image, color, [0, 0, 2*self.r, 2*self.r])

        self.velocity = [randint(-8,8),randint(4,8)]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
    def reset(self, x, y):
        self.velocity = [randint(-8,8),randint(4,8)]
        self.rect.center = (x, y)
        self.bounce()

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

    def bounce(self):
        self.velocity[1] = -self.velocity[1] 

class Paddle(pygame.sprite.Sprite):        
    def __init__(self, color, x, y):
        super().__init__()
        
        self.w = 100
        self.h = 10
        self.score = 0
        self.reward = 0
        self.hits = 0
        self.done = False

        # Set the background color and set it to be transparent
        self.image = pygame.Surface([self.w, self.h])
        self.image.fill(0)                    # 0 is Black
        self.image.set_colorkey(0)            # make Black color transparent

        pygame.draw.rect(self.image, color, [0, 0, self.w, self.h])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    def collided(self, other):
        self.reward += 1
        self.hits += 1
        other.bounce()
    
    def reset(self, x, y):
        self.score = 0
        self.reward = 0
        self.hits = 0
        self.done = False
        self.rect.center = (x, y)

    def move(self, y):
        self.rect.x += y
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > HEIGHT-self.w:
            self.rect.x = HEIGHT-self.w

class Pong(gym.Env):
    FPS = 30
    colors = {'BLACK': (0, 0, 0),
        'WHITE': (255, 255, 255),
        'GREY': (150, 150, 150) }
    
    def __init__(self, w = WIDTH, h = HEIGHT):
        super(Pong, self).__init__()
        self.observation_space = gym.spaces.Box(low = -8, high = 500, shape = (5,), dtype=np.int32)
        self.action_space = gym.spaces.Discrete(2) # 2 actions... left,right
        self.w = w
        self.h = h
        pygame.init()
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("RL PONG")
        self.clock = pygame.time.Clock()

        xmargin = 20
        self.paddle = Paddle(self.colors['WHITE'], w/2, h - xmargin)
        self.ball = Ball(self.colors['WHITE'], w/2, h/2)

        # list of all the sprites in the game.
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.paddle)
        self.all_sprites.add(self.ball)

    def reset(self):
        xmargin = 20
        self.paddle.reset(self.w/2 + 100, self.h - xmargin)
        self.ball.reset(self.w/2, self.h/2)

        #Return the initial positions
        observation = np.array((self.paddle.rect.centerx, self.ball.rect.centerx, self.ball.rect.centery,
                                  self.ball.velocity[0], self.ball.velocity[1]))
        return observation

    def render(self):
        #Display routine
        self.screen.fill(self.colors['GREY'])
        self.all_sprites.draw(self.screen)

        #Display scores:
        font = pygame.font.Font(None, 74)
        text = font.render(str(self.paddle.score), 1, self.colors['WHITE'])
        self.screen.blit(text, (self.w/2-10,10))
        pygame.display.flip()
        self.clock.tick(self.FPS)

    def step(self, action):
        self.all_sprites.update()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # Moving the paddles according to action given... -1, or 1
        speed = 8
        map_list = [-1, 1]
        self.paddle.move((map_list[action]) * speed)            # map from 0,1 to -1,1

        # Check if the ball is bouncing against any of the 4 walls:
        if self.ball.rect.x > self.w-self.ball.r*2:
            self.ball.velocity[0] = -self.ball.velocity[0]
        if self.ball.rect.x < 0:
            self.ball.velocity[0] = -self.ball.velocity[0]
        if self.ball.rect.y > self.h-self.ball.r*2:
            self.paddle.done = True #<=== GAME OVER!!!
        if self.ball.rect.y < 0:
            self.ball.velocity[1] = -self.ball.velocity[1]

        # Detect collisions between the ball and the paddles
        if pygame.sprite.collide_rect(self.ball, self.paddle) and self.ball.velocity[1]>0 :
            self.paddle.collided(self.ball)
            self.paddle.score +=1
            
        # If limit reached then done...
        lim = 1000
        if self.paddle.reward >= lim: 
            self.paddle.done = True

        # return observations
        observation = np.array((self.paddle.rect.centerx, self.ball.rect.centerx, self.ball.rect.centery,
                                  self.ball.velocity[0], self.ball.velocity[1]))

        reward = self.paddle.reward
        done = self.paddle.done
        info = {}
        return observation, reward, done, info
    
   
def test():
    action_list = [-1, 1]
    env = Pong()
    observation = env.reset()
    done = False
    while not done:  	
        observation, reward, done = env.step((random.choice(action_list)))
        env.render()

if __name__ == '__main__':    
    # test()
    pass
import pygame
import os

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.max_life = 100
        self.life = self.max_life
        self.alive = True

        base_path = "assets/inimigo"
        self.image = pygame.image.load(os.path.join(base_path, "demon.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 45))
        self.rect = self.image.get_rect(topleft=pos)

    def take_damage(self, amount):
        self.life -= amount
        if self.life <= 0:
            self.life = 0
            self.alive = False

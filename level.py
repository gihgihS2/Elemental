import pygame
from player import Player

class Level:
    def __init__(self, surface):
        self.display_surface = surface

        # Carregar o mapa
        self.background = pygame.image.load('assets/DESERTO/MAPAOK.png').convert()
        self.background = pygame.transform.scale(self.background, (800, 600))

        # Grupo de sprites
        self.all_sprites = pygame.sprite.Group()

        # Adicionar o jogador
        self.player = Player((750, 550))  # posição inicial
        self.all_sprites.add(self.player)

    def run(self, dt):
        # Desenhar o mapa de fundo
        self.display_surface.blit(self.background, (0, 0))

        # Atualizar e desenhar sprites
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.display_surface)

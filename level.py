import pygame

class Level:
    def __init__(self, surface):
        self.display_surface = surface

        # Carregar o mapa (coloque o caminho correto até o PNG)
        self.background = pygame.image.load('assets/DESERTO/MAPAOK.png').convert()
        self.background = pygame.transform.scale(self.background, (800, 600))  # ajusta ao tamanho da tela

    def run(self, dt):
        # Desenhar o mapa de fundo
        self.display_surface.blit(self.background, (0, 0))

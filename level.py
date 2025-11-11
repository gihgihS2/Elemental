import pygame
from player import Player
from enemy import Enemy


class Level:
    def __init__(self, surface, player_pos=None, inimigo_vivo=True):
        # Superfície de desenho
        self.display_surface = surface
        
        # Estado do inimigo
        self.inimigo_vivo = inimigo_vivo
        
        # Carregar e redimensionar background
        self.background = pygame.image.load('assets/DESERTO/MAPAOK.png').convert()
        self.background = pygame.transform.scale(self.background, (800, 600))
        
        # Grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        # Configuração inicial do jogador
        self.initial_player_pos = (750, 550)
        if player_pos is None:
            player_pos = self.initial_player_pos
        
        self.player = Player(player_pos)
        self.all_sprites.add(self.player)
        
        # Configuração do inimigo
        self.enemy = None
        if inimigo_vivo:
            self.enemy = Enemy((727, 273))
            self.all_sprites.add(self.enemy)
            self.enemies.add(self.enemy)
        
        # Fonte e prompts
        self.font = pygame.font.SysFont(None, 36)
        self.show_prompt = False
        self.combat_requested = False
        self.vitoria = None

    def check_proximity(self):
        """Verifica se o jogador está próximo do inimigo."""
        if self.enemy and self.player.rect.colliderect(self.enemy.rect.inflate(5, 5)):
            self.show_prompt = True
            return
        self.show_prompt = False

    def draw_prompt(self):
        """Desenha o prompt de combate na tela."""
        rect = pygame.Rect(200, 200, 400, 200)
        pygame.draw.rect(self.display_surface, (0, 0, 0), rect)
        pygame.draw.rect(self.display_surface, (255, 255, 255), rect, 4)

        text = self.font.render("Entrar em combate?", True, (255, 255, 255))
        yes_text = self.font.render("[Y] Sim", True, (0, 255, 0))

        self.display_surface.blit(text, (rect.x + 100, rect.y + 40))
        self.display_surface.blit(yes_text, (rect.x + 155, rect.y + 100))

    def handle_prompt_input(self, event):
        """Trata a entrada do jogador no prompt."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                self.combat_requested = True
            elif event.key == pygame.K_n:
                self.show_prompt = False

    def handle_collision(self):
        """Impede que o jogador atravesse o inimigo."""
        if self.enemy and pygame.sprite.collide_rect(self.player, self.enemy):
            dx = self.player.rect.centerx - self.enemy.rect.centerx
            dy = self.player.rect.centery - self.enemy.rect.centery

            if abs(dx) > abs(dy):
                if dx > 0:
                    self.player.rect.left = self.enemy.rect.right
                else:
                    self.player.rect.right = self.enemy.rect.left
            else:
                if dy > 0:
                    self.player.rect.top = self.enemy.rect.bottom
                else:
                    self.player.rect.bottom = self.enemy.rect.top

    def run(self, dt, events):
        """Executa o loop principal da fase."""
        # Desenhar background e sprites
        self.display_surface.blit(self.background, (0, 0))
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.display_surface)

        # Gerenciar colisões e proximidade
        self.handle_collision()
        self.check_proximity()

        # Tratar eventos de input
        for event in events:
            self.handle_prompt_input(event)

        # Desenhar prompt se necessário
        if self.show_prompt:
            self.draw_prompt()

        # Verificar vitória ou derrota
        if self.enemy and self.enemy.life <= 0:
            self.vitoria = True
            self.inimigo_vivo = False
            self.all_sprites.remove(self.enemy)
            self.enemies.remove(self.enemy)
            self.enemy = None
        elif self.player.life <= 0:
            self.vitoria = False
            self.player.rect.topleft = self.initial_player_pos

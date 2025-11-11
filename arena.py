import pygame
import random
import sys
import os

class Arena:
    def __init__(self, surface, player_life=100, inimigo_vivo=True):
        self.display_surface = surface
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)

        # --- Cores ---
        self.BRANCO = (255, 255, 255)
        self.PRETO = (0, 0, 0)
        self.VERMELHO = (255, 0, 0)
        self.VERDE = (0, 255, 0)
        self.AMARELO = (255, 255, 0)
        self.CINZA = (200, 200, 200)

        # --- Fundo ---
        arena_path = os.path.join("assets", "arenas", "arena1.png")
        self.background = pygame.image.load(arena_path).convert()
        self.background = pygame.transform.scale(self.background, (800, 600))

        # --- Sprites ---
        player_path = os.path.join("assets", "player", "combat.png")
        enemy_path = os.path.join("assets", "inimigo", "demon.png")

        self.player_img = pygame.image.load(player_path).convert_alpha()
        self.enemy_img = pygame.image.load(enemy_path).convert_alpha()

        self.player_img = pygame.transform.scale(self.player_img, (70, 90))
        self.enemy_img = pygame.transform.scale(self.enemy_img, (90, 150))

        # --- Estados ---
        self.turn = "player"
        self.action_taken = False
        self.vitoria = None
        self.enemy_alive = inimigo_vivo

        # --- Entidades ---
        self.player = {"x": 250, "y": 380, "life": player_life, "max_life": 100, "name": "Jogador"}
        self.enemy = {"x": 477, "y": 165, "life": 100, "max_life": 100, "name": "Demonizador"} if inimigo_vivo else None

        self.opcoes = ["Agua", "Preda", "Fogasso"]
        self.hud_rects = []

        # Tremor
        self.player_shake_timer = 0
        self.enemy_shake_timer = 0
        self.SHAKE_DURATION = 10
        self.SHAKE_INTENSITY = 5

        # Ataque inimigo
        self.enemy_attack_timer = 0.8

    # --- Barras de vida ---
    def draw_barra_vida(self, x, y, vida, vida_max):
        largura = 200
        altura = 20
        proporcao = max(vida / vida_max, 0)
        pygame.draw.rect(self.display_surface, self.CINZA, (x, y, largura, altura))
        pygame.draw.rect(self.display_surface, self.VERDE, (x, y, largura * proporcao, altura))
        pygame.draw.rect(self.display_surface, self.PRETO, (x, y, largura, altura), 2)

    def attack(self, attacker, attack_type, target):
        damage = {"Agua":10, "Preda":15, "Fogasso":25}.get(attack_type, 0)
        target["life"] -= damage
        target["life"] = max(target["life"], 0)

        if target["name"] == "Jogador":
            self.player_shake_timer = self.SHAKE_DURATION
        else:
            self.enemy_shake_timer = self.SHAKE_DURATION

    # --- Desenho ---
    def draw(self):
        self.display_surface.blit(self.background, (0, 0))

        # --- Tremor ---
        px, py, ex, ey = 0, 0, 0, 0
        if self.player_shake_timer > 0:
            px = random.randint(-self.SHAKE_INTENSITY, self.SHAKE_INTENSITY)
            py = random.randint(-self.SHAKE_INTENSITY, self.SHAKE_INTENSITY)
            self.player_shake_timer -= 1
        if self.enemy_shake_timer > 0:
            ex = random.randint(-self.SHAKE_INTENSITY, self.SHAKE_INTENSITY)
            ey = random.randint(-self.SHAKE_INTENSITY, self.SHAKE_INTENSITY)
            self.enemy_shake_timer -= 1

        # --- Sprites ---
        self.display_surface.blit(self.player_img, (self.player["x"]+px, self.player["y"]+py))
        if self.enemy:
            self.display_surface.blit(self.enemy_img, (self.enemy["x"]+ex, self.enemy["y"]+ey))

        # --- Barras de vida + nomes ---
        # Jogador
        self.draw_barra_vida(50, 30, self.player["life"], self.player["max_life"])
        player_name = self.font.render(self.player["name"], True, self.PRETO)
        self.display_surface.blit(player_name, (50, 10))

        # Inimigo
        if self.enemy:
            self.draw_barra_vida(550, 30, self.enemy["life"], self.enemy["max_life"])
            enemy_name = self.font.render(self.enemy["name"], True, self.PRETO)
            self.display_surface.blit(enemy_name, (550, 10))

        # --- HUD (botões) ---
        self.hud_rects.clear()
        for i, opc in enumerate(self.opcoes):
            rect = pygame.Rect(50 + i*200, 530, 180, 40)
            self.hud_rects.append(rect)
            color = self.AMARELO if self.turn == "player" and self.vitoria is None else (150, 150, 150)
            pygame.draw.rect(self.display_surface, color, rect, border_radius=10)
            text = self.font.render(opc, True, self.PRETO)
            self.display_surface.blit(text, (rect.x + 10, rect.y + 10))

        # --- Mensagem final ---
        if self.vitoria is not None:
            msg = "Você venceu!" if self.vitoria else "Você perdeu!"
            text = self.font.render(msg + " Pressione [Enter] para voltar.", True, self.PRETO)
            self.display_surface.blit(text, (200, 250))

        pygame.display.update()

    # --- Loop principal ---
    def run(self, events):
        dt = self.clock.tick(60)/1000
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if self.vitoria is not None and keys[pygame.K_RETURN]:
            self.enemy_alive = self.enemy and self.enemy["life"] > 0
            return "return"

        # Clique HUD
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and self.turn=="player" and self.vitoria is None:
                mx,my = pygame.mouse.get_pos()
                for i, rect in enumerate(self.hud_rects):
                    if rect.collidepoint(mx,my) and not self.action_taken:
                        self.attack(self.player, self.opcoes[i], self.enemy)
                        self.action_taken=True
                        self.turn="enemy"
                        self.enemy_attack_timer=0.8

        # Ataque inimigo
        if self.enemy and self.turn=="enemy" and self.vitoria is None:
            self.enemy_attack_timer -= dt
            if self.enemy_attack_timer<=0:
                escolha=random.choice(self.opcoes)
                self.attack(self.enemy, escolha, self.player)
                self.turn="player"
                self.action_taken=False

        # Fim
        if self.enemy and self.enemy["life"]<=0:
            self.vitoria=True
        elif self.player["life"]<=0:
            self.vitoria=False

        self.draw()
        return None

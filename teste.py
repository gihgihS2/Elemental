import pygame
import sys
import random

pygame.init()

# --- CONFIGURAÇÕES BÁSICAS ---
WIDTH, HEIGHT = 800, 600
tela = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elemental - Exploração e Batalha")

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARELO = (255, 255, 0)
CINZA = (200, 200, 200)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Player
player_size = 50
player_vel = 5
player_life = 100
player_max_life = 100

# NPC
enemy_size = 50
enemy_life = 100
enemy_max_life = 100
enemy_x = 500
enemy_y = 300

# HUD de ataques
opcoes = ["Soco", "Chute", "Ataque Especial"]
hud_rects = []

# Estados
mode = "livre"  # "livre" ou "battle"
turn = "player"
action_taken = False
jumping = False
jump_height = 0
MAX_JUMP = 50

# Posições
player_x = 100
player_y = HEIGHT//2 - player_size//2
npc_x = WIDTH - 200
npc_y = HEIGHT//2 - enemy_size//2

font = pygame.font.SysFont(None, 30)

# --- Funções ---
def draw_barra_vida(x, y, vida, vida_max):
    largura = 200
    altura = 20
    proporcao = max(vida / vida_max, 0)
    pygame.draw.rect(tela, CINZA, (x, y, largura, altura))
    pygame.draw.rect(tela, VERDE, (x, y, largura * proporcao, altura))
    pygame.draw.rect(tela, PRETO, (x, y, largura, altura), 2)

def attack(attacker, attack_type, target):
    damage = 0
    if attack_type == "Soco":
        damage = 10
    elif attack_type == "Chute":
        damage = 15
    elif attack_type == "Ataque Especial":
        damage = 25
    target["life"] -= damage
    target["life"] = max(target["life"], 0)
    print(f"{attacker['name']} usou {attack_type}! {target['name']} perdeu {damage} de vida")

def draw_livre():
    tela.fill((100, 180, 255))  # fundo azul claro
    pygame.draw.rect(tela, (80, 200, 80), (0, HEIGHT-100, WIDTH, 100))  # chão
    pygame.draw.rect(tela, AZUL, (player["x"], player["y"], player_size, player_size))
    pygame.draw.rect(tela, VERMELHO, (enemy_x, enemy_y, enemy_size, enemy_size))
    text = font.render("Modo Livre - Ande até o inimigo para iniciar batalha", True, PRETO)
    tela.blit(text, (50, 30))
    pygame.display.update()

def draw_battle():
    tela.fill(BRANCO)
    pygame.draw.rect(tela, AZUL, (player["x"], player["y"], player_size, player_size))
    pygame.draw.rect(tela, VERMELHO, (npc["x"], npc["y"], enemy_size, enemy_size))
    
    draw_barra_vida(50, 30, player["life"], player_max_life)
    draw_barra_vida(WIDTH - 250, 30, npc["life"], enemy_max_life)
    
    hud_rects.clear()
    if turn == "player":
        for i, opc in enumerate(opcoes):
            rect = pygame.Rect(50, HEIGHT-150 + i*50, 180, 40)
            hud_rects.append(rect)
            pygame.draw.rect(tela, AMARELO, rect, border_radius=10)
            text = font.render(opc, True, PRETO)
            tela.blit(text, (rect.x+10, rect.y+10))
    
    pygame.display.update()

# --- Objetos ---
player = {"x": player_x, "y": player_y, "life": player_life, "name": "Jogador"}
npc = {"x": npc_x, "y": npc_y, "life": enemy_life, "name": "Inimigo"}

# --- LOOP PRINCIPAL ---
running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Clique de ataque (só no modo batalha)
        if mode == "battle" and turn == "player" and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for i, rect in enumerate(hud_rects):
                if rect.collidepoint(mx, my) and not action_taken:
                    attack(player, opcoes[i], npc)
                    action_taken = True
                    pygame.time.delay(700)
                    turn = "npc"
                    action_taken = False  # <- reset para o NPC agir

    keys = pygame.key.get_pressed()

    # --- MODO LIVRE ---
    if mode == "livre":
        if keys[pygame.K_LEFT] and player["x"] > 0:
            player["x"] -= player_vel
        if keys[pygame.K_RIGHT] and player["x"] + player_size < WIDTH:
            player["x"] += player_vel
        if keys[pygame.K_UP] and player["y"] > 0:
            player["y"] -= player_vel
        if keys[pygame.K_DOWN] and player["y"] + player_size < HEIGHT - 100:
            player["y"] += player_vel
        
        # Verifica colisão com inimigo
        player_rect = pygame.Rect(player["x"], player["y"], player_size, player_size)
        enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_size, enemy_size)
        if player_rect.colliderect(enemy_rect):
            print("Entrando em modo batalha!")
            mode = "battle"
            player["x"] = 150
            player["y"] = HEIGHT//2 - player_size//2
            npc["x"] = WIDTH - 200
            npc["y"] = HEIGHT//2 - enemy_size//2

    # --- MODO BATALHA ---
    elif mode == "battle":
        if turn == "player":
            if keys[pygame.K_LEFT] and player["x"] - player_vel > 50:
                player["x"] -= player_vel
            if keys[pygame.K_RIGHT] and player["x"] + player_vel + player_size < WIDTH-400:
                player["x"] += player_vel
            if keys[pygame.K_UP] and not jumping:
                jumping = True
        
        # Atualiza pulo
        if jumping:
            if jump_height < MAX_JUMP:
                player["y"] -= 5
                jump_height += 5
            else:
                jumping = False
        elif jump_height > 0:
            player["y"] += 5
            jump_height -= 5

        # Turno do NPC
        if turn == "npc" and not action_taken:
            pygame.time.delay(700)
            if jump_height == 0:
                escolha = random.choice(opcoes)
                attack(npc, escolha, player)
            else:
                print("Jogador desviou!")
            action_taken = True
            pygame.time.delay(700)
            turn = "player"
            action_taken = False  # <- reset para o jogador agir novamente

        # Atualiza vidas
        player["life"] = max(player["life"], 0)
        npc["life"] = max(npc["life"], 0)

        # Vitória / Derrota
        if npc["life"] <= 0:
            print("Você venceu a batalha!")
            mode = "livre"
            npc["life"] = enemy_max_life
            player["x"], player["y"] = 100, 300

        if player["life"] <= 0:
            print("Você perdeu a batalha!")
            mode = "livre"
            player["life"] = player_max_life
            player["x"], player["y"] = 100, 300

    # --- DESENHO ---
    if mode == "livre":
        draw_livre()
    elif mode == "battle":
        draw_battle()

pygame.quit()
sys.exit()

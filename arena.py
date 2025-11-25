import pygame
import random
import sys
import os

class Arena:
    def __init__(self, surface, player_life=100, inimigo_vivo=True):
        self.display_surface = surface
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.font_big = pygame.font.SysFont(None, 36)

        # --- Cores ---
        self.BRANCO = (255, 255, 255)
        self.PRETO = (0, 0, 0)
        self.VERMELHO = (255, 0, 0)
        self.VERDE = (0, 255, 0)
        self.AMARELO = (255, 255, 0)
        self.CINZA = (200, 200, 200)
        self.CINZA_CLARO = (220, 220, 220)

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

        # --- Música e sons ---
        pygame.mixer.init()

        # Música de batalha
        music_path = os.path.join("assets", "sons", "Eleuxelier_bat.mp3")
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.05)
        pygame.mixer.music.play(-1)  # loop infinito

        # Efeitos
        self.som_erro = pygame.mixer.Sound(os.path.join("assets", "sons", "erro.mp3"))
        self.som_agua = pygame.mixer.Sound(os.path.join("assets", "sons", "som_agua.mp3"))
        self.som_fogo = pygame.mixer.Sound(os.path.join("assets", "sons", "som_fogo.mp3"))
        self.som_preda = pygame.mixer.Sound(os.path.join("assets", "sons", "som_preda.mp3"))

        self.som_erro.set_volume(0.04)
        self.som_agua.set_volume(0.04)
        self.som_fogo.set_volume(0.04)
        self.som_preda.set_volume(0.04)

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

        self.enemy_attack_timer = 0.8

        # CHANCES
        self.chance_erro_player = 0.15
        self.chance_erro_enemy = 0.15

        self.chance_critico_player = 0.15
        self.chance_critico_enemy = 0.10
        self.multiplicador_critico = 1.8

        self.mensagem = ""
        self.mensagem_timer = 0

        self.floating_texts = []

        # ANIMAÇÕES
        self.spell_frames = {
            "Agua": self.load_spell_frames(os.path.join("assets", "poderes", "poder_agua")),
            "Fogasso": self.load_spell_frames(os.path.join("assets", "poderes", "poder_fogo")),
            "Preda": self.load_spell_frames(os.path.join("assets", "poderes", "poder_preda")),
        }
        #posição dos poderzinhos
        self.anim_positions = {
            "player": (self.player["x"] + 270, self.player["y"] - 160),
            "enemy": (self.enemy["x"] - 190, self.enemy["y"] + 260)
        }

        self.current_anim = None
        # tempo por frame
        self.anim_frame_time = 0.03

    def load_spell_frames(self, folder):
        frames = []
        try:
            if not os.path.isdir(folder): return frames
            files = sorted([f for f in os.listdir(folder) if f.lower().endswith('.png')])
            for fname in files:
                path = os.path.join(folder, fname)
                img = pygame.image.load(path).convert_alpha()
                # escala padrão
                img = pygame.transform.scale(img, (160, 160))
                frames.append(img)
        except Exception as e:
            print("Erro ao carregar frames:", e)
        return frames

    # BARRA DE VIDA
    def draw_barra_vida(self, x, y, vida, vida_max):
        largura = 200
        altura = 20
        proporcao = max(vida / vida_max, 0)
        pygame.draw.rect(self.display_surface, self.CINZA, (x, y, largura, altura))
        pygame.draw.rect(self.display_surface, self.VERDE, (x, y, largura * proporcao, altura))
        pygame.draw.rect(self.display_surface, self.PRETO, (x, y, largura, altura), 2)

    # LÓGICA DO DANO
    def perform_attack(self, attacker, attack_type, target):
        if attacker["name"] == "Jogador":
            chance_erro = self.chance_erro_player
            chance_crit = self.chance_critico_player
        else:
            chance_erro = self.chance_erro_enemy
            chance_crit = self.chance_critico_enemy

        # ERRO AQUI É DESCONSIDERADO (erros reais agora só ocorrem antes da animação)
        # mas vamos manter caso seja usado por fallback
        if random.random() < chance_erro:
            self.mensagem = f"{attacker['name']} errou o ataque!"
            self.mensagem_timer = 1.2
            self.som_erro.play()
            return False

        base_damage = {"Agua": 10, "Preda": 15, "Fogasso": 25}.get(attack_type, 0)
        critico = random.random() < chance_crit
        damage = int(base_damage * self.multiplicador_critico) if critico else base_damage

        if target:
            target["life"] = max(target["life"] - damage, 0)

        if target["name"] == "Jogador":
            self.player_shake_timer = self.SHAKE_DURATION
        else:
            self.enemy_shake_timer = self.SHAKE_DURATION

        if critico:
            self.mensagem = f"🔥 CRÍTICO! {attacker['name']} usou {attack_type} causando {damage}!"
        else:
            self.mensagem = f"{attacker['name']} usou {attack_type}! Causou {damage}!"

        self.mensagem_timer = 2

        
        tx = target["x"] + 20
        ty = target["y"] - 10
        text_str = f"CRÍTICO! -{damage}" if critico else f"-{damage}"
        color = self.AMARELO if critico else self.VERMELHO

        self.floating_texts.append({
            "text": text_str,
            "x": tx, "y": ty,
            "timer": 1.2,
            "color": color,
            "vy": -0.9
        })

        return True

    # ATAQUE + ANIMAÇÃO
    def attack(self, attacker, attack_type, target):

        # --- ERRO ANTES DA ANIMAÇÃO ---
        if attacker["name"] == "Jogador":
            chance_erro = self.chance_erro_player
        else:
            chance_erro = self.chance_erro_enemy

        if random.random() < chance_erro:
            self.mensagem = f"{attacker['name']} errou o ataque!"
            self.mensagem_timer = 1.2
            self.som_erro.play()

            tx = target["x"] + 20
            ty = target["y"] - 10

            self.floating_texts.append({
                "text": "ERROU!",
                "x": tx, "y": ty,
                "timer": 1.2,
                "color": self.CINZA_CLARO,
                "vy": -0.8
            })

            if attacker["name"] == "Jogador":
                self.turn = "enemy"
                self.action_taken = True
                self.enemy_attack_timer = 0.8
            else:
                self.turn = "player"
                self.action_taken = False
                self.enemy_attack_timer = 0.8

            return

        # SOM DO ATAQUE
        if attack_type == "Agua":
            self.som_agua.play()
        elif attack_type == "Fogasso":
            self.som_fogo.play()
        elif attack_type == "Preda":
            self.som_preda.play()

        # ANIMAÇÃO
        frames = self.spell_frames.get(attack_type, [])
        if not frames:
            self.perform_attack(attacker, attack_type, target)
            return

        who = "player" if attacker["name"] == "Jogador" else "enemy"
        pos = self.anim_positions.get(who, (400, 300))

        self.current_anim = {
            "frames": frames,
            "index": 0,
            "time": 0.0,
            "frame_time": self.anim_frame_time,
            "pos": pos,
            "attacker": attacker,
            "target": target,
            "attack_type": attack_type
        }

        self.action_taken = True

    # DESENHO
    def draw(self):
        self.display_surface.blit(self.background, (0, 0))

        # Tremor
        px = py = ex = ey = 0
        if self.player_shake_timer > 0:
            px = random.randint(-5, 5)
            py = random.randint(-5, 5)
            self.player_shake_timer -= 1

        if self.enemy_shake_timer > 0:
            ex = random.randint(-5, 5)
            ey = random.randint(-5, 5)
            self.enemy_shake_timer -= 1

        self.display_surface.blit(self.player_img, (self.player["x"] + px, self.player["y"] + py))
        if self.enemy:
            self.display_surface.blit(self.enemy_img, (self.enemy["x"] + ex, self.enemy["y"] + ey))

        # Barras
        self.draw_barra_vida(50, 30, self.player["life"], self.player["max_life"])
        self.display_surface.blit(self.font.render(self.player["name"], True, self.VERDE), (50, 10))

        if self.enemy:
            self.draw_barra_vida(550, 30, self.enemy["life"], self.enemy["max_life"])
            self.display_surface.blit(self.font.render(self.enemy["name"], True, self.VERMELHO), (550, 10))

        # HUD
        self.hud_rects.clear()
        for i, opc in enumerate(self.opcoes):
            rect = pygame.Rect(50 + i * 200, 530, 180, 40)
            self.hud_rects.append(rect)
            color = self.AMARELO if self.turn == "player" else (150, 150, 150)
            pygame.draw.rect(self.display_surface, color, rect, border_radius=10)
            self.display_surface.blit(self.font.render(opc, True, self.PRETO), (rect.x + 10, rect.y + 10))

        # ANIMAÇÃO ATUAL
        if self.current_anim:
            anim = self.current_anim
            idx = int(anim["index"])
            if 0 <= idx < len(anim["frames"]):
                surf = anim["frames"][idx]
                ax = anim["pos"][0] - surf.get_width() // 2
                ay = anim["pos"][1] - surf.get_height() // 2
                self.display_surface.blit(surf, (ax, ay))

        # texto
        remove = []
        for i, ft in enumerate(self.floating_texts):
            ft["y"] += ft["vy"]
            ft["timer"] -= 1/60

            surf = self.font_big.render(ft["text"], True, ft["color"]) if "CRÍTICO" in ft["text"] else self.font.render(ft["text"], True, ft["color"])
            shadow = self.font.render(ft["text"], True, self.PRETO)

            self.display_surface.blit(shadow, (int(ft["x"]) + 1, int(ft["y"]) + 1))
            self.display_surface.blit(surf, (int(ft["x"]), int(ft["y"])))

            if ft["timer"] <= 0:
                remove.append(i)

        for j in reversed(remove):
            self.floating_texts.pop(j)

        # Mensagem de combate
        if self.mensagem_timer > 0:
            self.mensagem_timer -= 1/60
            rect_bg = pygame.Rect(160, 470, 480, 40)
            pygame.draw.rect(self.display_surface, (0, 0, 0), rect_bg)
            pygame.draw.rect(self.display_surface, self.CINZA, rect_bg, 2)
            self.display_surface.blit(self.font.render(self.mensagem, True, self.BRANCO), (rect_bg.x + 10, rect_bg.y + 6))

        # Tela final 
        if self.vitoria is not None:
            pygame.mixer.music.stop() # PARA A MUSICA 
            msg = "Você venceu!" if self.vitoria else "Você perdeu!"
            self.display_surface.blit(self.font.render(msg + " Pressione [Enter] para voltar.", True, self.BRANCO), (200, 250))

        pygame.display.update()

    def run(self, events):
        dt = self.clock.tick(60) / 1000
        self.last_dt = dt

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if self.vitoria is not None and keys[pygame.K_RETURN]:
            return "return"

        # Clique HUD
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.turn == "player" and self.vitoria is None:
                mx, my = pygame.mouse.get_pos()
                for i, rect in enumerate(self.hud_rects):
                    if rect.collidepoint(mx, my) and not self.action_taken:
                        self.attack(self.player, self.opcoes[i], self.enemy)
                        break

        # Ataque inimigo
        if self.enemy and self.turn == "enemy" and self.vitoria is None and self.mensagem_timer <= 0:
            if self.current_anim is None:
                self.enemy_attack_timer -= dt
                if self.enemy_attack_timer <= 0:
                    escolha = random.choice(self.opcoes)
                    self.attack(self.enemy, escolha, self.player)

        # Atualiza animação
        if self.current_anim:
            anim = self.current_anim
            anim["time"] += dt
            while anim["time"] >= anim["frame_time"]:
                anim["time"] -= anim["frame_time"]
                anim["index"] += 1
            if int(anim["index"]) >= len(anim["frames"]):
                attacker = anim["attacker"]
                attack_type = anim["attack_type"]
                target = anim["target"]

                self.perform_attack(attacker, attack_type, target)
                self.current_anim = None

                if attacker["name"] == "Jogador":
                    self.turn = "enemy"
                    self.enemy_attack_timer = 0.8
                    self.action_taken = True
                else:
                    self.turn = "player"
                    self.action_taken = False
                    self.enemy_attack_timer = 0.8

        # Fim do combate
        if self.enemy and self.enemy["life"] <= 0:
            self.vitoria = True
            self.enemy_alive = False
        elif self.player["life"] <= 0:
            self.vitoria = False

        self.draw()
        return None

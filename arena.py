# Arena (arquivo atualizado com sistema de animação posicionável)
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

        # --- CHANCES DE ERRO ---
        self.chance_erro_player = 0.15
        self.chance_erro_enemy = 0.15

        # --- CRÍTICO ---
        self.chance_critico_player = 0.15     # 15%
        self.chance_critico_enemy = 0.10      # 10%
        self.multiplicador_critico = 1.8      # 80% mais dano

        # --- Mensagens ---
        self.mensagem = ""
        self.mensagem_timer = 0

        # --- Floating texts (dano / erro / crítico) ---
        # cada item: {"text": str, "x": float, "y": float, "timer": float, "color": (r,g,b), "vy": float}
        self.floating_texts = []

        # ----------------------
        # SISTEMA DE ANIMAÇÃO
        # ----------------------
        # Carrega frames das pastas (se existirem)
        self.spell_frames = {
            "Agua": self.load_spell_frames(os.path.join("assets", "poderes", "poder_agua")),
            "Fogasso": self.load_spell_frames(os.path.join("assets", "poderes", "poder_fogo")),
            "Preda": self.load_spell_frames(os.path.join("assets", "poderes", "poder_preda")),
        }

        # Posições configuráveis (mude esses valores para posicionar manualmente)
        # Use chaves "player" e "enemy" como referência; você pode colocar coordenadas diferentes por poder se quiser.
        self.anim_positions = {
            "player": (self.player["x"] + 270, self.player["y"] - 160),
            "enemy": (self.enemy["x"] - 190, self.enemy["y"] + 260)
        }

        # Estado da animação atual (toca uma por vez)
        self.current_anim = None
        # tempo por frame (padrão, pode ajustar por spell se quiser)
        self.anim_frame_time = 0.03

    def load_spell_frames(self, folder):
        """Carrega todos os pngs da pasta ordenados e retorna lista de surfaces."""
        frames = []
        try:
            if not os.path.isdir(folder):
                return frames
            files = [f for f in os.listdir(folder) if f.lower().endswith('.png')]
            files.sort()
            for fname in files:
                path = os.path.join(folder, fname)
                img = pygame.image.load(path).convert_alpha()
                # escala padrão (ajuste se necessário)
                img = pygame.transform.scale(img, (160, 160))
                frames.append(img)
        except Exception as e:
            print('Erro carregando frames em', folder, e)
        return frames

    # --- Barras de vida ---
    def draw_barra_vida(self, x, y, vida, vida_max):
        largura = 200
        altura = 20
        proporcao = max(vida / vida_max, 0)
        pygame.draw.rect(self.display_surface, self.CINZA, (x, y, largura, altura))
        pygame.draw.rect(self.display_surface, self.VERDE, (x, y, largura * proporcao, altura))
        pygame.draw.rect(self.display_surface, self.PRETO, (x, y, largura, altura), 2)

    # ---- lógica do ataque (aplica dano / crítico / erro / floating text) ----
    def perform_attack(self, attacker, attack_type, target):
        """Aplica o resultado do ataque — mesma lógica antiga."""
        # ----- CHANCE DE ERRO / CRÍTICO -----
        if attacker["name"] == "Jogador":
            chance_erro = self.chance_erro_player
            chance_crit = self.chance_critico_player
        else:
            chance_erro = self.chance_erro_enemy
            chance_crit = self.chance_critico_enemy

        # Errou
        if random.random() < chance_erro:
            self.mensagem = f"{attacker['name']} errou o ataque!"
            self.mensagem_timer = 1.2


            tx = (target["x"] + (target.get("max_life", 0) and 0)) if target else attacker["x"]
            ty = (target["y"] - 10) if target else attacker["y"] - 10

            if target is None:
                tx = attacker["x"]
                ty = attacker["y"] - 10

            self.floating_texts.append({
                "text": "ERROU!",
                "x": tx,
                "y": ty,
                "timer": 1.2,
                "color": self.CINZA_CLARO,
                "vy": -0.8
            })
            return False  # ataque sem dano

        # ----- DANO BASE -----
        base_damage = {"Agua": 10, "Preda": 15, "Fogasso": 25}.get(attack_type, 0)

        # ----- CRÍTICO -----
        critico = False
        if random.random() < chance_crit:
            critico = True
            damage = int(base_damage * self.multiplicador_critico)
        else:
            damage = base_damage

        # Aplica dano
        if target:
            target["life"] -= damage
            target["life"] = max(target["life"], 0)

        # Tremor
        if target and target["name"] == "Jogador":
            self.player_shake_timer = self.SHAKE_DURATION
        elif target:
            self.enemy_shake_timer = self.SHAKE_DURATION

        # Mensagem principal (barra inferior)
        if critico:
            self.mensagem = f"🔥 CRÍTICO! {attacker['name']} usou {attack_type} causando {damage}!"
        else:
            self.mensagem = f"{attacker['name']} usou {attack_type}! Causou {damage}!"

        self.mensagem_timer = 2

        # --- Floating text: mostrará dano (ou texto de crítico + dano) sobre o alvo ---
        if target:
            tx = target["x"] + 20
            ty = target["y"] - 10
        else:
            tx = attacker["x"]
            ty = attacker["y"] - 10

        if critico:
            text_str = f"CRÍTICO! -{damage}"
            color = self.AMARELO
        else:
            text_str = f"-{damage}"
            color = self.VERMELHO

        self.floating_texts.append({
            "text": text_str,
            "x": tx,
            "y": ty,
            "timer": 1.2,
            "color": color,
            "vy": -0.9
        })

        return True  # ataque com dano aplicado

    # --- Inicia animação de ataque (aplica dano somente quando terminar) ---
    def attack(self, attacker, attack_type, target):
        # inicia animação ao invés de aplicar dano imediatamente
        frames = self.spell_frames.get(attack_type, [])
        if not frames:
            # se não tiver frames, aplica ataque direto
            self.perform_attack(attacker, attack_type, target)
            return

        # decide posição baseada em quem atacou (pode ser personalizada em self.anim_positions)
        who = "player" if attacker["name"] == "Jogador" else "enemy"
        pos = self.anim_positions.get(who, (400, 300))

        # cria animação atual
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
        # bloqueia ação até animação terminar
        self.action_taken = True

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
        player_name = self.font.render(self.player["name"], True, self.VERDE)
        self.display_surface.blit(player_name, (50, 10))

        # Inimigo
        if self.enemy:
            self.draw_barra_vida(550, 30, self.enemy["life"], self.enemy["max_life"])
            enemy_name = self.font.render(self.enemy["name"], True, self.VERMELHO)
            self.display_surface.blit(enemy_name, (550, 10))

        # --- HUD ---
        self.hud_rects.clear()
        for i, opc in enumerate(self.opcoes):
            rect = pygame.Rect(50 + i*200, 530, 180, 40)
            self.hud_rects.append(rect)
            color = self.AMARELO if self.turn == "player" and self.vitoria is None else (150, 150, 150)
            pygame.draw.rect(self.display_surface, color, rect, border_radius=10)
            text = self.font.render(opc, True, self.PRETO)
            self.display_surface.blit(text, (rect.x + 10, rect.y + 10))

        # --- Desenhar animação atual (se houver) ---
        if self.current_anim:
            anim = self.current_anim
            idx = int(anim["index"])
            frames = anim["frames"]
            if 0 <= idx < len(frames):
                surf = frames[idx]
                # ajustar posição centralizando a animação
                ax = anim["pos"][0] - surf.get_width()//2
                ay = anim["pos"][1] - surf.get_height()//2
                self.display_surface.blit(surf, (ax, ay))

        # --- Floating texts (atualiza e desenha) ---
        # Usamos decrementos por frame assumindo ~60 FPS (mesma lógica da mensagem_timer)
        remove_idxs = []
        for i, ft in enumerate(self.floating_texts):
            # mover para cima
            ft["y"] += ft["vy"]
            ft["timer"] -= 1/60

            # escolha de fonte: maior para crítico
            if "CRÍTICO" in ft["text"] or "CRÍTICO" in ft["text"].upper() or "CRÍTICO" in ft["text"]:
                surf = self.font_big.render(ft["text"], True, ft["color"])
            else:
                surf = self.font.render(ft["text"], True, ft["color"])

            # desenha com sombra (melhora legibilidade)
            shadow = self.font.render(ft["text"], True, self.PRETO)
            sx = int(ft["x"]) + 1
            sy = int(ft["y"]) + 1
            self.display_surface.blit(shadow, (sx, sy))
            self.display_surface.blit(surf, (int(ft["x"]), int(ft["y"])))

            if ft["timer"] <= 0:
                remove_idxs.append(i)

        # remove expirados (do fim para o início)
        for j in reversed(remove_idxs):
            self.floating_texts.pop(j)

        # --- Mensagens de Combate (linha inferior) ---
        if self.mensagem_timer > 0:
            self.mensagem_timer -= 1/60
            msg_text = self.font.render(self.mensagem, True, self.BRANCO)
            # desenha um fundo semitransparente simples (retângulo) para melhorar leitura
            rect_bg = pygame.Rect(160, 470, 480, 40)
            pygame.draw.rect(self.display_surface, (0,0,0), rect_bg)
            pygame.draw.rect(self.display_surface, self.CINZA, rect_bg, 2)
            self.display_surface.blit(msg_text, (rect_bg.x + 10, rect_bg.y + 6))

        # --- Mensagem final ---
        if self.vitoria is not None:
            msg = "Você venceu!" if self.vitoria else "Você perdeu!"
            text = self.font.render(msg + " Pressione [Enter] para voltar.", True, self.BRANCO)
            self.display_surface.blit(text, (200, 250))

        pygame.display.update()

    # --- Loop principal ---
    def run(self, events):
        dt = self.clock.tick(60)/1000
        self.last_dt = dt
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
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.turn=="player" and self.vitoria is None:
                mx,my = pygame.mouse.get_pos()
                for i, rect in enumerate(self.hud_rects):
                    if rect.collidepoint(mx,my) and not self.action_taken:
                        self.attack(self.player, self.opcoes[i], self.enemy)
                        # action_taken setado dentro da attack
                        break

        # Ataque inimigo
        if self.enemy and self.turn=="enemy" and self.vitoria is None and self.mensagem_timer <= 0:
            # se animação em curso, não decrementar
            if self.current_anim is None:
                self.enemy_attack_timer -= dt
                if self.enemy_attack_timer<=0:
                    escolha=random.choice(self.opcoes)
                    self.attack(self.enemy, escolha, self.player)

        # Atualiza animação atual (se houver) e aplica ataque ao final
        if self.current_anim:
            anim = self.current_anim
            anim["time"] += self.last_dt
            # avança index conforme frame_time
            while anim["time"] >= anim["frame_time"]:
                anim["time"] -= anim["frame_time"]
                anim["index"] += 1
            # quando terminar a animação (index >= len) -> aplicar ataque
            if int(anim["index"]) >= len(anim["frames"]):
                attacker = anim["attacker"]
                attack_type = anim["attack_type"]
                target = anim["target"]
                # aplica lógica (dano/erro/critico/floating)
                self.perform_attack(attacker, attack_type, target)
                # animação finalizada, limpa
                self.current_anim = None
                # ajustar turnos/flags
                if attacker["name"] == "Jogador":
                    # após jogador atacar -> vez do inimigo
                    self.turn = "enemy"
                    self.enemy_attack_timer = 0.8
                    self.action_taken = True
                else:
                    # após inimigo atacar -> volta para jogador
                    self.turn = "player"
                    self.action_taken = False
                    self.enemy_attack_timer = 0.8

        # Fim
        if self.enemy and self.enemy["life"]<=0:
            self.vitoria=True
        elif self.player["life"]<=0:
            self.vitoria=False

        self.draw()
        return None

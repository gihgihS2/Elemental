import pygame
import sys
from level import Level
from arena import Arena
import os

class Game:
    inimigo_vivo = True

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('ELEMENTAL')
        self.clock = pygame.time.Clock()

        # Estados: 'main_menu', 'exploration', 'arena'
        self.state = "main_menu"
        self.level = None
        self.arena = None

        # --- Carregar assets do menu inicial ---
        menu_base = os.path.join("assets", "menu")

        self.menu_bg = pygame.image.load(os.path.join(menu_base, "fundo_da_tela.jpg")).convert()
        self.menu_bg = pygame.transform.scale(self.menu_bg, (800, 600))

        self.btn_comecar_img = pygame.image.load(os.path.join(menu_base, "comecar.png")).convert_alpha()
        self.btn_sair_img = pygame.image.load(os.path.join(menu_base, "sair_do_jogo.png")).convert_alpha()

        # Posições dos botões
        self.btn_comecar_rect = self.btn_comecar_img.get_rect(center=(300, 300))
        self.btn_sair_rect = self.btn_sair_img.get_rect(center=(500, 300))

        self.font = pygame.font.SysFont(None, 28)

        # 🔊 --- INICIAR MÚSICA DO MENU ---
        pygame.mixer.music.load(os.path.join("assets", "sons", "menu.mp3"))
        pygame.mixer.music.play(-1)   # -1 = loop infinito
        pygame.mixer.music.set_volume(0.03)


    def start_new_game(self):
        pygame.mixer.music.stop()

        self.level = Level(self.screen, inimigo_vivo=Game.inimigo_vivo)
        self.state = "exploration"
        self.arena = None


    def open_arena_from_level(self):
        self.arena = Arena(
            self.screen,
            player_life=self.level.player.life,
            inimigo_vivo=Game.inimigo_vivo
        )
        self.state = "arena"


    def draw_main_menu(self):
        self.screen.blit(self.menu_bg, (0, 0))

        title_surf = self.font.render("ELEMENTAL", True, (255, 0, 0))
        title_rect = title_surf.get_rect(center=(400, 150))
        self.screen.blit(title_surf, title_rect)

        self.screen.blit(self.btn_comecar_img, self.btn_comecar_rect)
        self.screen.blit(self.btn_sair_img, self.btn_sair_rect)


    def handle_main_menu_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()

                if self.btn_comecar_rect.collidepoint(mx, my):
                    self.start_new_game()

                elif self.btn_sair_rect.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()


    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000
            events = pygame.event.get()

            # Fechar janela sempre
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # ----- MENU INICIAL -----
            if self.state == "main_menu":
                self.handle_main_menu_events(events)
                self.draw_main_menu()
                pygame.display.update()
                continue

            # ----- EXPLORAÇÃO -----
            elif self.state == "exploration":
                self.level.run(dt, events)
                pygame.display.update()

                # se pedir combate, entra na arena
                if self.level.combat_requested:
                    self.level.stop_all_sounds()
                    self.open_arena_from_level()

                continue

            # ----- ARENA -----
            elif self.state == "arena":
                result = self.arena.run(events)

                if result == "return":
                    Game.inimigo_vivo = self.arena.enemy_alive

                    self.state = "exploration"
                    self.level = Level(self.screen, inimigo_vivo=Game.inimigo_vivo)

                    self.level.player.life = 100
                    self.level.player.rect.topleft = self.level.initial_player_pos
                    self.level.combat_requested = False

                continue


if __name__ == '__main__':
    game = Game()
    game.run()

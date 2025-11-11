import pygame
import sys
from level import Level
from arena import Arena

class Game:
    inimigo_vivo = True

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Sprout Land - Deserto')
        self.clock = pygame.time.Clock()

        # Estado inicial
        self.state = "exploration"
        self.level = Level(self.screen, inimigo_vivo=Game.inimigo_vivo)
        self.arena = None

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # ---------------- EXPLORAÇÃO ----------------
            if self.state == "exploration":
                self.level.run(dt, events)
                pygame.display.update()

                # Se o jogador pediu combate, vai pra arena
                if self.level.combat_requested:
                    self.state = "arena"
                    self.arena = Arena(
                        self.screen,
                        player_life=self.level.player.life,
                        inimigo_vivo=Game.inimigo_vivo
                    )

            # ---------------- ARENA ----------------
            elif self.state == "arena":
                result = self.arena.run(events)

                if result == "return":
                    # Atualiza estado do inimigo e vida do player
                    Game.inimigo_vivo = self.arena.enemy_alive
                    player_life = self.arena.player["life"]

                    # Volta pra exploração
                    self.state = "exploration"

                    # Se perdeu o combate
                    if not self.arena.vitoria:
                        # Cria novo Level e reseta jogador
                        self.level = Level(self.screen, inimigo_vivo=Game.inimigo_vivo)
                        self.level.player.life = 100  # revive com vida cheia
                        self.level.player.rect.topleft = self.level.initial_player_pos
                    else:
                        # Vitória — mantém vida atual e inimigo morto
                        self.level = Level(self.screen, inimigo_vivo=Game.inimigo_vivo)
                        self.level.player.life = player_life

                    # Garante que o combate foi encerrado
                    self.level.combat_requested = False

if __name__ == '__main__':
    game = Game()
    game.run()

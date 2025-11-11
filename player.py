import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        # Caminhos dos sprites por direção
        base_path = "assets/player"
        self.sprites = {
            "baixo": pygame.image.load(os.path.join(base_path, "baixo.png")).convert_alpha(),
            "cima": pygame.image.load(os.path.join(base_path, "cima.png")).convert_alpha(),
            "direita": pygame.image.load(os.path.join(base_path, "direita.png")).convert_alpha(),
            "esquerda": pygame.image.load(os.path.join(base_path, "esquerda.png")).convert_alpha(),
        }

        # Carregar animações ajustadas
        self.animations = self.load_frames()

        # Direção inicial
        self.direction = "baixo"
        self.frame_index = 0
        self.image = self.animations[self.direction][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # Movimento
        self.speed = 150
        self.moving = False
        self.last_update = 0
        self.frame_rate = 0.15  # segundos entre frames

    def load_frames(self):
        """Recorta e organiza os frames de cada direção, detectando automaticamente a orientação."""
        animations = {}
        scale_factor = 0.35  # ajuste de tamanho (2x opcional)

        for direction, sheet in self.sprites.items():
            sheet_width = sheet.get_width()
            sheet_height = sheet.get_height()

            # Detectar orientação automaticamente
            if sheet_width > sheet_height:
                # Frames dispostos na horizontal
                num_frames = max(1, sheet_width // sheet_height)
                frame_width = sheet_width // num_frames
                frame_height = sheet_height
                horizontal = True
            else:
                # Frames dispostos na vertical
                num_frames = max(1, sheet_height // sheet_width)
                frame_width = sheet_width
                frame_height = sheet_height // num_frames
                horizontal = False

            frames = []
            for i in range(num_frames):
                if horizontal:
                    rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                else:
                    rect = pygame.Rect(0, i * frame_height, frame_width, frame_height)

                # Evitar erro de recorte
                if rect.right > sheet_width or rect.bottom > sheet_height:
                    break

                image = sheet.subsurface(rect)
                new_size = (int(frame_width * scale_factor), int(frame_height * scale_factor))
                image = pygame.transform.scale(image, new_size)
                frames.append(image)

            animations[direction] = frames

        return animations

    def handle_input(self, dt):
        """Verifica teclas pressionadas e move o player."""
        keys = pygame.key.get_pressed()
        self.moving = False
        movement = pygame.Vector2(0, 0)

        if keys[pygame.K_w]:
            movement.y -= 1
            self.direction = "cima"
            self.moving = True
        elif keys[pygame.K_s]:
            movement.y += 1
            self.direction = "baixo"
            self.moving = True
        elif keys[pygame.K_a]:
            movement.x -= 1
            self.direction = "esquerda"
            self.moving = True
        elif keys[pygame.K_d]:
            movement.x += 1
            self.direction = "direita"
            self.moving = True

        if movement.length() > 0:
            movement = movement.normalize()

        self.rect.x += movement.x * self.speed * dt
        self.rect.y += movement.y * self.speed * dt

    def animate(self, dt):
        """Atualiza o frame da animação."""
        if self.moving:
            self.last_update += dt
            if self.last_update >= self.frame_rate:
                self.last_update = 0
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.direction])
                self.image = self.animations[self.direction][self.frame_index]
        else:
            self.frame_index = 0
            self.image = self.animations[self.direction][self.frame_index]

    def update(self, dt):
        self.handle_input(dt)
        self.animate(dt)

import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.max_life = 100
        self.life = self.max_life  

        base_path = "assets/player"
        self.sprites = {
            "baixo": pygame.image.load(os.path.join(base_path, "baixo.png")).convert_alpha(),
            "cima": pygame.image.load(os.path.join(base_path, "cima.png")).convert_alpha(),
            "direita": pygame.image.load(os.path.join(base_path, "direita.png")).convert_alpha(),
            "esquerda": pygame.image.load(os.path.join(base_path, "esquerda.png")).convert_alpha(),
        }

        self.animations = self.load_frames()
        self.direction = "baixo"
        self.frame_index = 0
        self.image = self.animations[self.direction][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        self.speed = 150
        self.moving = False
        self.last_update = 0
        self.frame_rate = 0.15

    def load_frames(self):
        animations = {}
        scale_factor = 0.35
        for direction, sheet in self.sprites.items():
            sheet_width, sheet_height = sheet.get_size()
            horizontal = sheet_width > sheet_height
            num_frames = max(1, sheet_width // sheet_height if horizontal else sheet_height // sheet_width)
            frame_width = sheet_width // num_frames if horizontal else sheet_width
            frame_height = sheet_height if horizontal else sheet_height // num_frames

            frames = []
            for i in range(num_frames):
                rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height) if horizontal else pygame.Rect(0, i * frame_height, frame_width, frame_height)
                image = sheet.subsurface(rect)
                new_size = (int(frame_width * scale_factor), int(frame_height * scale_factor))
                image = pygame.transform.scale(image, new_size)
                frames.append(image)
            animations[direction] = frames
        return animations

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        self.moving = False
        movement = pygame.Vector2(0, 0)

        if keys[pygame.K_w]: movement.y -= 1; self.direction = "cima"; self.moving = True
        if keys[pygame.K_s]: movement.y += 1; self.direction = "baixo"; self.moving = True
        if keys[pygame.K_a]: movement.x -= 1; self.direction = "esquerda"; self.moving = True
        if keys[pygame.K_d]: movement.x += 1; self.direction = "direita"; self.moving = True

        if movement.length() > 0:
            movement = movement.normalize()

        self.rect.x += movement.x * self.speed * dt
        self.rect.y += movement.y * self.speed * dt

        # Limites da tela
        self.rect.clamp_ip(pygame.Rect(0, 0, 800, 600))

    def animate(self, dt):
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

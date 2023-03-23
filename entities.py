import pygame
from math import sqrt
from tools import SpriteGroup


class Ghost:
    def __init__(self, x, y, color):
        self.images = []

        for direction in ["up", "right", "down", "left"]:
            img = pygame.image.load(f"sprites/ghosts/ghost_{color}_{direction}.png").convert_alpha()
            img = pygame.transform.scale(img, (40, 40))
            self.images.append(img)

        self.rect = pygame.Rect(x, y, self.images[0].get_width(), self.images[0].get_height())
        self.precise_mask = pygame.mask.from_surface(self.images[0])

        self.vx = 0
        self.vy = 0

        self.x = x
        self.y = y

        self.accel = 0.05
        self.max_speed = 2
        self.direction = None

    def update(self, player, dt):
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y

        dc = sqrt(dx ** 2 + dy ** 2)  # Calculate magnitude of vector
        ratio = self.accel / dc  # Calculate ratio between acceleration speed and magnitude

        accel_x = dx * ratio  # Calculate normilized vectors
        accel_y = dy * ratio

        self.vx += accel_x * dt * 125  # Apply acceleration
        self.vy += accel_y * dt * 125

        dc = sqrt(self.vx ** 2 + self.vy ** 2)  # Calculate magnitude of vector
        ratio = self.max_speed / dc  # Calculate ratio between acceleration speed and magnitude

        if ratio < 1:
            self.vx *= ratio
            self.vy *= ratio

        self.x += self.vx * dt * 125
        self.y += self.vy * dt * 125

        self.rect.x = self.x
        self.rect.y = self.y

        if abs(dx) > abs(dy):
            self.direction = 1 if dx > 0 else 3
        else:
            self.direction = 2 if dy > 0 else 0

    def check_collision(self, player):
        offset_x = self.rect.x - player.rect.x
        offset_y = self.rect.y - player.rect.y

        return player.sprite_group.mask.overlap(self.precise_mask, (offset_x, offset_y))

    def draw(self, screen):
        img = self.images[self.direction]
        screen.blit(img, self.rect)


class Player:
    def __init__(self, x, y):
        self.sprite_group = SpriteGroup("sprites/player", "dino", 0.25, (45, 51))
        self.rect = pygame.Rect(x, y, 45, 51)

        self.mask = pygame.mask.Mask((self.rect.width, self.rect.height))
        self.mask.fill()

        self.vx = 0
        self.vy = 0

        self.on_ground = False
        self.dunked = False
        self.left = False

        self.sprite_group.add_rule(lambda: self.dunked, "dunking")
        self.sprite_group.add_rule(lambda: not self.on_ground and self.vy > 0, "falling")
        self.sprite_group.add_rule(lambda: not self.on_ground, "jumping")
        self.sprite_group.add_rule(lambda: self.vx != 0, "walking")
        self.sprite_group.add_rule(lambda: self.on_ground, "standing")
        self.sprite_group.set_mirror(lambda: self.left)

    def update_on_ground(self, stage):
        self.rect.y += 1
        self.on_ground = bool(self.check_collision(stage))
        self.rect.y -= 1

        if self.on_ground:
            self.vy = 0
            self.land()

    def check_collision(self, stage):
        offset_x = self.rect.x
        offset_y = self.rect.y

        return stage.mask.overlap(self.mask, (offset_x, offset_y))

    def jump(self):
        if self.on_ground:
            self.vy -= 6.5
            self.on_ground = False

    def land(self):
        self.on_ground = True
        self.dunked = False

    def dunk(self):
        if not self.on_ground and not self.dunked:
            self.vy = 10
            self.dunked = True

    def get_keys(self, keys):
        self.vx = 0

        if keys[pygame.K_LEFT]:
            self.vx -= 3
        if keys[pygame.K_RIGHT]:
            self.vx += 3

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.jump()

            elif event.key == pygame.K_DOWN:
                self.dunk()

    def collide_vertical(self, stage, overlap):
        top = self.vy < 0
        x = overlap[0]

        if top:
            y = overlap[1]

            while stage.mask.get_at((x, y)):
                y += 1

            bounce = y - overlap[1]

        else:
            bounce = overlap[1] - (self.rect.y + self.rect.h)

        self.rect.y += bounce

        if not top:
            self.land()

    def slow_collide_vertical(self, stage):
        top = self.vy < 0

        while self.check_collision(stage):
            self.rect.y += 1 if top else -1

        if not top:
            self.land()

    def collide_horizontal(self, stage, overlap):
        left = self.vx < 0
        y = overlap[1]

        if left:
            x = overlap[0]

            while stage.mask.get_at((x, y)):
                x += 1

            bounce = x - overlap[0]

        else:
            x = self.rect.x + self.rect.w

            while stage.mask.get_at((x, y)):
                x -= 1

            bounce = x - (self.rect.x + self.rect.w)

        self.rect.x += bounce

    def slow_collide_horizontal(self, stage):
        left = self.vx < 0

        while self.check_collision(stage):
            self.rect.x += 1 if left else -1

    def update(self, stage, dt):
        if self.vx != 0:
            self.left = self.vx < 0

        self.sprite_group.tick(dt)
        update_rects = [self.rect.copy()]

        if not self.dunked:
            self.rect.x += int(self.vx * dt * 125)

            self.rect.x = max(self.rect.x, 0)
            self.rect.x = min(self.rect.x, stage.image.get_width() - self.rect.w)

            overlap = self.check_collision(stage)

            if overlap:
                self.collide_horizontal(stage, overlap)

            overlap = self.check_collision(stage)

            if overlap:  # Still overlapping, switching to slow correction
                self.slow_collide_horizontal(stage)

        if not self.on_ground:
            self.vy += 0.1 * dt * 125 if not self.dunked else 0
            self.rect.y += int(self.vy * dt * 125)
            overlap = self.check_collision(stage)

            if overlap:
                self.collide_vertical(stage, overlap)

                overlap = self.check_collision(stage)

                if overlap:
                    self.slow_collide_vertical(stage)

                self.vy = 0

        if self.on_ground:
            self.update_on_ground(stage)

        update_rects.append(self.rect)
        return update_rects

    def draw(self, screen):
        screen.blit(self.sprite_group.sprite, self.rect)
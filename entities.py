import pygame


class Player:
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.image.load("sprites/player.png").convert_alpha()
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())
        self.mask = pygame.mask.Mask((self.rect.width, self.rect.height))
        self.mask.fill()

        self.vx = 0
        self.vy = 0

        self.on_ground = False

    def update_on_ground(self, stage):
        self.rect.y += 1
        self.on_ground = bool(self.check_collision(stage))
        self.rect.y -= 1

        if self.on_ground:
            self.vy = 0

    def check_collision(self, stage):
        offset_x = self.rect.x
        offset_y = self.rect.y

        return stage.mask.overlap(self.mask, (offset_x, offset_y))

    def jump(self):
        if self.on_ground:
            self.vy -= 6.5
            self.on_ground = False

    def get_keys(self, keys):
        self.vx = 0

        if keys[pygame.K_LEFT]:
            self.vx -= 3
        if keys[pygame.K_RIGHT]:
            self.vx += 3

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            self.jump()

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
            self.on_ground = True

    def slow_collide_vertical(self, stage):
        top = self.vy < 0

        while self.check_collision(stage):
            self.rect.y += 1 if top else -1

        if not top:
            self.on_ground = True

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
        update_rects = [self.rect.copy()]

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
            self.vy += 0.1 * dt * 125
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
        screen.blit(self.image, self.rect)
import pygame
from math import ceil

pygame.init()
pygame.display.set_caption("Tower Climberen")


info = pygame.display.Info()
w = info


settings = {
    'size': (info.current_w // 2, int(info.current_h * 0.8)),
    'fps': 120
}


def mask_collide(mask, rect, x, y):
    return rect.collidepoint(x, y) and mask.get_at((x - rect.x, y - rect.y))


class Stage:
    def __init__(self, file):
        self.image = pygame.image.load(f"sprites/{file}.png").convert_alpha()
        self.mask = pygame.image.load(f"sprites/{file}_mask.png")
        self.mask.set_colorkey((255, 255, 255))
        self.mask = pygame.mask.from_surface(self.mask.convert_alpha())

    def draw(self, screen):
        screen.blit(self.image, (0, 0))


class Player(pygame.sprite.Sprite):
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
        self.on_ground = not not self.check_collision(stage)
        self.rect.y -= 1

        if self.on_ground:
            self.vy = 0

    def check_collision(self, stage):
        offset_x = self.rect.x
        offset_y = self.rect.y

        return stage.mask.overlap(self.mask, (offset_x, offset_y))

    def jump(self):
        if self.on_ground:
            self.vy -= 7
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


class State:
    def __init__(self, state_id):
        self.id = state_id

        self.done = False
        self.next = None
        self.quit = False
        self.preserve = False
        self.update_rects = []
        self.next_args = []
        self.next_kwargs = {}

    def get_event(self, event):
        pass

    def get_keys(self, keys):
        pass

    def update(self, screen, dt):
        pass

    def startup(self, screen):
        pass

    def restart(self, *args, **kwargs):
        pass

    def destroy(self):
        pass


class Level(State):
    def __init__(self, state_id):
        super().__init__(state_id)

        self.player = None
        self.stage = None

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next = "pause"
                self.preserve = True
                self.done = True

            self.player.get_event(event)

    def get_keys(self, keys):
        self.player.get_keys(keys)

    def restart(self, *args, **kwargs):
        if len(args) != 2:
            return

        x, vy = args

        self.player.rect.x = x
        self.player.vy = vy


class Level1(Level):
    def startup(self, screen):
        w, h = screen.get_size()

        self.player = Player(w // 2, h - 100)
        self.stage = Stage(self.id)

        screen.fill((255, 255, 255))
        self.update_rects = [screen.get_rect()]

    def update(self, screen, dt):
        self.update_rects.extend(self.player.update(self.stage, dt))

        if self.player.rect.y < 0:
            self.player.rect.y = 0
            self.player.vy = 0

            self.next = "level2"
            self.preserve = True
            self.done = True

        # screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (0, 0, 0), self.update_rects[0])
        self.stage.draw(screen)
        self.player.draw(screen)


class Level2(Level):
    def startup(self, screen):
        w, h = screen.get_size()

        self.player = Player(100, h - 250)
        self.stage = Stage(self.id)

        screen.fill((255, 255, 255))
        self.update_rects = [screen.get_rect()]

    def update(self, screen, dt):
        self.update_rects.extend(self.player.update(self.stage, dt))

        if self.player.rect.y < 0:  # Player is above map
            self.player.rect.y = 0
            self.player.vy = 0

            self.next = "level3"
            self.preserve = True
            self.done = True

        if self.player.rect.y + self.player.rect.h > self.stage.image.get_height():  # Player is below map
            self.next_args = [self.player.rect.x, self.player.vy]
            self.done = True

        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, (255, 255, 255), self.update_rects[0])
        self.stage.draw(screen)
        self.player.draw(screen)


class Menu(State):
    def __init__(self, state_id):
        super().__init__(state_id)

        self.start_button = None
        self.start_mask = None
        self.start_rect = None

        self.exit_button = None
        self.exit_mask = None
        self.exit_rect = None

    def startup(self, screen):
        w, h = screen.get_size()

        self.start_button = pygame.image.load("sprites/start_button.png").convert_alpha()
        self.start_mask = pygame.mask.from_surface(self.start_button)
        self.start_rect = self.start_button.get_rect(center=(w // 2, h // 2 - 50))

        self.exit_button = pygame.image.load("sprites/exit_button.png").convert_alpha()
        self.exit_mask = pygame.mask.from_surface(self.exit_button)
        self.exit_rect = self.exit_button.get_rect(center=(w // 2, h // 2 + 50))

        screen.fill((255, 255, 255))

        screen.blit(self.start_button, self.start_rect)
        screen.blit(self.exit_button, self.exit_rect)

        self.update_rects.append(screen.get_rect())

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.quit = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            x, y = pygame.mouse.get_pos()

            if mask_collide(self.start_mask, self.start_rect, x, y):
                self.next = "level1"
                self.done = True

            elif mask_collide(self.exit_mask, self.exit_rect, x, y):
                self.quit = True


class Pause(State):
    def __init__(self, state_id):
        super().__init__(state_id)
        self.resume_button = None
        self.resume_mask = None
        self.resume_rect = None

        self.restart_button = None
        self.restart_mask = None
        self.restart_rect = None

        self.menu_button = None
        self.menu_mask = None
        self.menu_rect = None

        self.exit_button = None
        self.exit_mask = None
        self.exit_rect = None

    def startup(self, screen):
        w, h = screen.get_size()

        self.resume_button = pygame.image.load("sprites/resume_button.png").convert_alpha()
        self.resume_mask = pygame.mask.from_surface(self.resume_button)
        self.resume_rect = self.resume_button.get_rect(center=(w // 2, h // 2 - 150))

        self.restart_button = pygame.image.load("sprites/restart_button.png").convert_alpha()
        self.restart_mask = pygame.mask.from_surface(self.restart_button)
        self.restart_rect = self.restart_button.get_rect(center=(w // 2, h // 2 - 50))

        self.menu_button = pygame.image.load("sprites/menu_button.png").convert_alpha()
        self.menu_mask = pygame.mask.from_surface(self.menu_button)
        self.menu_rect = self.menu_button.get_rect(center=(w // 2, h // 2 + 50))

        self.exit_button = pygame.image.load("sprites/exit_button.png").convert_alpha()
        self.exit_mask = pygame.mask.from_surface(self.exit_button)
        self.exit_rect = self.exit_button.get_rect(center=(w // 2, h // 2 + 150))

        screen.blit(self.resume_button, self.resume_rect)
        screen.blit(self.restart_button, self.restart_rect)
        screen.blit(self.menu_button, self.menu_rect)
        screen.blit(self.exit_button, self.exit_rect)

        self.update_rects.append(screen.get_rect())

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            x, y = pygame.mouse.get_pos()

            if mask_collide(self.resume_mask, self.resume_rect, x, y):
                self.done = True

            elif mask_collide(self.restart_mask, self.restart_rect, x, y):
                self.next = "level1"
                self.done = True

            elif mask_collide(self.menu_mask, self.menu_rect, x, y):
                self.next = "menu"
                self.done = True

            elif mask_collide(self.exit_mask, self.exit_rect, x, y):
                self.quit = True


class Control:
    def __init__(self, start_state, **settings):
        self.__dict__.update(settings)
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = states[start_state](start_state)
        self.state.startup(self.screen)
        self.backlog_state = []

    def flip_state(self):
        state_id = self.state.next

        if state_id is None:
            backlogged = self.backlog_state.pop()

            backlogged.restart(*self.state.next_args, **self.state.next_kwargs)
            backlogged.next = None
            self.state.destroy()
            self.state = backlogged

            return

        if self.state.preserve:
            self.backlog_state.append(self.state)
            self.state.done = False
        else:
            self.state.destroy()
            self.backlog_state.clear()

        self.state = states[state_id](state_id, *self.state.next_args, **self.state.next_kwargs)  # Initialize new state
        self.state.startup(self.screen)

    def update(self, dt):
        if self.state.quit:
            self.running = False

        elif self.state.done:
            self.flip_state()

        self.state.update(self.screen, dt)

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.state.get_event(event)

        self.state.get_keys(pygame.key.get_pressed())

    def main_game_loop(self):
        delta_time = 1 / self.fps

        while self.running:
            self.event_loop()
            self.update(delta_time)
            pygame.display.update()  # self.state.update_rects
            self.state.update_rects.clear()
            delta_time = self.clock.tick(self.fps) / 1000.0


states = {
    "menu": Menu,
    "level1": Level1,
    "level2": Level2,
    "level3": None,
    "pause": Pause
}


if __name__ == "__main__":
    cont = Control("menu", **settings)
    cont.main_game_loop()

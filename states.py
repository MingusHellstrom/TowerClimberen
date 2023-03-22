import pygame
from entities import Player, Ghost
import random


level_info = {
    "level1": {
        "start_pos": (480, 764),
        "next_state": "level5",
        "is_first": True,
        "ghosts": [
            (500, 100, "orange")
        ]
    },
    "level2": {
        "start_pos": (100, 614),
        "next_state": "level3",
        "is_first": False,
        "ghosts": [
            (500, 100, "orange")
        ]
    },
    "level3": {
        "start_pos": (100, 614),
        "next_state": "level4",
        "is_first": False,
        "ghosts": [
            (500, 100, "orange")
        ]
    },
    "level4": {
        "start_pos": (100, 614),
        "next_state": "level5",
        "is_first": False,
        "ghosts": [
            (500, 100, "orange")
        ]
    },
    "level5": {
        "start_pos": (50, 764),
        "next_state": "menu",
        "is_first": False,
        "ghosts": [
            (800, 750, "orange")
        ]
    }
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
        self.done = False
        self.next = None
        self.quit = False
        self.preserve = False
        self.update_rects = []
        self.next_args = []
        self.next_kwargs = {}

    def destroy(self):
        pass


class Level(State):
    def __init__(self, state_id):
        super().__init__(state_id)

        self.player = None
        self.stage = None
        self.ghosts = None

        self.start_pos = None
        self.next_state = None
        self.is_first = None

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next = "pause"
                self.preserve = True
                self.done = True

            self.player.get_event(event)

    def get_keys(self, keys):
        self.player.get_keys(keys)

    def startup(self, screen):
        self.start_pos = level_info[self.id]["start_pos"]
        self.next_state = level_info[self.id]["next_state"]
        self.is_first = level_info[self.id]["is_first"]
        ghosts = level_info[self.id]["ghosts"]

        self.player = Player(*self.start_pos)
        self.stage = Stage(self.id)
        self.ghosts = []

        for ghost in ghosts:
            self.ghosts.append(Ghost(*ghost))

        screen.fill((255, 255, 255))
        self.update_rects = [screen.get_rect()]

    def restart(self, *args, **kwargs):
        if len(args) == 3:
            x, vy, dunked = args

            self.player.rect.x = x
            self.player.vy = vy
            self.player.dunked = dunked

            for ghost in self.ghosts:
                ghost.x = random.randint(0, self.stage.image.get_width())
                ghost.y = random.randint(0, self.stage.image.get_height())

        super().restart()

    def update(self, screen, dt):
        self.update_rects.extend(self.player.update(self.stage, dt))

        for ghost in self.ghosts:
            ghost.update(self.player, dt)

            if ghost.check_collision(self.player):
                self.done = True
                self.next = "menu"

        if self.player.rect.y < 0:
            self.player.rect.y = 0
            self.player.vy = 0

            self.next = self.next_state
            self.preserve = True
            self.done = True

        if not self.is_first and self.player.rect.y + self.player.rect.h > self.stage.image.get_height():  # Player is below map
            self.next_args = [self.player.rect.x, self.player.vy, self.player.dunked]
            self.done = True

        self.stage.draw(screen)
        self.player.draw(screen)

        for ghost in self.ghosts:
            ghost.draw(screen)


class Level1(Level):
    pass

class Level2(Level):
    pass

class Level3(Level):
    pass

class Level4(Level):
    pass

class Level5(Level):
    pass


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
import pygame
from math import ceil

pygame.init()
pygame.display.set_caption("Tower Climberen")


info = pygame.display.Info()
w = info


settings = {
    'size': (info.current_w // 2, int(info.current_h * 0.8)),
    'fps': 60
}


def scale_speed(speed, dt):
    return speed * dt * 125


class Stage:
    def __init__(self, file):
        self.image = pygame.image.load(file).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

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
            self.vy -= 6

    def get_keys(self, keys):
        self.vx = 0

        if keys[pygame.K_LEFT]:
            self.vx -= 3
        if keys[pygame.K_RIGHT]:
            self.vx += 3

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            self.jump()

    def collide(self, stage, overlap, real_vy):
        if real_vy > 0:  # Player is moving downwards
            bounce = overlap[1] - (self.rect.y + self.rect.h)

            if real_vy < abs(bounce):  # Collision could not have occured vertically
                self.collide_horizontal(stage, overlap)

            else:
                self.rect.y += bounce
                self.on_ground = True
                self.vy = 0

        else:
            x, y = overlap

            while stage.mask.get_at((x, y)):
                y += 1

            bounce = y - overlap[1] - 1

            if abs(real_vy) < bounce:  # Collision could not have occured vertically
                self.collide_horizontal(stage, overlap)

            else:
                self.rect.y += bounce + 4
                self.vy = 0


    def collide_horizontal(self, stage, overlap):
        left = self.rect.x == overlap[0]
        y = overlap[1]

        try:
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

        except IndexError:  # Outside map
            return

        self.rect.x += bounce
        # self.vx = 0

    def update(self, stage, dt):
        update_rects = [self.rect.copy()]

        if abs(self.vy) > 1:  # Movement is happening
            self.on_ground = False

        if not self.on_ground:
            self.vy += 0.1 * dt * 125
            real_vy = self.vy * dt * 125
            self.rect.y += int(real_vy)
            overlap_point = self.check_collision(stage)

            if overlap_point:  # Check if collision has occured
                self.collide(stage, overlap_point, real_vy)  # Handle collision

        self.rect.x += int(self.vx * dt * 125)

        self.rect.x = max(self.rect.x, 0)
        self.rect.x = min(self.rect.x, stage.image.get_width() - self.rect.w)

        if self.on_ground:
            self.update_on_ground(stage)

        update_rects.append((self.rect.x, self.rect.y, self.rect.w, self.rect.h))
        return update_rects

        # return [(update_rect.x - 30, update_rect.y - 30, update_rect.w + 60, update_rect.h + 60)]

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class State:
    def __init__(self):
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

    def destroy(self):
        pass


class Level1(State):
    def __init__(self):
        super().__init__()

        self.player = None
        self.stage = None

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.quit = True

            self.player.get_event(event)

    def get_keys(self, keys):
        self.player.get_keys(keys)

    def startup(self, screen):
        w, h = screen.get_size()

        self.player = Player(w // 2, h - 100)
        self.stage = Stage("sprites/level1.png")

        screen.fill((255, 255, 255))
        self.update_rects = [screen.get_rect()]

    def update(self, screen, dt):
        self.update_rects.extend(self.player.update(self.stage, dt))

        # screen.fill((255, 255, 255))
        pygame.draw.rect(screen, (255, 255, 255), self.update_rects[0])
        self.stage.draw(screen)
        self.player.draw(screen)


class Menu(State):
    def __init__(self):
        super().__init__()
        self.button = None

    def startup(self, screen):
        w, h = screen.get_size()

        self.button = pygame.Rect((w // 2, h // 2, 100, 60))
        self.button.center = (w // 2, h // 2)

        pygame.draw.rect(screen, (255, 255, 255), self.button)
        self.update_rects.append(self.button)

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.quit = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            x, y = pygame.mouse.get_pos()

            if self.button.collidepoint(x, y):
                self.next = "level1"
                self.done = True

    def update(self, screen, dt):
        pass


class Control:
    def __init__(self, start_state, **settings):
        self.__dict__.update(settings)
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = states[start_state]()
        self.state.startup(self.screen)
        self.backlog_state = None

    def flip_state(self):
        state_id = self.state.next

        if state_id is None:
            self.state.destroy()
            self.state = self.backlog_state
            self.backlog_state = None
            return

        if self.state.preserve:
            self.backlog_state = self.state
        else:
            self.state.destroy()
            self.backlog_state = None

        self.state = states[state_id](*self.state.next_args, **self.state.next_kwargs)  # Initialize new state
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
        delta_time = 0.009

        while self.running:
            self.update(delta_time)
            self.event_loop()
            delta_time = self.clock.tick(self.fps) / 1000.0
            pygame.display.update()  # self.state.update_rects
            self.state.update_rects.clear()


states = {
    "menu": Menu,
    "level1": Level1,
    "level2": None,
    "level3": None,
    "pause": None
}


if __name__ == "__main__":
    cont = Control("menu", **settings)
    cont.main_game_loop()

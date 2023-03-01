import pygame

pygame.init()
pygame.display.set_caption("Tower Climberen")


settings = {
    'size':(600,400),
    'fps' :60
}


class State:
    def __init__(self, controller):
        self.done = False
        self.next = None
        self.quit = False
        self.preserve = False
        self.update_rects = []

        self.con = controller

    def get_event(self, event):
        pass

    def update(self, screen, dt):
        pass

    def startup(self):
        pass

    def destroy(self):
        pass


class Menu(State):
    def __init__(self, controller):
        super().__init__(controller)

        w, h = self.con.screen.get_size()

        self.button = pygame.Rect((w // 2, h // 2, 100, 60))
        self.button.center = (w // 2, h // 2)

    def update(self, screen, dt):
        pygame.draw.rect(screen, (255, 255, 255), self.button)
        self.update_rects = self.button


class Control:
    def __init__(self, start_state, **settings):
        self.__dict__.update(settings)
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = states[start_state](self)
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

        self.state = states[state_id](self, *self.state.next_args, **self.state.next_kwargs)  # Initialize new state
        self.state.startup()

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

    def main_game_loop(self):
        while self.running:
            delta_time = self.clock.tick(self.fps) / 1000.0
            self.event_loop()
            self.update(delta_time)
            pygame.display.update(self.state.update_rects)


states = {
    "menu": Menu,
    "level1": None,
    "level2": None,
    "level3": None,
    "pause": None
}


if __name__ == "__main__":
    cont = Control("menu", **settings)
    cont.main_game_loop()

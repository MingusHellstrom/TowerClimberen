import states
import pygame


pygame.init()
pygame.display.set_caption("Tower Climberen")


info = pygame.display.Info()
w = info


settings = {
    'size': (info.current_w // 2, int(info.current_h * 0.8)),
    'fps': 120
}


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
            backlogged = self.backlog_state.pop()  # Pop the last state off the stack

            backlogged.restart(*self.state.next_args, **self.state.next_kwargs)  # Reinit the last state with args
            self.state.destroy()  # Call the cleaner
            self.state = backlogged  # Replace current state with backlogged state

            return

        if self.state.preserve:  # Current state is to be preserved
            self.backlog_state.append(self.state)

        else:  # State is not preserved, destroy stack
            self.state.destroy()
            self.backlog_state.clear()

        self.state = states[state_id](state_id, *self.state.next_args, **self.state.next_kwargs)  # Initialize new state
        self.state.startup(self.screen)  # Initialize startup function

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
    "menu": states.Menu,
    "level1": states.Level1,
    "level2": states.Level2,
    "level3": states.Level3,
    "level4": states.Level4,
    "level5": states.Level5,
    "pause": states.Pause
}


if __name__ == "__main__":
    cont = Control("menu", **settings)
    cont.main_game_loop()

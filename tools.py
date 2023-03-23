import pygame
import glob
import os


# pygame.init()
# pygame.display.set_mode((20, 20))


class SpriteGroup:
    def __init__(self, path, name, dt, size=None):
        self.name = name

        self.dt = dt
        self.time = 0
        self.index = 0
        self.group = None

        self.rules = []
        self.mirror_func = None

        self.sprites = {}

        for file in glob.glob(os.path.join(path, name) + "*.png"):
            file_name = os.path.splitext(os.path.split(file)[1])[0]
            _, group, index = file_name.split("_")
            index = int(index)

            if group not in self.sprites:
                self.sprites[group] = []
                self.sprites[f"{group}-mirror"] = []

            if len(self.sprites[group]) - 1 < index:
                self.sprites[group].extend([None] * (index - len(self.sprites[group]) + 1))
                self.sprites[f"{group}-mirror"].extend([None] * (index - len(self.sprites[f"{group}-mirror"]) + 1))

            img = pygame.image.load(file).convert_alpha()

            if size:
                img = pygame.transform.scale(img, size)

            self.sprites[group][index] = img
            self.sprites[f"{group}-mirror"][index] = pygame.transform.flip(img, True, False)

        self.masks = {}

        for group, imgs in self.sprites.items():
            self.masks[group] = []

            for img in imgs:
                self.masks[group].append(pygame.mask.from_surface(img))

    @property
    def sprite(self):
        return self.sprites[self.group][self.index] if not self.mirror_func() else self.sprites[f"{self.group}-mirror"][self.index]

    @property
    def mask(self):
        return self.masks[self.group][self.index] if not self.mirror_func() else self.masks[f"{self.group}-mirror"][self.index]

    def add_rule(self, eval_func, group):
        self.rules.append((eval_func, group))

    def set_mirror(self, eval_func):
        self.mirror_func = eval_func

    def tick(self, dt):
        for eval_func, group in self.rules:
            if eval_func():
                if group != self.group:
                    self.group = group
                    self.time = 0
                    self.index = 0

                break

        self.time += dt

        if self.time > self.dt:
            self.index = (self.index + 1) % len(self.sprites[self.group])
            self.time %= self.dt



if __name__ == "__main__":
    s = SpriteGroup("sprites/player", "dino", size=(15 * 3, 17 * 3))

import pygame

pygame.init()
pygame.display.set_caption("Tower Climberen")


def running():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True


def draw_window():
    window = pygame.display.set_mode((400, 600))
    pygame.display.update()


def main():
    clock = pygame.time.Clock()
    while running():
        draw_window()
        clock.tick(120)


if __name__ == "__main__":
    main()

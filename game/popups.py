import pygame
import pygame.freetype
import textwrap

import pygame_gui

from game import loader


def scale_image(image, scalar):
    return pygame.transform.scale(
        image, (image.get_width() * scalar, image.get_height() * scalar)
    )


def find_center(image):
    return pygame.Vector2(image.get_width() / 2, image.get_height() / 2)


class Newspaper:
    def __init__(self, message):
        newspaper = pygame.image.load(loader.filepath("newspaper.png"))
        newspaper = scale_image(newspaper, 2)
        newspaper = newspaper.convert_alpha()

        font = pygame.freetype.Font(loader.filepath("lato/lato.ttf"))

        lines = textwrap.wrap(message, 29)
        for i, text in enumerate(lines):
            rendered = font.render(text, size=16)[0]
            x = newspaper.get_width() / 2 - rendered.get_width() / 2
            newspaper.blit(rendered, (x, 8 + i * 19))

        self.image = newspaper
        self.location = pygame.Vector2(200, 300)

        self.rotation = 0
        self.rotating = True
        self.finished = False

        self.manager = pygame_gui.UIManager((1280, 720))

    def display(self, time_delta):
        screen = pygame.display.get_surface()

        if self.rotating:
            self.rotation += time_delta * 350

        if self.rotation > 720:
            self.rotation = 0
            self.rotating = False
            self.next_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(50, 450, 300, 50),
                text="Next",
                manager=self.manager,
            )

        im = pygame.transform.rotate(self.image, self.rotation)

        loc = self.location - find_center(im)

        screen.blit(im, loc)

        self.manager.update(time_delta)
        self.manager.draw_ui(pygame.display.get_surface())

        return self.finished

    def process_events(self, event):
        self.manager.process_events(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == "ui_button_pressed":
                if event.ui_element == self.next_button:
                    self.finished = True

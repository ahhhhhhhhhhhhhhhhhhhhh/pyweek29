import pygame
import pygame.freetype
import textwrap

from game import loader

def scale_image(image, scalar):
    return pygame.transform.scale(image, (image.get_width()*scalar, image.get_height()*scalar))

def find_center(image):
    return pygame.Vector2(image.get_width()/2, image.get_height()/2)

news_base = pygame.image.load(loader.filepath("newspaper.png"))
news_base = scale_image(news_base, 2)
news_base = news_base.convert_alpha()


pygame.freetype.init()
font = pygame.freetype.Font(loader.filepath("lato/lato.ttf"))


class Newspaper:
    def __init__(self, message):
        newspaper = news_base.copy()

        lines = textwrap.wrap(message, 29)
        for i, text in enumerate(lines):
            rendered = font.render(text, size=16)[0]
            x = newspaper.get_width()/2 - rendered.get_width()/2
            newspaper.blit(rendered, (x, 8+i*19))
        
        self.image = newspaper
        self.location = pygame.Vector2(640,360)

        self.rotation = 0
        self.rotating = True

    def display(self, time_delta, screen = pygame.display.get_surface()):
        if self.rotating:
            self.rotation += time_delta * 350

        if self.rotation > 720:
            self.rotation = 0
            self.rotating = False
        
        im = pygame.transform.rotate(self.image, self.rotation)

        loc = self.location - find_center(im)

        screen.blit(im, loc)
        

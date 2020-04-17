import pygame
import pygame.freetype
import textwrap
import random

import pygame_gui

from game import loader
from game import events
from game import more_elements
from game.sound import SoundManager


def scale_image(image, scalar):
    return pygame.transform.scale(
        image, (int(image.get_width() * scalar), int(image.get_height() * scalar))
    )


def find_center(image):
    return pygame.Vector2(image.get_width() / 2, image.get_height() / 2)


class Towns:
    names = ["ant", "bee", "default", "destroyed", "future", "pretty", "superhero"]
    images = {}

    for name in names:
        images[name] = scale_image(
            pygame.image.load(loader.filepath(f"towns/{name}.png")), 2
        )

    @staticmethod
    def get_image(name):
        return Towns.images[name]

    current_town = "default"

class Newspaper:
    def __init__(self, message, *args):
        self.playSound = False
        self.next_button = None
        newspaper = pygame.image.load(loader.filepath("newspaper.png"))
        newspaper = scale_image(newspaper, 4)
        newspaper = newspaper.convert_alpha()

        self.headlines = [message, *args] # need to be able to reference headlines easily later for saving gamedata

        messages = [message, *args]
        messages = [mes.title() if "'" not in mes else mes for mes in messages]

        self.font = pygame.freetype.Font(loader.filepath("lora/Lora-Bold.ttf"))

        self._fit_text_to_rect(newspaper, pygame.Rect(12, 12, 564, 90), messages[0])

        messages = messages[1:]

        areas = [
            pygame.Rect(12, 115, 128, 80),
            pygame.Rect(152, 115, 164, 80),
            pygame.Rect(328, 115, 246, 80),
        ]
        random.shuffle(areas)

        for i in range(3):
            if messages:
                mes = messages.pop()
                area = areas.pop()
                self._fit_text_to_rect(newspaper, area, mes)
            else:
                area = areas.pop()

        self.image = newspaper
        self.location = pygame.Vector2(640, 360)

        self.next_event = "_"  # needed for common interface with decisions
        self.name = "newspaper"

    def _fit_text_to_rect(self, image, rect, text):
        # pygame.draw.rect(image, (40,200,75), rect) #shows relevant area

        considering = set()

        for i in range(10, 50):
            t = textwrap.wrap(text, i)
            maxlen = max([len(line) for line in t])
            font_size = 1.75 * (rect.width / maxlen)
            # print(f"{len(t)} lines at {font_size}")
            if font_size * 1.1 * len(t) > rect.height:
                pass
            else:
                considering.add((font_size, tuple(t)))

        if not considering:
            considering.add((rect.height / 1.1, (text,)))

        considering = list(considering)
        considering.sort(key=lambda x: x[0])

        prefs = considering[-1]
        font_size = int(prefs[0])
        lines = prefs[1]

        # used for vertical centering
        vertical_space = len(lines) * font_size + (1.1 * (len(lines) - 1))
        starting_y = rect.y + (rect.height / 2 - vertical_space / 2)

        for i, text in enumerate(lines):
            rendered = self.font.render(text, size=font_size)[0]
            x = (
                rect.x + rect.width / 2 - rendered.get_width() / 2
            )  # horizontal centering by line
            image.blit(rendered, (x, int(starting_y + i * font_size * 1.1)))

    def ready(self):
        self.rotation = 0
        self.maxrotation = 720
        self.rotating = True
        self.finished = False

        self.manager = pygame_gui.UIManager((1280, 720), loader.filepath("theme.json"))

    def display(self, time_delta):
        self.manager.update(time_delta)
        self.manager.draw_ui(pygame.display.get_surface())

        screen = pygame.display.get_surface()

        if self.rotating:
            self.rotation += time_delta * 350

        if self.rotation > self.maxrotation:
            self.rotation = 0
            self.rotating = False
            button_background = pygame_gui.elements.UIImage(
                manager=self.manager,
                relative_rect=pygame.Rect(490, 640, 300, 300),
                image_surface=events.Images.alone_button_image,
            )
            self.next_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(490, 656, 300, 40),
                text="Next",
                manager=self.manager,
            )

        if self.rotating:
            im = scale_image(self.image, self.rotation / self.maxrotation)
        else:
            im = self.image

        im = pygame.transform.rotate(im, self.rotation)

        loc = self.location - find_center(im)

        screen.blit(im, loc)

        if self.playSound == False:
            SoundManager.instance.playNewspaperSound()
            self.playSound = True

        return self.finished

    def process_events(self, event):
        self.manager.process_events(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == "ui_button_pressed":
                if event.ui_element == self.next_button:
                    self.finished = True


class EndScreen:
    def __init__(self):
        self.name = "end screen"

        self.overlay_surf = pygame.Surface((1280, 720))
        self.overlay_surf.convert_alpha()
        self.overlay_surf.fill((255, 0, 0))
        self.overlay_surf.set_alpha(0)

        self.elapsed_time = 0
        self.ui_created = False
        self.end_button = None

        self.message = ""  # set by code that calls this
        # "Thanks to the efforts of a humble ant colony: history is altered"

    def ready(self):
        self.manager = pygame_gui.UIManager((1280, 720), loader.filepath("theme.json"))

    def display(self, time_delta):
        screen = pygame.display.get_surface()

        self.elapsed_time += time_delta
        target_alpha = min(20 * self.elapsed_time, 100)
        if target_alpha != self.overlay_surf.get_alpha():
            self.overlay_surf.set_alpha(target_alpha)

        if self.elapsed_time > 3 and not self.ui_created:
            pygame_gui.elements.UILabel(
                manager=self.manager,
                relative_rect=pygame.Rect(220, 90, 880, 80),
                text="Your colony has failed!",
                object_id="endgame_large",
            )
            pygame_gui.elements.UITextBox(
                manager=self.manager,
                relative_rect=pygame.Rect(500, 450, 330, 150),
                html_text=self.message,
            )
            self.end_button = pygame_gui.elements.UIButton(
                manager=self.manager,
                relative_rect=pygame.Rect(510, 600, 300, 40),
                text="End Game",
            )
            self.ui_created = True

        screen.blit(self.overlay_surf, (0, 0))

        self.manager.update(time_delta)
        self.manager.draw_ui(pygame.display.get_surface())

    def process_events(self, event):
        self.manager.process_events(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == "ui_button_pressed":
                if event.ui_element == self.end_button:
                    pygame.quit()
                    raise SystemExit


class EndgameScreen:
    def __init__(self, name):
        self.name = name

        self.message = "THIS IS AN EXAMPLE MESSAGE"  # set by code that calls this
        # "Thanks to the efforts of a humble ant colony: history is altered"

        self.town = "bee" #name of town to show

        self.elapsed_time = 0
        self.zoom_time = 8
        self.zoom_started = False
        self.zooming = True
        self.zoom_im = None
        self.x = 0.0
        self.y = 0.0

        self.revealed = False

    def ready(self):
        self.manager = pygame_gui.UIManager((1280, 720), loader.filepath("theme.json"))

        self.font_color = "#000000" if self.town != "future" else "#FFFFFF"
  
    def display(self, time_delta):
        screen = pygame.display.get_surface()

        if self.zoom_started: 
            self._display_zoom(time_delta, screen)

        if not self.zoom_started:
            self.zoom_started = True
            self.zoom_im = screen.copy()

        self.manager.update(time_delta)
        self.manager.draw_ui(screen)

        return False

    def _display_zoom(self, time_delta, screen):
        self.elapsed_time += time_delta

        if self.zooming:
            self.x = -3592 * self.elapsed_time / self.zoom_time
            self.y = -192 * self.elapsed_time / self.zoom_time
            
        if self.elapsed_time > self.zoom_time and self.zooming:
            self.zooming = False
            self.zoom_im = scale_image(self.zoom_im, 4)

        if self.elapsed_time > self.zoom_time + 2 and not self.revealed:
            self.revealed = True
            surf = pygame.Surface((1280, 720))
            surf.blit(scale_image(Towns.get_image(self.town), 4), (0, 0))
            self.zoom_im = surf
            self.x = 0
            self.y = 0

            pygame_gui.elements.UITextBox(
                manager=self.manager,
                relative_rect=pygame.Rect(200, 90, 880, 100),
                html_text=f"<font color={self.font_color}>Congratulations</font>",
                object_id="endgame_large",
            )
            pygame_gui.elements.UITextBox(
                manager=self.manager,
                relative_rect=pygame.Rect(200, 150, 880, 100),
                html_text=f"<font color={self.font_color}>You have changed the course of history</font>",
                object_id="endgame_subtitle",
            )
            pygame_gui.elements.UITextBox(
                manager=self.manager,
                relative_rect=pygame.Rect(440, 290, 400, 200),
                html_text=f"<font color={self.font_color}>{self.message}</font>",
            )
            self.end_button = more_elements.TextButton(
                manager=self.manager,
                relative_rect=pygame.Rect(520, 560, 110, 40),
                html_text=f"<font color={self.font_color}>End Game</font>",
            )

        if self.zooming:
            current_zoom = scale_image(self.zoom_im, 1 + (3/self.zoom_time * self.elapsed_time))
            screen.blit(current_zoom, (int(self.x), int(self.y)))
        else:
            screen.blit(self.zoom_im, (int(self.x), int(self.y)))

    def process_events(self, event):
        self.manager.process_events(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == "ui_button_pressed":
                if event.ui_element == self.end_button:
                    pygame.quit()
                    raise SystemExit

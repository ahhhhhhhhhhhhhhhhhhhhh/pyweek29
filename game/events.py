import pygame
import pygame_gui

from game.resources import Resources
from game import loader
from game import more_elements


class Images:
    scroll_image = pygame.transform.scale(
        pygame.image.load(loader.filepath("ui_images/scroll004.png")), (400, 300)
    )
    button_scroll_image = pygame.transform.scale(
        pygame.image.load(loader.filepath("ui_images/button.png")), (300, 300)
    )
    button_ext_image = pygame.transform.scale(
        pygame.image.load(loader.filepath("ui_images/button_ext.png")), (300, 300)
    )
    alone_button_image = pygame.transform.scale(
        pygame.image.load(loader.filepath("ui_images/alone-button.png")), (300, 100)
    )
    food_icon = pygame.transform.scale(
        pygame.image.load(loader.filepath("food_icon.png")), (40, 40)
    )
    pop_icon = pygame.transform.scale(
        pygame.image.load(loader.filepath("pop_icon.png")), (40, 40)
    )
    territory_icon = pygame.transform.scale(
        pygame.image.load(loader.filepath("territory_icon.png")), (40, 40)
    )


def impacts_to_html(outcome):
    orig_outcome = outcome
    outcome = [str(i) for i in outcome]
    outcome = ["+" + i if int(i) > 0 else i for i in outcome]
    outcome = [
        f"<font color='#FF0000'>{i}</font>"
        if int(i) < 0
        else f"<font color='#00FF00'>{i}</font>"
        for i in outcome
    ]
    out = ""
    icons = []
    if orig_outcome[0] != 0:
        out += f"<br>{outcome[0]} <font color='#FFFF00'>food</font>"
        icons.append(Images.food_icon)
    if orig_outcome[1] != 0:
        out += f"<br>{outcome[1]} <font color='#FF00FF'>population</font>"
        icons.append(Images.pop_icon)
    if orig_outcome[2] != 0:
        out += f"<br>{outcome[2]} <font color='#00FFFF'>territory</font>"
        icons.append(Images.territory_icon)
    return out, icons


class Event:
    def __init__(self, name):
        self.name = name

        self.text = "text"
        self.impacts = [0, 0, 0]  # food, population, territory

        self.next_event = "_"  # needed for common interface with decisions

    def ready(self):
        self.manager = pygame_gui.UIManager((1280, 720), loader.filepath("theme.json"))

        html, icons = impacts_to_html(self.impacts)

        self.button_ext_background = pygame_gui.elements.UIImage(
            manager=self.manager,
            relative_rect=pygame.Rect(50, 150, 300, 300),
            image_surface=Images.button_ext_image,
        )
        self.button_background = pygame_gui.elements.UIImage(
            manager=self.manager,
            relative_rect=pygame.Rect(50, 200, 300, 300),
            image_surface=Images.button_scroll_image,
        )
        self.background_image = pygame_gui.elements.UIImage(
            manager=self.manager,
            relative_rect=pygame.Rect(15, 150, 400, 300),
            image_surface=Images.scroll_image,
        )

        self.textbox = pygame_gui.elements.UITextBox(
            manager=self.manager,
            relative_rect=pygame.Rect(50, 175, 300, 200),
            html_text=self.text + html,
        )

        self.next_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(50, 400, 300, 40),
            text="Next",
            manager=self.manager,
        )

        Resources.instance.food += self.impacts[0]
        Resources.instance.population += self.impacts[1]
        Resources.instance.territory += self.impacts[2]

        self.finished = False

    def display(self, time_delta):
        self.manager.update(time_delta)
        self.manager.draw_ui(pygame.display.get_surface())

        return self.finished

    def process_events(self, event):
        self.manager.process_events(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == "ui_button_pressed":
                if event.ui_element == self.next_button:
                    self.finished = True


class Decision:
    def __init__(self, name):
        self.name = name

        self.hook = True  # if decision is the beginning of a series of events/decisions

        self.text = "text"
        self.options = ["choice 1", "choice 2", "choice 3"]
        self.outcomes = ["this happened", "that happened", "something else"]
        self.impacts = [
            [1, 1, 1],
            [0, 0, 0],
            [0, 0, 0],
        ]  # [food, population, territory]
        self.leads_to = ["_", "_", "_"]  # _ means no following event
        self.next_event = "_"

    def ready(self):
        self.manager = pygame_gui.UIManager((1280, 720), loader.filepath("theme.json"))

        self.button_ext_background = pygame_gui.elements.UIImage(
            manager=self.manager,
            relative_rect=pygame.Rect(50, 150, 300, 300),
            image_surface=Images.button_ext_image,
        )
        self.button_background = pygame_gui.elements.UIImage(
            manager=self.manager,
            relative_rect=pygame.Rect(50, 150 + len(self.options) * 50, 300, 300),
            image_surface=Images.button_scroll_image,
        )
        self.background_image = pygame_gui.elements.UIImage(
            manager=self.manager,
            relative_rect=pygame.Rect(15, 150, 400, 300),
            image_surface=Images.scroll_image,
        )
        self.textbox = pygame_gui.elements.UITextBox(
            manager=self.manager,
            relative_rect=pygame.Rect(50, 175, 300, 200),
            html_text=self.text,
        )

        self.decision_buttons = []
        cumulative_height = 400
        for i, option in enumerate(self.options):
            button = more_elements.TextButton(
                relative_rect=pygame.Rect(50, cumulative_height, 300, 20),
                text=option,
                manager=self.manager,
            )
            cumulative_height += button.relative_rect.height + 10
            self.decision_buttons.append(button)

        self.button_background.set_position(
            pygame.Rect(50, cumulative_height - 250, 300, 300)
        )

        self.finished = False

        self.next_button = None

    def display(self, time_delta):
        self.manager.update(time_delta)
        self.manager.draw_ui(pygame.display.get_surface())
        return self.finished

    def process_events(self, event):
        self.manager.process_events(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == "ui_button_pressed":
                if event.ui_element in self.decision_buttons:
                    user_choice = self.decision_buttons.index(event.ui_element)

                    self.textbox.html_text = self.outcomes[user_choice]
                    html, icons = impacts_to_html(self.impacts[user_choice])
                    self.textbox.html_text += html
                    self.textbox.rebuild()

                    self._update_resources(user_choice)

                    for button in self.decision_buttons:
                        button.kill()

                    self.button_background.set_relative_position(
                        pygame.Rect(50, 200, 300, 300)
                    )

                    self.next_button = pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect(50, 400, 300, 40),
                        text="Next",
                        manager=self.manager,
                    )

                    self.next_event = self.leads_to[user_choice]

                if event.ui_element == self.next_button:
                    self.finished = True

    def _update_resources(self, user_choice):
        Resources.instance.food += self.impacts[user_choice][0]
        Resources.instance.population += self.impacts[user_choice][1]
        Resources.instance.territory += self.impacts[user_choice][2]


class Quest:
    def __init__(self, name):
        self.name = name
        self.decision = Decision(name)

        self.prereqs = [0, 0, 0]  # food, population, territory
        self.newspaper_lines = [
            "_",
            "_",
            "_",
        ]  # line that gets put into the newspaper queue
        self.is_headline = False  # if newspaper line is meant to be headline

        self.endgame_image = None

    def ready(self):
        self.decision.ready()

    def display(self, time_delta):
        return self.decision.display(time_delta)

    def process_events(self, event):
        self.decision.process_events(event)
        self.finished = self.decision.finished
        self.next_event = self.decision.next_event

        # prevents an error when all of a quest's options leads to another event
        if self.next_event in self.decision.leads_to:
            self.chosen_line = self.newspaper_lines[
                self.decision.leads_to.index(self.next_event)
            ]

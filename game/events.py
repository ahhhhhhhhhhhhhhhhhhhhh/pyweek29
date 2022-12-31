import pygame
import pygame_gui

from game import loader, more_elements, popups
from game.popups import scale_image
from game.resources import Resources


class Images:
    scroll_image = pygame.transform.scale(
        pygame.image.load(loader.filepath("ui_images/scroll004.png")), (400, 300)
    )
    scroll_image1 = pygame.transform.scale(
        pygame.image.load(loader.filepath("ui_images/scroll001.png")), (400, 300)
    )
    scroll_image2 = pygame.transform.scale(
        pygame.image.load(loader.filepath("ui_images/scroll002.png")), (400, 300)
    )
    scroll_image3 = pygame.transform.scale(
        pygame.image.load(loader.filepath("ui_images/scroll003.png")), (400, 300)
    )
    scroll_image4 = pygame.transform.scale(
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
    pop_icon = pygame.transform.scale(pygame.image.load(loader.filepath("pop_icon.png")), (40, 40))
    territory_icon = pygame.transform.scale(
        pygame.image.load(loader.filepath("territory_icon.png")), (40, 40)
    )


class Icons:
    names = ["advisor", "bee", "beetle", "cockroach", "explorer", "worker", "soldier"]
    images = {}

    for name in names:
        images[name] = scale_image(pygame.image.load(loader.filepath(f"advisors/{name}.png")), 4)

    @staticmethod
    def get_image(name):
        return Icons.images[name]


def impacts_to_html(outcome):
    orig_outcome = outcome
    outcome = [str(i) for i in outcome]
    outcome = ["+" + i if int(i) > 0 else i for i in outcome]
    outcome = [
        f"<font color='#FF0000'>{i}</font>" if int(i) < 0 else f"<font color='#00FF00'>{i}</font>"
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
        self.text_impacted = False
        self.impacts = [0, 0, 0]  # food, population, territory

        self.next_event = "_"  # needed for common interface with decisions
        self.advisor_name = "advisor"

    def ready(self):
        # self.manager = pygame_gui.UIManager((1280, 720), loader.filepath("theme.json"))
        self.manager = pygame_gui.UIManager((1280, 720))
        self.finished = False

        self.button_ext_background = more_elements.ImageBox(Images.button_ext_image, (50, 150))
        self.button_ext_background.visible = False
        self.button_background = more_elements.ImageBox(Images.button_scroll_image, (50, 200))
        self.button_background.visible = False
        self.background_image = more_elements.ImageBox(Images.scroll_image1, (15, 150))
        self.advisor_image = more_elements.ImageBox(Icons.get_image(self.advisor_name), (180, 145))

        self.image_group = more_elements.Group(
            self.button_background,
            self.button_ext_background,
            self.background_image,
            self.advisor_image,
        )

        self.textbox = pygame_gui.elements.UITextBox(
            manager=self.manager,
            relative_rect=pygame.Rect(50, 175, 300, 200),
            html_text="",
        )

        self.animation_stage = 1
        self.animation_stages = 5
        self.animation_time = 0
        self.animation_flip_time = 0.1

        self._ready()

    def _ready(self):
        self.apply_impact(self.impacts)
        if not self.text_impacted:
            html, icons = impacts_to_html(self.impacts)
            self.text += html
            self.text_impacted = True

        self.next_button = None

    def create_buttons(self):
        self.next_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(50, 400, 300, 40),
            text="Next",
            manager=self.manager,
        )

    def display(self, time_delta):
        self.image_group.draw(pygame.display.get_surface())

        self.animation_time += time_delta
        if self.animation_stage < self.animation_stages:
            if self.animation_time > self.animation_flip_time:
                self.animation_time = 0
                self.animation_stage += 1
                if self.animation_stage < self.animation_stages:
                    self.background_image.image = getattr(
                        Images, f"scroll_image{self.animation_stage}"
                    )
                if self.animation_stage == self.animation_stages - 1:
                    self.textbox.html_text = self.text
                    self.textbox.rebuild()
                if self.animation_stage == self.animation_stages:
                    self.button_ext_background.visible = True
                    self.button_background.visible = True
                    self.create_buttons()

        self.manager.update(time_delta)
        self.manager.draw_ui(pygame.display.get_surface())

        return self.finished

    def process_events(self, event):
        self.manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.next_button:
                self.finished = True

    def apply_impact(self, impact):
        Resources.instance.food += impact[0]
        Resources.instance.population += impact[1]
        Resources.instance.territory += impact[2]


class Decision(Event):
    def __init__(self, name):
        super().__init__(name)

        self.hook = True  # if decision is the beginning of a series of events/decisions

        self.options = ["choice 1", "choice 2", "choice 3"]
        self.outcomes = ["this happened", "that happened", "something else"]
        self.impacts = [
            [1, 1, 1],
            [0, 0, 0],
            [0, 0, 0],
        ]  # [food, population, territory]
        self.leads_to = ["_", "_", "_"]  # _ means no following event

    def _ready(self):
        self.decision_buttons = []
        self.next_button = None

    def create_buttons(self):
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

        self.button_background.set_position(pygame.Rect(50, cumulative_height - 250, 300, 300))
        self.button_ext_background.set_position(
            pygame.Rect(50, max(cumulative_height - 550, 150), 300, 300)
        )

    def process_events(self, event):
        super().process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element in self.decision_buttons:
                user_choice = self.decision_buttons.index(event.ui_element)

                self.textbox.html_text = self.outcomes[user_choice]
                html, icons = impacts_to_html(self.impacts[user_choice])
                self.textbox.html_text += html
                self.textbox.rebuild()

                self.apply_impact(self.impacts[user_choice])

                for button in self.decision_buttons:
                    button.kill()

                self.button_background.set_position(pygame.Rect(50, 200, 300, 300))

                self.next_button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(50, 400, 300, 40),
                    text="Next",
                    manager=self.manager,
                )

                self.next_event = self.leads_to[user_choice]


class Quest(Decision):
    def _quest_init(self):  # called special in the quest loader
        self.prereqs = [0, 0, 0]  # food, population, territory
        self.newspaper_lines = [
            "_",
            "_",
            "_",
        ]  # line that gets put into the newspaper queue
        self.is_headline = False  # if newspaper line is meant to be headline

        self.endgame_image = None

    def process_events(self, event):
        super().process_events(event)

        # prevents an error when all of a quest's options leads to another event
        if self.next_event in self.leads_to:
            self.chosen_line = self.newspaper_lines[self.leads_to.index(self.next_event)]

    def display(self, time_delta):
        var = super().display(time_delta)

        if var and self.endgame_image:
            popups.Towns.current_town = popups.Towns.get_image(self.endgame_image)

        return var

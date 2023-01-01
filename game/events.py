import pygame
import pygame_gui

from game import loader, more_elements, popups
from game.popups import scale_image
from game.resources import Resources


class Images:
    scroll_images = [
        pygame.transform.scale(
            pygame.image.load(loader.filepath(f"ui_images/scroll00{i}.png")), (400, 300)
        )
        for i in range(5)
    ]
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
    str_outcome = [
        f"<font color='#00FF00'>{'+' + str(i)}</font>" if i > 0 else 
        f"<font color='#FF0000'>{i}</font>" 
        for i in outcome
    ]
    labels = [
        "<font color='#FFFF00'>food</font>",
        "<font color='#FF00FF'>population</font>",
        "<font color='#00FFFF'>territory</font>"
    ]
    out = (
        f"<br>{s} {label}" 
        for s, label, val in zip(str_outcome, labels, outcome)
        if val != 0
    )

    return "".join(out)


class Scroll:
    def __init__(self, manager: pygame_gui.UIManager, main_text: str, advisor_name: str):
        self.manager = manager
        self.text = main_text

        self.finished = False
        self.scroll_index = 0
        self.flip_time = 0.1  # time between frames
        self.animation_timer = 0

        self.background = more_elements.ImageBox(Images.scroll_images[0], (15, 150))
        self.button_background = more_elements.ImageBox(Images.button_scroll_image, (50, 200))
        self.button_background.visible = False
        self.button_ext_background = more_elements.ImageBox(Images.button_ext_image, (50, 150))
        self.button_ext_background.visible = False
        self.advisor_image = more_elements.ImageBox(Icons.get_image(advisor_name), (180, 145))

        self.image_group = more_elements.Group(
            self.button_background,
            self.button_ext_background,
            self.background,
            self.advisor_image,
        ) 

        self.textbox = pygame_gui.elements.UITextBox(
            manager=self.manager,
            relative_rect=pygame.Rect(50, 175, 300, 200),
            html_text="",
        )

    def display(self, time_delta):
        self.image_group.draw(pygame.display.get_surface())

        # updating scroll animation
        self.animation_timer += time_delta
        if not self.finished and self.animation_timer > self.flip_time:
            self.animation_timer = 0
            if self.scroll_index < len(Images.scroll_images) - 1:
                self.scroll_index += 1
                self.background.image = Images.scroll_images[self.scroll_index]
            # if scroll animation finished, make bottom of scroll visible
            else:
                self.finished = True
                self.set_text(self.text)
                self.button_ext_background.visible = True
                self.button_background.visible = True

        self.manager.update(time_delta)
        self.manager.draw_ui(pygame.display.get_surface())

        return self.finished

    def set_text(self, text):
        self.textbox.html_text = text
        self.textbox.rebuild()



class Event:
    def __init__(self, name):
        self.name = name

        self.text = "text"
        self.text_impacted = False
        self.impacts = [0, 0, 0]  # food, population, territory

        self.next_event = "_"  # needed for common interface with decisions
        self.advisor_name = "advisor"

        self.quest = False

    def ready(self):
        self.manager = pygame_gui.UIManager((1280, 720), loader.filepath("theme.json"))
        self.finished = False

        self.apply_impact(self.impacts)
        html = impacts_to_html(self.impacts)
        self.text += html

        self.scroll = Scroll(self.manager, self.text, self.advisor_name)
        self.next_button = None

    def create_buttons(self):
        self.next_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(50, 400, 300, 40),
            text="Next",
            manager=self.manager,
        )

    def display(self, time_delta):
        animation_done = self.scroll.display(time_delta)
        if animation_done and self.next_button is None:
            self.create_buttons()

        return self.finished

    def process_events(self, event):
        self.manager.process_events(event)

        if (
            event.type == pygame.USEREVENT and 
            event.user_type == "ui_button_pressed" and 
            event.ui_element == self.next_button
        ):
            self.finished = True

    def apply_impact(self, impact):
        Resources.instance.food += impact[0]
        Resources.instance.population += impact[1]
        Resources.instance.territory += impact[2]

class Decision(Event):
    def __init__(self, name):
        super().__init__(name)

        self.hook = False  # if decision is the beginning of a series of events/decisions
        self.quest = False

        self.options = [] 

    def _ready(self):
        self.decision_buttons = []
        self.next_button = None

    def create_buttons(self):
        self.decision_buttons = []
        cumulative_height = 400
        for option in self.options:
            button = more_elements.TextButton(
                relative_rect=pygame.Rect(50, cumulative_height, 300, 20),
                text=option.text,
                manager=self.manager,
            )
            cumulative_height += button.relative_rect.height + 10
            self.decision_buttons.append(button)

        self.scroll.button_background.set_position(pygame.Rect(50, cumulative_height - 250, 300, 300))
        self.scroll.button_ext_background.set_position(
            pygame.Rect(50, max(cumulative_height - 550, 150), 300, 300)
        )

        # messy solution, want to clarify the event/decision inheritence to avoid this
        self.next_button = ""

    def process_events(self, event):
        super().process_events(event)

        if event.type != pygame.USEREVENT:
            return
        if event.user_type != "ui_button_pressed":
            return
        if event.ui_element not in self.decision_buttons:
            return

        user_choice = self.decision_buttons.index(event.ui_element)
        selected = self.options[user_choice]

        self.scroll.set_text(selected.outcome + impacts_to_html(selected.impacts))

        self.apply_impact(selected.impacts)

        for button in self.decision_buttons:
            button.kill()

        self.scroll.button_background.set_position(pygame.Rect(50, 200, 300, 300))

        self.next_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(50, 400, 300, 40),
            text="Next",
            manager=self.manager,
        )

        self.next_event = selected.leads_to
        self.chosen_line = selected.newspaper

class Option:
    def __init__(self):
        self.text = "text"
        self.outcome = ""
        self.impacts = [0, 0, 0]

        self.leads_to = "_"

        self.newspaper = ""
        self.is_headline = False


class Quest(Decision):
    def _quest_init(self):  # called special in the quest loader
        self.prereqs = [0, 0, 0]  # food, population, territory
        self.newspaper_lines = [
            "_",
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

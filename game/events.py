import pygame
import pygame_gui

from game.resources import Resources
import game.loader as loader

class Images:
    scroll_image = pygame.transform.scale(pygame.image.load(loader.filepath("scroll.png")),(300,200))
    button_scroll_image = pygame.transform.scale(pygame.image.load(loader.filepath("button.png")),(300,300))

class Event:
    def __init__(self, name):
        self.name = name

        self.text = "text"
        self.impact = [0, 0, 0] # food, population, territory

    def ready(self):
        self.manager = pygame_gui.UIManager((1280, 720), loader.filepath('theme.json'))
        
        self.back_buttons = pygame_gui.elements.ui_image.UIImage(
            manager=self.manager,
            relative_rect = pygame.Rect(50, 200, 300, 300),
            image_surface = Images.button_scroll_image,
        )
        self.background_image = pygame_gui.elements.ui_image.UIImage(
            manager=self.manager,
            relative_rect=pygame.Rect(50, 200, 300, 200),
            image_surface=Images.scroll_image,
        )
        
        self.textbox = pygame_gui.elements.ui_text_box.UITextBox(
            manager=self.manager,
            relative_rect=pygame.Rect(80, 215, 250, 170),
            html_text=self.text,
        )

        self.next_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(50, 400, 300, 50),
            text="Next",
            manager=self.manager,
        )

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

                    Resources.instance.food += self.impacts[0]
                    Resources.instance.population += self.impacts[1]
                    Resources.instance.territory += self.impacts[2]


class Decision:
    
    def __init__(self, name):
        self.name = name

        self.text = "text"
        self.options = ["choice 1", "choice 2", "choice 3"]
        self.outcomes = ["this happened", "that happened", "something else"]
        self.impacts = [
            [1, 1, 1],
            [0, 0, 0],
            [0, 0, 0],
        ]  # [food, population, territory]

    def ready(self):
        self.manager = pygame_gui.UIManager((1280, 720), loader.filepath('theme.json'))
        self.back_buttons = pygame_gui.elements.ui_image.UIImage(
            manager=self.manager,
            relative_rect = pygame.Rect(50, 150+len(self.options)*50, 300, 300),
            image_surface = Images.button_scroll_image,
        )
        self.background_image = pygame_gui.elements.ui_image.UIImage(
            manager=self.manager,
            relative_rect=pygame.Rect(50, 200, 300, 200),
            image_surface=Images.scroll_image,
        )
        self.textbox = pygame_gui.elements.ui_text_box.UITextBox(
            manager=self.manager,
            relative_rect=pygame.Rect(80, 215, 250, 170),
            html_text=self.text,
        )
        # self.textbox.background_surf = self.image_surface
        # self.textbox.background_color = (255,0,0,255)
        # self.textbox.formatted_text_block.indexed_styles[0].bg_color = pygame.Color(0,0,0,0)
        # self.textbox.formatted_text_block.redraw_from_chunks(None)
        # self.textbox.full_redraw()
        # print ('\n'.join([str(i)+':'+str(j) for i,j in self.textbox.__dict__.items()]))
        # print (self.textbox.__dict__['formatted_text_block'].__dict__)
        # print (dir(self.textbox.__dict__['formatted_text_block']))
        
        self.decision_buttons = []
        for i, option in enumerate(self.options):
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(100, 400 + 50 * i, 200, 50),
                text=option,
                manager=self.manager,
            )
            self.decision_buttons.append(button)

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
                    self.textbox.rebuild()

                    self._update_resources(user_choice)

                    for button in self.decision_buttons:
                        button.kill()
                    
                    self.back_buttons.set_relative_position(pygame.Rect(50,200,300,300))
                    
                    self.next_button = pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect(50, 400, 300, 50),
                        text="Next",
                        manager=self.manager,
                    )

                if event.ui_element == self.next_button:
                    self.finished = True

    def _update_resources(self, user_choice):
        Resources.instance.food += self.impacts[user_choice][0]
        Resources.instance.population += self.impacts[user_choice][1]
        Resources.instance.territory += self.impacts[user_choice][2]


# placeholder for when it runs out
class NoDecision:
    def display(self, _):
        pass

    def process_events(self, _):
        pass

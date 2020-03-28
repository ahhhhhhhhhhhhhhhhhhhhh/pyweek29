import pygame_gui
import pygame


class TextButton(pygame_gui.elements.UIButton):
    def __init__(self, **kwargs):
        relative_rect = kwargs["relative_rect"]
        html_text = kwargs["html_text"] if "html_text" in kwargs else kwargs["text"]
        manager = kwargs["manager"]

        line_size = relative_rect.height

        self.textbox = pygame_gui.elements.ui_text_box.UITextBox(
            manager=manager, html_text=html_text, relative_rect=relative_rect
        )

        while self.textbox.scroll_bar != None:
            relative_rect.height += line_size
            self.textbox.kill()
            self.textbox = pygame_gui.elements.ui_text_box.UITextBox(
                manager=manager, html_text=html_text, relative_rect=relative_rect
            )

        self.textbox.kill()  # necessary for the final one to be constructed after super().init

        super().__init__(relative_rect=relative_rect, text="", manager=manager)

        self.textbox = pygame_gui.elements.ui_text_box.UITextBox(
            manager=manager, html_text=html_text, relative_rect=relative_rect
        )

    def kill(self):
        super().kill()
        self.textbox.kill()


class ImageBox:
    def __init__(self, image, location):
        self.image = image
        self.location = location
        self.visible = True

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, self.location)

    def set_position(self, new_loc):
        self.location = new_loc.copy()


class Group:
    def __init__(self, *args):
        self.elements = list(args)

    def draw(self, screen):
        for element in self.elements:
            element.draw(screen)

'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "game"
package.
'''

import pygame

import pygame_gui

from game import loader

width, height = [1280, 720]
bgcolor = (230,30,70)

def main():
    print("Hello from your game's main()")
    print(loader.load('sample.txt').read())
    
    pygame.init()

    pygame.display.set_caption("Amazing Game 10/10") #changes name of pygame window

    screen = pygame.display.set_mode((width,height))
    clock = pygame.time.Clock()

    manager = pygame_gui.UIManager((width, height))

    test_label = pygame_gui.elements.UILabel(relative_rect = pygame.Rect(50,50,300,30),
                                             text = "Hello world",
                                             manager = manager)
    
    test_button = pygame_gui.elements.UIButton(relative_rect = pygame.Rect(500,500,100,30),
                                               text = "Click me",
                                               manager = manager)

    textbox = pygame_gui.elements.ui_text_box.UITextBox(html_text = "oh boy a text box. there's so much room for activites",
                                                        relative_rect = pygame.Rect(50, 200, 200, 200),
                                                        manager = manager)
    textbox.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)

    refresh_textbox_button = pygame_gui.elements.UIButton(relative_rect = pygame.Rect(50,420,200,30),
                                                           text = "refresh text box",
                                                           manager = manager)

    while True:
        time_delta = clock.tick(60) / 1000
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.USEREVENT:
                if event.user_type == "ui_button_pressed":
                    if event.ui_element == test_button:
                        print("button clicked my dudes")
                    if event.ui_element == refresh_textbox_button:
                        textbox.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)

            manager.process_events(event)

        manager.update(time_delta)

        screen.fill(bgcolor)
        
        manager.draw_ui(screen)
        
        pygame.display.flip()

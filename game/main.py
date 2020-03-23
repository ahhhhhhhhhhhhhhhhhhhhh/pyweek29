'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "game"
package.
'''

import pygame
import os

import pygame_gui

from game import loader
from game import events


width, height = [1280, 720]
bgcolor = (230,30,70)


def main():
    print("Hello from your game's main()")
    print(loader.load('sample.txt').read())
    
    pygame.init()

    pygame.display.set_caption("Amazing Game 10/10") #changes name of pygame window

    screen = pygame.display.set_mode((width,height))
    clock = pygame.time.Clock()

    #imported after pygame.init, which is crucial for this one
    from game import popups

    manager = pygame_gui.UIManager((width, height))

    n = popups.Newspaper("Ant Colony Overruns Granary! City Officials Scramble.")


    food = 50
    population = 50
    territory = 50

    food_display = pygame_gui.elements.UILabel(manager = manager,
                                                relative_rect = pygame.Rect(20,20,150,25),
                                                text = "Food: " + str(food))
    population_display = pygame_gui.elements.UILabel(manager = manager,
                                                relative_rect = pygame.Rect(20,50,150,25),
                                                text = "Population: " + str(population))
    territory_display = pygame_gui.elements.UILabel(manager = manager,
                                                relative_rect = pygame.Rect(20,80,150,25),
                                                text = "Territory: " + str(territory))
    updateResourceDisplay(food, food_display, population, population_display, territory, territory_display)



    decision_textbox = pygame_gui.elements.ui_text_box.UITextBox(manager = manager,
                                                                relative_rect = pygame.Rect(50,200,300,200),
                                                                html_text = "*decision text*")
    decision_buttons = []
    next_decision_button = pygame_gui.elements.UIButton(manager = manager,
                                                        relative_rect = pygame.Rect(50,600,300,50),
                                                        text = "Next")
    next_decision_button.disable()

    #example decisions
    theft_decision = events.Decision("theft")
    theft_decision.text = "An ant was found stealing from the colony's food supply! How do you respond?"
    theft_decision.options = ["Banish the ant", "Do nothing"]
    theft_decision.outcomes = ["Angry at your decision, several of the banished ant's friends leave with them", "Seeing there are no conequences, more ants begin to steal food"]
    theft_decision.impacts = [[0,-5,0],[-10,0,0]]

    war_decision = events.Decision("war")
    war_decision.text = "The beetles have been encroaching on your territory recently. Should we go to war to teach them a lesson?"
    war_decision.options = ["Yes, war!", "No, peace"]
    war_decision.outcomes = ["Your soldiers attack the beetles, sucessfully pushing them back and gaining territory. You do face some losses though", "The beetles continue to take your land"]
    war_decision.impacts = [[0,5,-10],[0,-20,0]]

    decision_queue = [theft_decision, war_decision]


    current_decision = decision_queue.pop(0)
    displayDecision(manager, decision_textbox, decision_buttons, current_decision)


    while True:
        time_delta = clock.tick(60) / 1000
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.USEREVENT:
                if event.user_type == "ui_button_pressed":
                    if event.ui_element in decision_buttons:
                        user_choice = decision_buttons.index(event.ui_element)

                        displayOutcome(decision_textbox, decision_buttons, current_decision, user_choice)

                        food += current_decision.impacts[user_choice][0]
                        population += current_decision.impacts[user_choice][1]
                        territory += current_decision.impacts[user_choice][2]

                        updateResourceDisplay(food, food_display, population, population_display, territory, territory_display)  

                        next_decision_button.enable()

                    if event.ui_element == next_decision_button:
                        if len(decision_queue) > 0:
                            current_decision = decision_queue.pop(0)  
                            displayDecision(manager, decision_textbox, decision_buttons, current_decision)  
                        else:
                            print("no more decisions")         

            manager.process_events(event)

        manager.update(time_delta)

        screen.fill(bgcolor)
        n.display(time_delta)
        
        manager.draw_ui(screen)
        
        pygame.display.flip()


def displayDecision(manager, decision_textbox, decision_buttons, decision):
    decision_textbox.html_text = decision.text
    decision_textbox.rebuild()

    for i,option in enumerate(decision.options):
        button = pygame_gui.elements.UIButton(relative_rect = pygame.Rect(50,400+50*i,300,50),
                                            text = option,
                                            manager = manager)
        decision_buttons.append(button)

def displayOutcome(decision_textbox, decision_buttons, decision, user_choice):
    decision_textbox.html_text = decision.outcomes[user_choice]
    decision_textbox.rebuild()

    for i in range(len(decision_buttons) - 1, -1, -1):
        decision_buttons[i].kill()
        decision_buttons.pop(i)

def updateResourceDisplay(food, food_display, population, population_display, territory, territory_display):
    food_display.set_text("Food: " + str(food))
    food_display.rebuild()
    population_display.set_text("Population: " + str(population))
    population_display.rebuild()
    territory_display.set_text("Territory: " + str(territory))
    territory_display.rebuild()
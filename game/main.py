"""Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "game"
package.
"""

import pygame
import pygame.freetype
import os

import pygame_gui

from game import loader
from game import events
from game import popups
from game.resources import Resources


width, height = [1280, 720]


def main():
    print("Hello from your game's main()")
    print(loader.load("sample.txt").read())

    pygame.init()
    pygame.freetype.init()

    pygame.display.set_caption("Amazing Game 10/10")  # changes name of pygame window

    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    manager = pygame_gui.UIManager((width, height))

    newspaper = popups.Newspaper(
        "Ant Colony Overruns Granary! City Officials Scramble."
    )

    food = 50
    population = 50
    territory = 50

    # creates the Resources object, which can be accessed from anywhere as Resources.instance
    Resources(manager, food, population, territory)

    # example decisions
    theft_decision = events.Decision("theft")
    theft_decision.text = (
        "An ant was found stealing from the colony's food supply! How do you respond?"
    )
    theft_decision.options = ["Banish the ant", "Do nothing"]
    theft_decision.outcomes = [
        "Angry at your decision, several of the banished ant's friends leave with them",
        "Seeing there are no conequences, more ants begin to steal food",
    ]
    theft_decision.impacts = [[0, -5, 0], [-10, 0, 0]]

    war_decision = events.Decision("war")
    war_decision.text = "The beetles have been encroaching on your territory recently. Should we go to war to teach them a lesson?"
    war_decision.options = ["Yes, war!", "No, peace"]
    war_decision.outcomes = [
        "Your soldiers attack the beetles, sucessfully pushing them back and gaining territory. You do face some losses though",
        "The beetles continue to take your land",
    ]
    war_decision.impacts = [[0, -10, 5], [0, 0, -20]]


    #example events
    spoiled_food_event = events.Event("spoiled food")
    spoiled_food_event.text = (
        "Some food in storage has spoiled!"
    )
    spoiled_food_event.impacts = [-5, 0, 0]
    spoiled_food_event.ready()

    new_land_event = events.Event("new land")
    new_land_event.text = (
        "Your scouts have found some new uninhabited land!"
    )
    new_land_event.impacts = [0, 0, 5]
    new_land_event.ready()

    event_queue = [newspaper, war_decision, new_land_event, spoiled_food_event, newspaper, theft_decision, new_land_event]

    current_decision = event_queue.pop(0)
    current_decision.ready()

    bg = pygame.image.load (loader.filepath("Queen's room.png"))
    bg = pygame.transform.scale(bg,(1280,720))
    while True:
        time_delta = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.USEREVENT:
                pass

            manager.process_events(event)
            current_decision.process_events(event)

        manager.update(time_delta)

        screen.blit(bg,(0,0))

        if current_decision.display(time_delta):
            if len(event_queue) > 0:
                current_decision = event_queue.pop(0)
                current_decision.ready()
            else:
                current_decision = events.NoDecision()
                print("no more decisions")

        manager.draw_ui(screen)

        pygame.display.flip()

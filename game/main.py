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

    all_events = loadEvents("events.txt")

    all_decisions = loadDecisions("decisions.txt")

    event_queue = [all_events[0], all_events[1], all_decisions[0], newspaper, all_decisions[1]]

    current_decision = event_queue.pop(0)
    current_decision.ready()

    bg = pygame.image.load(loader.filepath("Queen's room.png"))
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

def loadEvents(filename):
    file = loader.load(filename).readlines()
    file = [line.rstrip().decode() for line in file]
    
    all_events = []

    i = 0
    while i < len(file):
        line = file[i]
        if len(line) > 0 and line[0] == "#":
            event = events.Event("".join(line[1:]))
            event.text = file[i + 1]
            event.impacts = [int(i) for i in file[i + 2].split(",")]

            all_events.append(event)

            i += 2

        i += 1

    return all_events

def loadDecisions(filename):
    file = loader.load(filename).readlines()
    file = [line.rstrip().decode() for line in file]

    all_decisions = []

    i = 0
    while i < len(file):
        line = file[i]
        if len(line) > 0 and line[0] == "#":
            event = events.Decision("".join(line[1:]))
            event.text = file[i + 1]

            event.options = []
            event.impacts = []
            event.outcomes = []

            num_choices = int(file[i + 2])
            for choice in range(num_choices):
                event.options.append(file[i + 3 + choice * 3])
                event.outcomes.append(file[i + 4 + choice * 3])
                event.impacts.append([int(i) for i in file[i + 5 + choice * 3].split(",")])

            all_decisions.append(event)

            i += 2 + num_choices * 3

        i += 1

    return all_decisions



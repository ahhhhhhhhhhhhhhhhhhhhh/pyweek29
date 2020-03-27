import pygame
import pygame.freetype
import os
import random

import pygame_gui

from game import loader
from game import events
from game import popups
from game.sound import SoundManager
from game.resources import Resources

width, height = [1280, 720]


def main():
    pygame.init()
    pygame.freetype.init()
    pygame.mixer.init(buffer=512)

    pygame.display.set_caption("Queen of the Hill")  # changes name of pygame window

    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    manager = pygame_gui.UIManager((width, height), loader.filepath("theme.json"))

    backgrounds = []
    for i in range(1, 18):
        im = pygame.image.load(loader.filepath(f"queen_animation/QR{i}.png"))
        im = pygame.transform.scale(im, (1280, 720))
        im.set_colorkey((167, 255, 255))
        im = im.convert_alpha()
        backgrounds.append(im)

    bg_flip_time = 0.1
    bg_pos = 0
    bg_current_time = 0

    town_im = pygame.Surface((260, 172))  # placeholder for now
    town_im.fill((230, 30, 70))

    SoundManager(manager, width, height)

    normal_headlines = loader.loadHeadlines("headlines.txt")
    headlines_queue = (
        []
    )  # list of tuples: (string of newspaper line, boolean is headline)
    newspaper = popups.Newspaper(
        getRandHeadline(normal_headlines),
        getRandHeadline(normal_headlines),
        getRandHeadline(normal_headlines),
        getRandHeadline(normal_headlines),
    )

    food = 50
    population = 50
    territory = 50

    # creates the Resources object, which can be accessed from anywhere as Resources.instance
    Resources(food, population, territory)

    all_events = loader.loadEvents("events.txt")

    all_decisions = loader.loadDecisions("decisions.txt")

    decision_hooks = [decision for decision in all_decisions if decision.hook]

    all_quests = loader.loadQuests("quests.txt")

    quest_hooks = [quest for quest in all_quests if quest.decision.hook]

    # dict of event names to event to easily reference events
    find_event = {}
    for event in all_events + all_decisions + all_quests:
        find_event[event.name] = event

    # manually inputting newspaper headlines
    find_event["explore2"].newspaper_lines = [
        "local grain silo infested with ants",
        "local grain silo infested with ants",
        "_",
    ]
    find_event["explore3"].newspaper_lines = [
        "farmers report a state-wide grain shortage, blame ants",
        "farmers report a state-wide grain shortage, blame ants",
    ]
    find_event["explore4"].newspaper_lines = [
        "experts say grain shortage key cause in lagging war effort"
    ]

    event_queue = [
        getRandDecision(all_decisions, decision_hooks),
        getRandDecision(all_decisions, decision_hooks),
        getRandElement(all_events),
        getRandElement(quest_hooks),
        getRandElement(all_events),
        newspaper,
    ]

    current_decision = event_queue.pop(0)
    # current_decision = popups.EndScreen() #Uncomment start of line to test endgame object
    current_decision.ready()

    event_num = 0  # number of events processed

    while True:
        time_delta = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.USEREVENT:
                pass

            manager.process_events(event)
            Resources.instance.manager.process_events(event)
            SoundManager.instance.process_events(event)
            current_decision.process_events(event)

        manager.update(time_delta)
        Resources.instance.manager.update(time_delta)

        screen.blit(town_im, (928, 52))

        bg_current_time += time_delta
        if bg_current_time > bg_flip_time:
            bg_current_time = 0
            bg_pos += 1
            bg_pos %= len(backgrounds)

        screen.blit(backgrounds[bg_pos], (0, 0))

        Resources.instance.manager.draw_ui(screen)

        if current_decision.display(time_delta):
            event_num += 1

            if isinstance(current_decision, events.Quest):
                print("quest:", current_decision.name)
                if current_decision.chosen_line != "_":
                    headlines_queue.append(
                        (current_decision.chosen_line, current_decision.is_headline)
                    )

            if current_decision.next_event != "_":
                next_event = find_event[current_decision.next_event]
                event_queue.append(next_event)

            if (
                event_num % 3 == 0
            ):  # so that resource control events don't happen for a bunch of turns in a row
                if Resources.instance.population < 20:
                    event_queue.insert(0, find_event["low population"])
                elif (
                    Resources.instance.territory < Resources.instance.population - 10
                ):  # elif statements so multiple resource control events don't happen at once
                    event_queue.insert(0, find_event["low territory"])
                elif Resources.instance.food > Resources.instance.population + 20:
                    if Resources.instance.population < Resources.instance.territory:
                        event_queue.insert(0, find_event["food surplus population"])
                    else:
                        event_queue.insert(0, find_event["food surplus territory"])

            current_decision = event_queue.pop(0)
            current_decision.ready()

            if isinstance(current_decision, popups.Newspaper):
                while len(event_queue) < 5:
                    rand = random.randrange(100)
                    if rand < 65:
                        event_queue.append(
                            getRandDecision(all_decisions, decision_hooks)
                        )
                    else:
                        event_queue.append(getRandElement(all_events))

                # event_queue.append(getRandElement(quest_hooks))

                current_decision = generateNewspaper(headlines_queue, normal_headlines)
                current_decision.ready()

                event_queue.append(newspaper)

        manager.draw_ui(screen)

        pygame.display.flip()


def getRandElement(lst):
    return lst[random.randrange(0, len(lst))]


# make sure all decisions get cycled through before repeats
def getRandDecision(all_decisions, decision_hooks):
    if len(decision_hooks) == 0:
        decision_hooks = [decision for decision in all_decisions if decision.hook]
    return decision_hooks.pop(random.randrange(0, len(decision_hooks)))


# headlines also get cycled through
def getRandHeadline(normal_headlines):
    if len(normal_headlines) == 0:
        normal_headlines = loader.loadHeadlines("headlines.txt")
    return normal_headlines.pop(random.randrange(len(normal_headlines)))


def generateNewspaper(headlines_queue, normal_headlines):
    if len(headlines_queue) > 0:
        data = headlines_queue.pop(0)
        if data[1]:  # means queue fills headline
            newspaper = popups.Newspaper(
                data[0],
                getRandHeadline(normal_headlines),
                getRandHeadline(normal_headlines),
                getRandHeadline(normal_headlines),
            )
        else:
            newspaper = popups.Newspaper(
                getRandHeadline(normal_headlines),
                data[0],
                getRandHeadline(normal_headlines),
                getRandHeadline(normal_headlines),
            )
    else:
        newspaper = popups.Newspaper(
            getRandHeadline(normal_headlines),
            getRandHeadline(normal_headlines),
            getRandHeadline(normal_headlines),
            getRandHeadline(normal_headlines),
        )

    return newspaper

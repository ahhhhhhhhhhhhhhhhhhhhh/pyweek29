import os
import random

import pygame
import pygame.freetype
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
    pygame.display.set_icon(pygame.image.load(loader.filepath("icon.png")))

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

    eyes = pygame.image.load(loader.filepath(f"eyes.png"))
    eyes = pygame.transform.scale(eyes, (40, 8))
    eyes = eyes.convert_alpha()

    town_im = popups.Towns.get_image("default")

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
    all_quests = loader.loadQuests("quests.txt")
    all_endgames = []  # placeholder

    decision_hooks = [decision for decision in all_decisions if decision.hook]
    quest_hooks = [quest for quest in all_quests if quest.hook]

    # dict of event names to event to easily reference events
    find_event = {}
    for event in all_events + all_decisions + all_quests + all_endgames:
        find_event[event.name] = event

    #setting up endgames
    find_event["bee endgame"] = popups.EndgameScreen("bee endgame")
    find_event["bee endgame"].town = "bee"
    find_event["bee endgame"].message = "You did it! Human civilization is no longer. The bees, aided by the technology created in your joint labs, spread accross the Earth, building a new kind of civilization. The era of humans has ended. All because of a small trade route, and a partnership, between a bee hive and an inisigificant ant colony."

    find_event["explore endgame"] = popups.EndgameScreen("explore endgame")
    find_event["explore endgame"].town = "destroyed"
    find_event["explore endgame"].message = "After their surrender, rouge government officials chose to launch nuclear weapons against their enemies, destroying human society as we know it. All because of a food shortage stemming from an insignificant ant colony."
    
    find_event["ant takeover endgame"] = popups.EndgameScreen("ant takeover endgame")
    find_event["ant takeover endgame"].town = "ant"
    find_event["ant takeover endgame"].message = "When those lone explorers ventured into the mysterious concrete building, they were mutated into a new form of ant, one that was destined to rule the world. From this insignificant ant colony came the most sophisticated society known to earth."
    
    find_event["superhero endgame"] = popups.EndgameScreen("superhero endgame")
    find_event["superhero endgame"].town = "superhero"
    find_event["superhero endgame"].message = "Who knew that the ants that ventured into the mysterious concrete building were actually entering a nuclear power plant, and the radiation that the absorbed would later be transferred to a human, to create the next superhero, ManAnt. Now humanity is safe from threats of any kind as ManAnt protects the race from destruction."
    
    find_event["democracy endgame"] = popups.EndgameScreen("democracy endgame")
    find_event["democracy endgame"].town = "future"
    find_event["democracy endgame"].message = "Inspired by a book about a function democracy found in an ant colony, countries around the world opened their governments to the people, becoming more transparent, fair, and championing democratic ideals. This led to an unprecedented era of productivity, scientific breakthrough, and happiness. The Eath has truly become a utopia, all thanks to the actions of a seemengly insigificant ant colony"
    
    #checks to made sure all leads from all decisions exist
    for item in [*all_decisions, *all_quests]:
        leads = item.leads_to
        actual_leads = []  # needs preprocessing because of the new multi lead things
        for next_item in leads:
            if next_item.count(","):
                actual_leads += next_item.split(",")
            else:
                actual_leads.append(next_item)

        for next_item in actual_leads:
            if next_item != "_":
                if next_item not in find_event:
                    raise ValueError(f"The story item {item.name} leads to nonexistent item {next_item}")

    print("Verified story item integrity")

    # manually inputting newspaper headlines
    find_event["explore2"].newspaper_lines = [
        "local grain silo infested with ants",
        "local grain silo infested with ants",
        "_",
    ]
    find_event["explore3"].newspaper_lines = [
        "farmers report a state-wide grain shortage, blame ants",
        "farmers report a state-wide grain shortage, blame ants"
    ]
    find_event["explore4"].newspaper_lines = [
        "Experts Say Grain Shortage Key Cause In Mariposa's Lagging War Effort"
    ]
    find_event["explore5"].newspaper_lines = [
        "Government insiders say surrender imminent, Mariposa cannot continue war given food shortage"
    ]
    find_event["explore5"].is_headline = True
    find_event["explore6"].newspaper_lines = [
        "Mariposa capitulates, government leaders flee, nuclear weapons missing"
    ]
    find_event["explore6"].is_headline = True

    find_event["bees4"].newspaper_lines = [
        "local zoologist reports unprecedented levels of bee, ant cooperation",
        "_",
    ]
    find_event["bees5"].newspaper_lines = [
        'local zoologist finds ants and bees living together: "completely unprecedented"'
    ]
    find_event["bees6"].newspaper_lines = [
        'experts report local ants, bees seem "way, way too smart"'
    ]
    find_event["bees7"].newspaper_lines = [
        "local villagers flee after bee attack, become laughingstock of nation"
    ]
    find_event["bees7"].is_headline = True
    find_event["bees8"].newspaper_lines = [
        "Military Mobalizes Against New Insect Threat, Say Venom \"Is Like Nothing We've Ever Seen\""
    ]
    find_event["bees8"].is_headline = True

    find_event["radioactive-explore"].newspaper_lines = [
        "nuclear power plant infested with ants",
        "scientists worry about enviromental impact of local nuclear plant",
    ]
    find_event["radioactive-ant"].newspaper_lines = [
        "reports of abnormally large ants scare residents",
        "_",
    ]
    find_event["radioactive-ant2"].newspaper_lines = [
        "have radioactive ants created the next superhero? exclusive interview with ManAnt",
        "have radioactive ants created the next superhero? exclusive interview with ManAnt",
    ]
    find_event["radioactive-ant2"].is_headline = True
    find_event["radioactive-ant3"].newspaper_lines = [
        "experts say nation-wide drop in crime due to ManAnt",
    ]
    find_event["radioactive-ant3"].is_headline = True
    find_event["radioactive-colony3"].newspaper_lines = [
        "new 'super ant' discovered in nearby anthill",
        "_",
    ]
    find_event["radioactive-colony4"].newspaper_lines = [
        "'Super Ants' Force Residents Out Of Homes, Evacuation Of Town In Progress",
        "_",
    ]
    find_event["radioactive-colony4"].is_headline = True

    find_event["democracy3"].newspaper_lines = [
        "_",
        "_",
        "scientist discovers ant colony with democratic society",
    ]
    find_event["democracy4"].newspaper_lines = [
        "'Even Ants Can Do It', A Book Written By Steven Herald, The Discoverer Of Ant Democracy",
        "_"
    ]
    find_event["democracy5"].newspaper_lines = [
        "Citizens accross the world are rallying for worldwide democracy, inspired by recent book on ants"
    ]
    find_event["democracy5"].is_headline = True

    # manually inputting endgame images to the end of quest chains
    find_event["bees8"].endgame_image = "bee"
    find_event["explore6"].endgame_image = "destroyed"
    find_event["radioactive-colony3"].endgame_image = "ant"
    find_event["radioactive-ant2"].endgame_image = "superhero"
    find_event["democracy5"].endgame_image = "future"

    # manually inputting advisor icons
    # decisions
    find_event["beetle start"].advisor_name = "beetle"
    find_event["beetle demand"].advisor_name = "beetle"
    find_event["beetle border skirmish"].advisor_name = "beetle"
    find_event["beetle planning"].advisor_name = "beetle"
    find_event["new land"].advisor_name = "explorer"
    find_event["storm"].advisor_name = "worker"
    find_event["refugees"].advisor_name = "explorer"
    find_event["grasshopper"].advisor_name = "explorer"
    find_event["grasshopper variation2"].advisor_name = "explorer"
    find_event["cockroach merchant"].advisor_name = "cockroach"
    find_event["cockroach merchant returns"].advisor_name = "cockroach"
    # events
    find_event["new tunnels"].advisor_name = "worker"
    # quests
    find_event["explore2"].advisor_name = "explorer"
    find_event["explore3"].advisor_name = "explorer"
    find_event["explore4"].advisor_name = "explorer"
    find_event["explore5"].advisor_name = "explorer"
    find_event["explore6"].advisor_name = "explorer"

    find_event["bees"].advisor_name = "bee"
    find_event["bees2"].advisor_name = "bee"
    find_event["bees3 a"].advisor_name = "bee"
    find_event["bees3 b"].advisor_name = "bee"
    find_event["bees4"].advisor_name = "bee"
    find_event["bees5"].advisor_name = "bee"
    find_event["bees6"].advisor_name = "bee"
    find_event["bees7"].advisor_name = "bee"
    find_event["bees8"].advisor_name = "bee"

    find_event["radioactive-discover"].advisor_name = "explorer"
    find_event["radioactive-wait"].advisor_name = "explorer"
    find_event["radioactive-explore"].advisor_name = "explorer"
    find_event["radioactive-ant"].advisor_name = "explorer"
    find_event["radioactive-ant2"].advisor_name = "explorer"
    find_event["radioactive-colony"].advisor_name = "explorer"
    find_event["radioactive-colony2"].advisor_name = "explorer"
    find_event["radioactive-colony3"].advisor_name = "explorer"
    find_event["radioactive-colony4"].advisor_name = "explorer"
    
    
    event_queue = [
        getRandDecision(all_decisions, decision_hooks),
        getRandDecision(all_decisions, decision_hooks),
        getRandElement(all_events),
        #getRandDecision(all_quests, quest_hooks),
        getRandElement(all_events),
        newspaper,
    ]
    
    print (event_queue[3].name)
    
    quest_queue = []  # specific queue for quest events

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

        screen.blit(popups.Towns.current_town, (898, 48))

        bg_current_time += time_delta
        if bg_current_time > bg_flip_time:
            bg_current_time = 0
            bg_pos += 1
            bg_pos %= len(backgrounds)

        screen.blit(backgrounds[bg_pos], (0, 0))
        screen.blit(eyes, (644, 248))

        Resources.instance.manager.draw_ui(screen)

        if current_decision.display(time_delta):
            event_num += 1

            if isinstance(current_decision, events.Quest):
                if current_decision.chosen_line != "_":
                    headlines_queue.append((current_decision.chosen_line, current_decision.is_headline))

                if current_decision.next_event != "_":
                    next_quest = find_event[current_decision.next_event]
                    if isinstance(next_quest, popups.EndgameScreen):
                        event_queue.insert(1, next_quest)
                    else:
                        quest_queue.append(next_quest)

            else:
                next_event_name = current_decision.next_event
                if current_decision.next_event.count(",") > 0:
                    next_event_name = random.choice(
                        current_decision.next_event.split(",")
                    )
                if next_event_name != "_":
                    next_event = find_event[next_event_name]
                    event_queue.append(next_event)

            # resource control trigger
            if event_num % 3 == 0:  # so that resource control events don't happen for a bunch of turns in a row
                if Resources.instance.population < 20:
                    event_queue.insert(0, find_event["low population"])
                elif (Resources.instance.territory < Resources.instance.population - 20):  # elif statements so multiple resource control events don't happen at once
                    event_queue.insert(0, find_event["low territory"])
                elif Resources.instance.food > Resources.instance.population + 20:
                    if Resources.instance.population < Resources.instance.territory:
                        event_queue.insert(0, find_event["food surplus population"])
                    else:
                        event_queue.insert(0, find_event["food surplus territory"])

            if Resources.instance.population <= 0:
                lose_screen = popups.EndScreen()
                lose_screen.message = "Try as you might, your colony simply could not survive. Without any workers, you are forced to flee as your territory is taken over by others."
                event_queue.insert(0, lose_screen)
            elif Resources.instance.territory <= 0:
                lose_screen = popups.EndScreen()
                lose_screen.message = "Try as you might, your colony simply could not survive. Without any territory you can claim on your own, you and your remaining workers are forced to flee the area."
                event_queue.insert(0, lose_screen)
            elif Resources.instance.food <= 0:
                event_queue.insert(0, find_event["starvation"])

            current_decision = event_queue.pop(0)
            #current_decision = popups.EndgameScreen() ###################testing purposes
            current_decision.ready()
            print("now playing event:", current_decision.name)

            if isinstance(current_decision, popups.Newspaper):
                while len(event_queue) < 5:
                    rand = random.randrange(100)
                    if rand < 65:
                        event_queue.append(getRandDecision(all_decisions, decision_hooks))
                    else:
                        event_queue.append(getRandElement(all_events))

                # only adds another quest hook if there is not an ongoing quest
                if len(quest_queue) == 0:
                    event_queue.append(getRandDecision(all_quests, quest_hooks))
                else:
                    event_queue.append(quest_queue.pop(0))

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

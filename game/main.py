import os
import random

import pygame
import pygame.freetype
import pygame_gui

from game import events, loader, popups
from game.resources import Resources
from game.sound import SoundManager

width, height = [1280, 720]


def main():
    pygame.init()
    pygame.freetype.init()
    pygame.mixer.init(buffer=512)

    pygame.display.set_caption("Queen of the Hill")  # changes name of pygame window
    pygame.display.set_icon(pygame.image.load(loader.filepath("icon.png")))

    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    # loading series of background images
    backgrounds = []
    for i in range(1, 18):
        im = pygame.image.load(loader.filepath(f"queen_animation/QR{i}.png"))
        im = pygame.transform.scale(im, (1280, 720))
        im.set_colorkey((167, 255, 255))
        im = im.convert()
        backgrounds.append(im)

    food = 50
    population = 50
    territory = 50

    # creates the Resources object, which can be accessed from anywhere as Resources.instance
    Resources(food, population, territory)

    # loading headlines and events from file
    normal_headlines = loader.load_lines("headlines.txt")

    all_events = loader.load_events("events.txt")
    all_decisions = loader.load_decisions("decisions.txt")
    all_quests = loader.load_decisions("quests.txt")

    # dict of event names to event to easily reference events
    find_event = {}
    for event in all_events + all_decisions + all_quests:
        find_event[event.name] = event

    # hardcoding endgame screens (TODO: incorporate into decision file format)
    setup_endgames(find_event)
    
    # checks to made sure all leads from all decisions exist
    for item in [*all_decisions, *all_quests]:
        leads = [o.leads_to for o in item.options]
        # leads = item.leads_to
        actual_leads = []  # needs preprocessing because of the new multi lead things
        for next_item in leads:
            if next_item.count(","):
                actual_leads += next_item.split(",")
            else:
                actual_leads.append(next_item)

        for next_item in actual_leads:
            if next_item != "_":
                if next_item not in find_event:
                    raise ValueError(
                        f"The story item {item.name} leads to nonexistent item {next_item}"
                    )
    print("Verified story item integrity")

    # with open("fixed_formatting_decisions.txt", "w") as file:
    #     to_write = []
    #     for d in all_decisions:
    #         to_write.append(f"#{d.name}")
    #         if d.hook:
    #             to_write.append("[hook]")
    #         if d.quest:
    #             to_write.append("[quest]")
    #         if d.advisor_name != "advisor":
    #             to_write.append(f"[advisor] {d.advisor_name}")
    #         to_write.append(d.text)
    #         for option in d.options:
    #             to_write.append("[option]")
    #             to_write.append(f"\t{option.text}")
    #             to_write.append(f"\t{option.outcome}")
    #             to_write.append(f"\t{', '.join([str(x) for x in option.impacts])}")
    #             if option.leads_to != "_":
    #                 to_write.append(f"\t[leads_to] {option.leads_to}")
    #             # print(d.newspaper_lines, i)
    #             if option.newspaper != "":
    #                 to_write.append(f"\t[newspaper] {option.newspaper}")
    #             if option.is_headline:
    #                 to_write.append("\t[headline]")

    #         to_write.append("")

    #     file.writelines([l + "\n" for l in to_write])

    global game_scene
    game_scene = GameScene(
        backgrounds, all_events, all_decisions, all_quests, find_event, normal_headlines
    )
    global main_menu
    main_menu = MainMenu()

    # current_scene = game_scene
    current_scene = main_menu

    SoundManager(game_scene.manager, width, height)

    # main game loop
    while True:
        time_delta = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            current_scene = current_scene.process_events(event)

            Resources.instance.manager.process_events(event)
            SoundManager.instance.process_events(event)

        current_scene.draw(screen)

        current_scene.update(time_delta)

        pygame.display.flip()


class MainMenu:
    def __init__(self):
        self.manager = pygame_gui.UIManager((width, height), loader.filepath("theme.json"))

        self.background = popups.Towns.get_image("ant")
        self.background = pygame.transform.scale(self.background, (width, height))

        self.title_text = pygame_gui.elements.UILabel(
            manager=self.manager,
            relative_rect=pygame.Rect(width / 2 - 500, 100, 1000, 200),
            text="Queen of the Hill",
            object_id="main_menu_title",
        )

        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(width / 2 - 100, height / 2 + 200, 200, 100),
            text="Start",
            manager=self.manager,
        )

    def process_events(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.start_button:
                    return game_scene

        self.manager.process_events(event)

        return self

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        self.manager.draw_ui(screen)

    def update(self, time_delta):
        if game_scene.event_num > 0 and self.start_button.text != "Resume":
            self.start_button.set_text("Resume")

        self.manager.update(time_delta)


class GameScene:
    def __init__(
        self,
        backgrounds,
        all_events,
        all_decisions,
        all_quests,
        find_event,
        normal_headlines,
    ):
        self.manager = pygame_gui.UIManager((width, height), loader.filepath("theme.json"))

        self.all_events = all_events
        self.all_decisions = all_decisions
        self.decision_hooks = [decision for decision in self.all_decisions if decision.hook]
        self.all_quests = all_quests
        self.quest_hooks = [quest for quest in self.all_quests if quest.hook]

        self.find_event = find_event

        self.event_num = 0

        self.bg_current_time = 0
        self.bg_flip_time = 0.1
        self.bg_pos = 0
        self.bgs = backgrounds
        self.bg = self.bgs[self.bg_pos]

        self.event_queue = [
            self.get_rand_decision(),
            self.get_rand_decision(),
            self.get_rand_event(),
            self.get_rand_event(),
        ]
        self.quest_queue = []
        self.current_decision = self.event_queue.pop(0)
        self.current_decision.ready()

        # list of tuples: (string of newspaper line, boolean is headline)
        self.headlines_queue = []
        self.normal_headlines = normal_headlines
        self.event_queue.append(self.generate_newspaper())

    def update(self, time_delta):
        self.manager.update(time_delta)
        self.update_bg(time_delta)

        Resources.instance.manager.update(time_delta)

        done = self.current_decision.display(time_delta)
        if not done:
            return


        self.event_num += 1

        if type(self.current_decision) == events.Decision and self.current_decision.quest:
            if self.current_decision.chosen_line:
                self.headlines_queue.append((self.current_decision.chosen_line, self.current_decision.is_headline))

            if self.current_decision.next_event != "_":
                next_quest = self.find_event[self.current_decision.next_event]
                if isinstance(next_quest, popups.EndgameScreen):
                    self.event_queue.insert(1, next_quest)
                else:
                    self.quest_queue.append(next_quest)

        else:
            next_event_name = self.current_decision.next_event
            if self.current_decision.next_event.count(",") > 0:
                next_event_name = random.choice(self.current_decision.next_event.split(","))
            if next_event_name != "_":
                next_event = self.find_event[next_event_name]
                self.event_queue.append(next_event)

        # resource control trigger
        # so that resource control events don't happen for a bunch of turns in a row
        if self.event_num % 3 == 0:
            if Resources.instance.population < 20:
                self.event_queue.insert(0, self.find_event["low population"])
            # elif statements so multiple resource control events don't happen at once
            elif Resources.instance.territory < Resources.instance.population - 20:
                self.event_queue.insert(0, self.find_event["low territory"])
            elif Resources.instance.food > Resources.instance.population + 20:
                if Resources.instance.population < Resources.instance.territory:
                    self.event_queue.insert(0, self.find_event["food surplus population"])
                else:
                    self.event_queue.insert(0, self.find_event["food surplus territory"])

        # losing scenarios
        if Resources.instance.population <= 0:
            lose_screen = popups.EndScreen()
            lose_screen.message = "Try as you might, your colony simply could not survive. Without any workers, you are forced to flee as your territory is taken over by others."
            self.event_queue.insert(0, lose_screen)
        elif Resources.instance.territory <= 0:
            lose_screen = popups.EndScreen()
            lose_screen.message = "Try as you might, your colony simply could not survive. Without any territory you can claim on your own, you and your remaining workers are forced to flee the area."
            self.event_queue.insert(0, lose_screen)
        elif Resources.instance.food <= 0:
            self.event_queue.insert(0, self.find_event["starvation"])

        self.current_decision = self.event_queue.pop(0)
        # current_decision = popups.EndgameScreen() ################### testing purposes
        self.current_decision.ready()

        print("now playing event:", self.current_decision.name)
        print("event_queue:", [event.name for event in self.event_queue])

        if isinstance(self.current_decision, popups.Newspaper):
            while len(self.event_queue) < 5:
                rand = random.randrange(100)
                if rand < 65:
                    self.event_queue.append(self.get_rand_decision())
                else:
                    self.event_queue.append(self.get_rand_event())

            # only adds another quest hook if there is not an ongoing quest
            if len(self.quest_queue) == 0:
                self.event_queue.append(self.get_rand_quest())
            else:
                self.event_queue.append(self.quest_queue.pop(0))

            self.event_queue.append(self.generate_newspaper())

    def process_events(self, event):
        # ESC key exits to main menu
        if event.type == pygame.KEYDOWN and event.key == 27:
            return main_menu

        self.manager.process_events(event)
        self.current_decision.process_events(event)

        return self

    def draw(self, screen):
        # drawing town image behind window
        screen.blit(popups.Towns.current_town, (898, 48))
        screen.blit(self.bg, (0, 0))

        Resources.instance.manager.draw_ui(screen)

        self.manager.draw_ui(screen)

    def update_bg(self, time_delta):
        self.bg_current_time += time_delta
        if self.bg_current_time > self.bg_flip_time:
            self.bg_current_time = 0
            self.bg_pos += 1
            self.bg_pos %= len(self.bgs)

        self.bg = self.bgs[self.bg_pos]

    def get_rand_decision(self):
        if len(self.decision_hooks) == 0:
            self.decision_hooks = [decision for decision in self.all_decisions if decision.hook]
        return self.decision_hooks.pop(random.randrange(0, len(self.decision_hooks)))

    def get_rand_quest(self):
        if len(self.quest_hooks) == 0:
            self.quest_hooks = [quest for quest in self.all_quests if quest.hook]
        return self.quest_hooks.pop(random.randrange(0, len(self.quest_hooks)))

    def get_rand_event(self):
        return self.all_events[random.randrange(0, len(self.all_events))]

    def generate_newspaper(self):
        if len(self.headlines_queue) > 0:
            data = self.headlines_queue.pop(0)
            if data[1]:  # means queue fills headline
                newspaper = popups.Newspaper(
                    data[0],
                    self.get_rand_headline(),
                    self.get_rand_headline(),
                    self.get_rand_headline(),
                )
            else:
                newspaper = popups.Newspaper(
                    self.get_rand_headline(),
                    data[0],
                    self.get_rand_headline(),
                    self.get_rand_headline(),
                )
        else:
            newspaper = popups.Newspaper(
                self.get_rand_headline(),
                self.get_rand_headline(),
                self.get_rand_headline(),
                self.get_rand_headline(),
            )

        return newspaper

    def get_rand_headline(self):
        if len(self.normal_headlines) == 0:
            self.normal_headlines = loader.loadHeadlines("headlines.txt")
        return self.normal_headlines.pop(random.randrange(len(self.normal_headlines)))


def setup_endgames(find_event):
    find_event["bee endgame"] = popups.EndgameScreen("bee endgame")
    find_event["bee endgame"].town = "bee"
    find_event[
        "bee endgame"
    ].message = "You did it! Human civilization is no longer. The bees, aided by the technology created in your joint labs, spread accross the Earth, building a new kind of civilization. The era of humans has ended. All because of a small trade route, and a partnership, between a bee hive and an inisigificant ant colony."

    find_event["explore endgame"] = popups.EndgameScreen("explore endgame")
    find_event["explore endgame"].town = "destroyed"
    find_event[
        "explore endgame"
    ].message = "After their surrender, rogue government officials chose to launch nuclear weapons against their enemies, destroying human society as we know it. All because of a food shortage stemming from an insignificant ant colony."

    find_event["ant takeover endgame"] = popups.EndgameScreen("ant takeover endgame")
    find_event["ant takeover endgame"].town = "ant"
    find_event[
        "ant takeover endgame"
    ].message = "When those lone explorers ventured into the mysterious concrete building, they were mutated into a new form of ant, one that was destined to rule the world. From this insignificant ant colony came the most sophisticated society known to earth."

    find_event["superhero endgame"] = popups.EndgameScreen("superhero endgame")
    find_event["superhero endgame"].town = "superhero"
    find_event[
        "superhero endgame"
    ].message = "Who knew that the ants that ventured into the mysterious concrete building were actually entering a nuclear power plant, and the radiation that the absorbed would later be transferred to a human, to create the next superhero, ManAnt. Now humanity is safe from threats of any kind as ManAnt protects the race from destruction."

    find_event["democracy endgame"] = popups.EndgameScreen("democracy endgame")
    find_event["democracy endgame"].town = "future"
    find_event[
        "democracy endgame"
    ].message = "Inspired by a book about a functioning democracy found in an ant colony, countries around the world opened their governments to the people, becoming more transparent, fair, and championing democratic ideals. This led to an unprecedented era of productivity, scientific breakthrough, and happiness. The Eath has truly become a utopia, all thanks to the actions of a seemengly insigificant ant colony"

    # manually inputting endgame images to the end of quest chains
    find_event["bees8"].endgame_image = "bee"
    find_event["explore6"].endgame_image = "destroyed"
    find_event["radioactive-colony3"].endgame_image = "ant"
    find_event["radioactive-ant2"].endgame_image = "superhero"
    find_event["democracy5"].endgame_image = "future"
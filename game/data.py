
import pickle
import os

from game import loader
from game import events

class Data:
    instance = None

    def __init__(self):
        self.load()

    def save(self, resources, event_queue, quest_queue, current_decision, decision_hooks, quest_hooks, headlines_queue, all_headlines, current_headlines):
        self.food = resources.food
        self.population = resources.population
        self.territory = resources.territory
        self.event_queue = [event.name for event in event_queue]
        self.quest_queue = [event.name for event in quest_queue]
        self.current_decision = current_decision.name
        self.decision_hooks = [event.name for event in decision_hooks]
        self.quest_hooks = [event.name for event in quest_hooks]
        self.headlines_queue = headlines_queue
        self.all_headlines = all_headlines
        self.current_headlines = current_headlines

        pickle.dump(Data.instance, open(loader.filepath("gamedata.txt"), "wb"))
        print("saved gamedata to file")

    def load(self):
        if os.path.exists(loader.filepath("gamedata.txt")):
            Data.instance = pickle.load(open(loader.filepath("gamedata.txt"), "rb"))
            print("loaded gamedata from file")
        else:
            open(loader.filepath("gamedata.txt"), "x")
            print("created gamedata file")

            # default settings
            self.masterVolume = 1
            self.musicVolume = 0.5

            # resources starting values
            self.food = 50
            self.population = 50
            self.territory = 50

            # setting up game variables
            self.event_queue = None
            self.quest_queue = None
            self.current_decision = None
            self.decision_hooks = None
            self.quest_hooks = None
            self.headlines_queue = None
            self.all_headlines = None
            self.current_headlines = None

            pickle.dump(self, open(loader.filepath("gamedata.txt"), "wb"))

            Data.instance = self




import pickle
import os

from game import loader
from game import events

class Data:
    instance = None

    def __init__(self):
        self.load()

    def save(self, resources, event_queue, quest_queue, current_decision):
        self.food = resources.food
        self.population = resources.population
        self.territory = resources.territory
        self.event_queue = [event.name for event in event_queue]
        self.quest_queue = [event.name for event in quest_queue]
        self.current_decision = current_decision.name

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
            self.masterVolume = 0.5
            self.musicVolume = 0.5

            # resources starting values
            self.food = 50
            self.population = 50
            self.territory = 50

            # setting up game variables
            self.event_queue = None
            self.quest_queue = None
            self.current_decision = None

            pickle.dump(self, open(loader.filepath("gamedata.txt"), "wb"))

            Data.instance = self



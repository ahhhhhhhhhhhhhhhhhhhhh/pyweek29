import os
import sys

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, "..", "data"))

if getattr(sys, 'frozen', False):
    data_py = os.path.abspath(os.path.dirname(sys.executable))
    data_dir = os.path.normpath(os.path.join(data_py, "..", "data"))

def filepath(filename):
    """Determine the path to a file in the data directory.
    """
    return os.path.join(data_dir, filename)


def load(filename, mode="rb"):
    return open(os.path.join(data_dir, filename), mode)


from game import events  # so that Images class can use loader.filepath()


def loadEvents(filename):
    file = load(filename).readlines()
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
    print("loaded " + str(len(all_events)) + " events")
    return all_events


def loadDecisions(filename):
    file = load(filename).readlines()
    file = [line.rstrip().decode() for line in file]

    all_decisions = []

    i = 0
    while i < len(file):
        line = file[i]
        if len(line) > 0 and line[0] == "#":
            event = loadDecision(file, i)

            all_decisions.append(event)

            i += 3 + len(event.options) * 4

        i += 1
    print("loaded " + str(len(all_decisions)) + " decisions")
    return all_decisions


def loadDecision(file, i):
    line = file[i]

    event = events.Decision("".join(line[1:]))

    event.hook = file[i + 1].lower() == "true"

    event.text = file[i + 2]

    event.options = []
    event.impacts = []
    event.outcomes = []
    event.leads_to = []

    num_choices = int(file[i + 3])
    for choice in range(num_choices):
        event.options.append(file[i + 4 + choice * 4])
        event.outcomes.append(file[i + 5 + choice * 4])
        event.impacts.append([int(i) for i in file[i + 6 + choice * 4].split(",")])
        event.leads_to.append(file[i + 7 + choice * 4])

    return event


def loadQuests(filename):
    file = load(filename).readlines()
    file = [line.rstrip().decode() for line in file]

    all_quests = []

    i = 0
    while i < len(file):
        line = file[i]
        if len(line) > 0 and line[0] == "#":
            quest = loadDecision(file, i)
            quest.__class__ = events.Quest
            quest._quest_init()

            all_quests.append(quest)

            i += 3 + len(quest.options) * 4

        i += 1
    print("loaded " + str(len(all_quests)) + " quests")
    return all_quests


def loadHeadlines(filename):
    file = load(filename).readlines()
    file = [line.rstrip().decode() for line in file]

    return file

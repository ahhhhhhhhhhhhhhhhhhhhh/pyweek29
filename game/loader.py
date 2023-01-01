import os
import sys

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, "..", "data"))

if getattr(sys, "frozen", False):
    data_py = os.path.abspath(os.path.dirname(sys.executable))
    data_dir = os.path.normpath(os.path.join(data_py, "..", "data"))


def filepath(filename):
    """Determine the path to a file in the data directory."""
    return os.path.join(data_dir, filename)


def load(filename, mode="rb"):
    return open(os.path.join(data_dir, filename), mode)


# so that Images class can use loader.filepath()
from game import events  

def load_lines(filename):
    return [line.rstrip().decode() for line in load(filename).readlines()]

def load_events(filename):
    file = load_lines(filename)
    loaded = []

    i = 0
    while i < len(file):
        line = file[i]
        if len(line) > 0 and line[0] == "#":
            event = events.Event(line[1:])
            event.text = file[i + 1]
            event.impacts = [int(i) for i in file[i + 2].split(",")]

            loaded.append(event)

            i += 2

        i += 1

    print(f"Loaded {len(loaded)} events")
    return loaded

def load_decisions(filename):
    file = load_lines(filename)
    decisions = []

    i = 0
    while i < len(file):
        line = file[i].strip("\t")
        if len(line) > 0 and line[0] == "#":
            d, i = read_decision(file, i)
            decisions.append(d)
        else:
            i += 1

    print(f"Loaded {len(decisions)} decisions")
    return decisions

def read_tag(file, i):
    line = file[i].split()
    assert len(line) > 0
    tag = line[0]
    assert tag[0] == "[" and tag[-1] == "]"
    tag = tag[1:-1]

    return tag, i + 1, line[1:]

def read_decision(file, i):
    d = events.Decision(file[i][1:])

    while i < len(file) and file[i] != "":
        line = file[i].strip("\t")
        if line[0] == "[":
            tag, i, args = read_tag(file, i)

            match tag:
                case "option":
                    option, i = read_option(file, i)
                    d.options.append(option)
                case "hook":
                    d.hook = True
                case "quest":
                    d.quest = True
                case "advisor":
                    d.advisor_name = args[0]
                case _:
                    print("read_decision: unknown tag", tag)
        else:
            d.text = line
            i += 1

    return d, i
        
def read_option(file, i):
    opt = events.Option()
    opt.text = file[i].strip("\t")
    opt.outcome = file[i + 1].strip("\t")
    opt.impacts = [int(n) for n in file[i + 2].split(",")]
    i += 3

    while i < len(file) and file[i] != "":
        tag, i, args = read_tag(file, i)

        match tag:
            case "option":
                return opt, i - 1
            case "leads_to":
                opt.leads_to = " ".join(args)
            case "newspaper":
                opt.newspaper = " ".join(args)
            case "headline":
                opt.is_headline = True
            case _:
                print("read_option: unknown tag", tag)

    return opt, i

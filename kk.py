#!/usr/bin/env python3

# read in command line arguments
from argparse import ArgumentParser

parser = ArgumentParser(
        prog="KK",
        description="A tool that automates the creation of Kris Kringle allocations, respecting user-defined rules.",)
parser.add_argument("filename")
args = parser.parse_args()

# read and parse the schematic
from kk_read import parse, resolve

commands = parse(args.filename)
people, buy, avoid = resolve(commands)

# form the model
from kk_model import make_allocation

allocation = make_allocation(people, buy, avoid)

# display the allocation
unvisited = list(people)
for src in unvisited: # NOTE: this list is modified as the loop progresses, but that isn't a problem here.
    cur = src
    print(f"{cur} -> ", end="")
    nxt = allocation[cur]

    while nxt != src:
        cur = nxt
        print(f"{cur} -> ", end="")
        unvisited.remove(cur)
        nxt = allocation[cur]

    print(src, end="\n\n")

"""
print(sum(1- sol[y[t,p]] for t, allocation in enumerate(history[-1:]) for p in people if p in allocation))
for t, allocation in enumerate(history[-1:]):
    for p in people:
        if p in allocation and sol[y[t,p]] < 0.5:
            print(p)

for g in groups:
    for p in g:
        print(f"{p} -> {allocation[p]}")
    print()"""


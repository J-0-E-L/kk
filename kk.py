#!/usr/bin/env python3

import itertools as it
import random, math
from pyscipopt import Model, quicksum, Conshdlr
from SEC import SEC
import json

sq = lambda A: it.product(A, A)

#random.seed(10)

from kk_read import parse, resolve

commands = parse("abc.kk")
people, buy, avoid = resolve(commands)

#from pprint import pprint
#pprint(people)
#pprint(buy)
#pprint(avoid)

model = Model("Family KK")

# x[p,q] encodes whether p buys for q
x = dict()
for p, q in sq(people):
    x[p,q] = model.addVar(vtype='B', name=f"x_{p}_{q}")

# Everyone gives and recieves exactly one gift
for p in people:
    model.addCons(quicksum(x[q,p] for q in people) == 1, name=f"sum_in_{p}")
    model.addCons(quicksum(x[p,q] for q in people) == 1, name=f"sum_out_{p}")

# "Avoid" constraints
for p in avoid:
    for q in avoid[p]:
        model.addCons(x[p,q] == 0)

# "Buy" constraints
for p in buy:
    for q in people:
        if q not in buy[p]:
            model.addCons(x[p,q] == 0)

# Add in (lazy) subtour elimination constraints
# based on https://pyscipopt.readthedocs.io/en/latest/tutorials/lazycons.html
conshdlr = SEC(len(people) // 3)
#conshdlr = SEC()
model.includeConshdlr(conshdlr, "Bounded TSP", "Eliminate subtours, but allowing those that are longer than a given threshold (omission yields ordinary TSP constraints)", chckpriority=-1, enfopriority=-1)

cons = conshdlr.createCons("no_subtours", x)
model.addPyCons(cons)

model.setObjective(quicksum((random.random()-0.5)*x[p,q] for p,q in sq(people)), sense="maximize")
model.hideOutput() # silence the solver
model.optimize()

sol = model.getBestSol()
allocation = dict()
for p,q in sq(people):
    if sol[x[p,q]] > 0.5:
        allocation[p] = q


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


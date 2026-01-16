#!/usr/bin/env python3

import itertools as it
import random, math
from pyscipopt import Model, quicksum, Conshdlr
from SEC import SEC
import json

sq = lambda A: it.product(A, A)

from kk_read import parse, resolve

def make_allocation(people, buy, avoid, seed=None):
    random.seed(seed)

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

    if model.getStatus() == "infeasible":
        print("No suitable allocation exists for this schematic") # TODO: fix this message
        raise Exception

    sol = model.getBestSol()
    allocation = dict()
    for p,q in sq(people):
        if sol[x[p,q]] > 0.5:
            allocation[p] = q

    return allocation


#!/usr/bin/env python3

# based on https://pyscipopt.readthedocs.io/en/latest/tutorials/lazycons.html

from pyscipopt import quicksum, Conshdlr, SCIP_RESULT
import networkx

class SEC(Conshdlr):
    def __init__(self, min_subtour_length=float("inf")):
        self.min_subtour_length =  min_subtour_length 

    # method for creating a constraint of this constraint handler type
    def createCons(self, name, variables):
        cons = self.model.createCons(self, name)
        # make sure to include the information relevant to this constraint type
        cons.data = {}
        cons.data["vars"] = variables
        return cons
    
    # construct a networkx graph from the current solution
    def build_graph(self, cons, solution=None):
        x = cons.data["vars"]
        G =  networkx.DiGraph()
        for p, q in x.keys():
            # record an edge from p to q if x_p_q is positive
            if self.model.getSolVal(solution, x[p, q]) > 0.5:
                G.add_edge(p, q)

        return G
    
    """
    # returns all subtours in solution ([] if the solution is a Hamiltonian cycle)
    def subtours(self, cons, solution=None):
        G = self.build_graph(cons, solution)
        cycles = list(G.subgraph(g) for g in networkx.weakly_connected_components(G))
        if len(cycles) == 1:
            return []
        return cycles 

    # checks whether solution is feasible w.r.t constraint type (whether it has subtours)
    def conscheck(self, constraints, solution, check_integrality, check_lp_rows, print_reason, completely, **results):
        for cons in constraints:
            if self.subtours(cons, solution):
                return {"result": SCIP_RESULT.INFEASIBLE}

        return {"result": SCIP_RESULT.FEASIBLE}


    # enforces the LP solution: search and block subtours found in the solution
    def consenfolp(self, constraints, n_useful_conss, sol_infeasible):
        consadded = False
        
        for cons in constraints:
            subtours = self.subtours(cons)
            # if subtours exist...
            if subtours:
                x = cons.data["vars"]
                for S in subtours:
                    # ... eliminate them!
                    #print(f"Constraint added: eliminates subtour of length {len(S.nodes)}") 
                    self.model.addCons(quicksum(x[p, q] for p, q in S.edges) <= len(S) - 1)
                    consadded = True

        if consadded:
            return {"result": SCIP_RESULT.CONSADDED}

        return {"result": SCIP_RESULT.FEASIBLE}
    """

    # returns all subtours in solution whose length is less than the allowed threshold ([] if the solution is a Hamiltonian cycle or has `large' subtours)
    def bad_subtours(self, cons, solution=None):
        G = self.build_graph(cons, solution)
        cycles = [G.subgraph(g) for g in networkx.weakly_connected_components(G)]
        if len(cycles) == 1:
            return []
        return [H for H in cycles if min(len(H.nodes), len(G.nodes) - len(H.nodes)) < self.min_subtour_length]

    # checks whether solution is feasible w.r.t constraint type (whether it has subtours)
    def conscheck(self, constraints, solution, check_integrality, check_lp_rows, print_reason, completely, **results):
        for cons in constraints:
            if self.bad_subtours(cons, solution):
                return {"result": SCIP_RESULT.INFEASIBLE}

        return {"result": SCIP_RESULT.FEASIBLE}

    # enforces the LP solution: search and block subtours found in the solution
    def consenfolp(self, constraints, n_useful_conss, sol_infeasible):
        consadded = False
        
        for cons in constraints:
            bad_subtours = self.bad_subtours(cons)
            # if short subtours exist...
            if bad_subtours:
                x = cons.data["vars"]
                for S in bad_subtours:
                    # ... eliminate them!
                    #print(f"Constraint added: eliminates subtour of length {len(S.nodes)}") 
                    self.model.addCons(quicksum(x[p, q] for p, q in S.edges) <= len(S) - 1)
                    consadded = True

        if consadded:
            return {"result": SCIP_RESULT.CONSADDED}

        return {"result": SCIP_RESULT.FEASIBLE}

    # TODO: figure out what this does by reading https://scipopt.org/doc/html/CONS.php#CONS_FUNDAMENTALCALLBACKS
    def conslock(self, constraint, locktype, nlockspos, nlocksneg):
        pass

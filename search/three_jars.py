#------------------------------------------------------------------------------------------------------------------
#   Three Jugs Problem - SimpleAI
#------------------------------------------------------------------------------------------------------------------

from simpleai.search import SearchProblem, breadth_first, depth_first

#------------------------------------------------------------------------------------------------------------------
#   Problem definition
#------------------------------------------------------------------------------------------------------------------

class ThreeJugsProblem(SearchProblem):
    """
    States are represented by tuples (a, b, c) where:
        a = current amount of water in jug A
        b = current amount of water in jug B
        c = current amount of water in jug C
    """

    def __init__(self, capacities=(12, 8, 5), initial_state=(0, 0, 0), target=6):
        self.capA, self.capB, self.capC = capacities
        self.target = target

        SearchProblem.__init__(self, initial_state)

    #------------------------------------------------------------
    # Possible actions
    #------------------------------------------------------------
    def actions(self, state):
        a, b, c = state
        capA, capB, capC = self.capA, self.capB, self.capC

        actions = []

        # --- Fill actions ---
        if a < capA: actions.append(('fillA',))
        if b < capB: actions.append(('fillB',))
        if c < capC: actions.append(('fillC',))

        # --- Empty actions ---
        if a > 0: actions.append(('emptyA',))
        if b > 0: actions.append(('emptyB',))
        if c > 0: actions.append(('emptyC',))

        # --- Pour actions (A->B, A->C, B->A, B->C, C->A, C->B) ---
        if a > 0 and b < capB: actions.append(('pourAB',))
        if a > 0 and c < capC: actions.append(('pourAC',))
        if b > 0 and a < capA: actions.append(('pourBA',))
        if b > 0 and c < capC: actions.append(('pourBC',))
        if c > 0 and a < capA: actions.append(('pourCA',))
        if c > 0 and b < capB: actions.append(('pourCB',))

        return actions

    #------------------------------------------------------------
    # Transition model
    #------------------------------------------------------------
    def result(self, state, action):
        a, b, c = state
        act = action[0]   # e.g. "fillA"

        capA, capB, capC = self.capA, self.capB, self.capC

        # Fill actions
        if act == 'fillA': a = capA
        elif act == 'fillB': b = capB
        elif act == 'fillC': c = capC

        # Empty actions
        elif act == 'emptyA': a = 0
        elif act == 'emptyB': b = 0
        elif act == 'emptyC': c = 0

        # Pour actions
        elif act == 'pourAB':
            delta = min(a, capB - b)
            a -= delta
            b += delta
        elif act == 'pourAC':
            delta = min(a, capC - c)
            a -= delta
            c += delta
        elif act == 'pourBA':
            delta = min(b, capA - a)
            b -= delta
            a += delta
        elif act == 'pourBC':
            delta = min(b, capC - c)
            b -= delta
            c += delta
        elif act == 'pourCA':
            delta = min(c, capA - a)
            c -= delta
            a += delta
        elif act == 'pourCB':
            delta = min(c, capB - b)
            c -= delta
            b += delta

        return (a, b, c)

    #------------------------------------------------------------
    # Goal test
    #------------------------------------------------------------
    def is_goal(self, state):
        a, b, c = state
        return (a == self.target) or (b == self.target) or (c == self.target)


#------------------------------------------------------------------------------------------------------------------
#   Program
#------------------------------------------------------------------------------------------------------------------

problem = ThreeJugsProblem(capacities=(12, 8, 5), initial_state=(0, 0, 0), target=6)
result = breadth_first(problem, graph_search=True)

# Print results
for i, (action, state) in enumerate(result.path()):
    print()
    if action is None:
        print("Initial configuration")
    elif i == len(result.path()) - 1:
        print("After action", action, "→ Goal achieved!")
    else:
        print("After action", action)
    print(state)

#------------------------------------------------------------------------------------------------------------------
#   End of file
#------------------------------------------------------------------------------------------------------------------

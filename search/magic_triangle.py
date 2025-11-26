#------------------------------------------------------------------------------------------------------------------
#   Triángulo Mágico con simpleai
#------------------------------------------------------------------------------------------------------------------

from simpleai.search import SearchProblem, depth_first, breadth_first

# Constantes
VALUES = {1, 2, 3, 4, 5, 6}
S = 10  # suma objetivo por cada lado

# Lados del triángulo (índices de las posiciones)
SIDES = [
    (0, 1, 3),  # A, B, D
    (1, 2, 4),  # B, C, E
    (2, 0, 5)   # C, A, F
]

#------------------------------------------------------------------------------------------------------------------
#   Problem definition
#------------------------------------------------------------------------------------------------------------------

class MagicTriangle(SearchProblem):

    def __init__(self):
        # Estado inicial: 6 posiciones vacías (None)
        initial_state = (None, None, None, None, None, None)
        super().__init__(initial_state)

    def actions(self, state):
        """
        Devuelve todas las acciones posibles: asignar un número disponible
        a la siguiente posición vacía.
        """
        # Elegimos la primera posición vacía
        try:
            pos = state.index(None)
        except ValueError:
            return []  # no hay acciones si el estado está completo

        used = set(v for v in state if v is not None)
        available = VALUES - used
        
        actions = []
        for v in available:
            # Acción: "SET-pos-value"
            if self._consistent_partial(state, pos, v):
                actions.append(f"SET-{pos}-{v}")

        return actions

    def result(self, state, action):
        """ Ejecuta una acción y devuelve el nuevo estado. """
        _, pos, value = action.split('-')
        pos = int(pos)
        value = int(value)

        state_list = list(state)
        state_list[pos] = value
        return tuple(state_list)

    def is_goal(self, state):
        """ Comprueba que todas las posiciones estén llenas y todas las sumas sean S. """
        if None in state:
            return False

        for (a, b, c) in SIDES:
            if state[a] + state[b] + state[c] != S:
                return False

        return True

    #--------------------------------------
    #   Función auxiliar: poda parcial
    #--------------------------------------
    def _consistent_partial(self, state, pos, v):
        """
        Valida el estado parcialmente asignado:
        - Si un lado está completo, su suma debe ser S.
        - Si un lado tiene suma parcial > S, se poda.
        """
        temp = list(state)
        temp[pos] = v
        temp = tuple(temp)

        for (a, b, c) in SIDES:
            vals = [temp[a], temp[b], temp[c]]

            if None not in vals:  
                # lado completo → debe cumplir S
                if sum(vals) != S:
                    return False
            else:
                # lado parcial → su suma no puede exceder S
                partial_sum = sum(x for x in vals if x is not None)
                if partial_sum >= S:
                    return False

        return True

#------------------------------------------------------------------------------------------------------------------
#   Program
#------------------------------------------------------------------------------------------------------------------

result = depth_first(MagicTriangle(), graph_search=True)

# Print results
for i, (action, state) in enumerate(result.path()):
    print()
    if action is None:
        print("Initial configuration:")
    elif i == len(result.path()) - 1:
        print("After", action, "→ Goal achieved!")
    else:
        print("After", action)
    print(state)

#------------------------------------------------------------------------------------------------------------------
#   End of file
#------------------------------------------------------------------------------------------------------------------

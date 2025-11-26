import math
import heapq

graph = {
    'A': [('B', 3/16.6), ('C', 2/11.1), ('D', 4/16.6)],          
    'B': [('A', 3/16.6), ('E', 5/11.1), ('F', 3/16.6)],
    'C': [('A', 2/11.1), ('F', 4/11.1)],                       
    'D': [('A', 4/16.6), ('G', 6/11.1)],
    'E': [('B', 5/11.1), ('H', 3/6.9)],                        
    'F': [('B', 3/16.6), ('C', 4/11.1), ('H', 2/16.6)],
    'G': [('D', 6/11.1), ('H', 5/16.6)],
    'H': [('E', 3/6.9), ('F', 2/16.6), ('G', 5/16.6)]
}

coords = {
    'A': (0, 0),
    'B': (3, 2),
    'C': (2, -2),
    'D': (-3, 2),
    'E': (4, 4),
    'F': (6, 0),
    'G': (-6, 1),
    'H': (4, 1)
}

# velocidad máxima del mapa 
VEL_MAX = 16.6  

def heuristic(nodo, goal):
    x1, y1 = coords[nodo]
    x2, y2 = coords[goal]

    distancia = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    return distancia / VEL_MAX

def reconstruir_parents(parents, objetivo):
    path = []
    while objetivo is not None:
        path.append(objetivo)
        objetivo = parents[objetivo]
    return path[::-1]

def a_star(start, goal):
    g_cost = {}
    f_cost = {}
    parents = {}
    closed = set()

    g_cost[start] = 0
    f_cost[start] = heuristic(start, goal)
    parents[start] = None

    open = [(f_cost[start], start)]

    while open:
        f_actual, nodo = heapq.heappop(open)

        if f_actual != f_cost[nodo]:
            continue

        if nodo == goal:
            return reconstruir_parents(parents, nodo), f_cost[nodo]

        closed.add(nodo)

        for neighbor, cost in graph[nodo]:
            if neighbor in closed:
                continue

            new_g = g_cost[nodo] + cost

            if neighbor not in g_cost or new_g < g_cost[neighbor]:
                g_cost[neighbor] = new_g
                h = heuristic(neighbor, goal)
                f_cost[neighbor] = new_g + h
                parents[neighbor] = nodo

                heapq.heappush(open, (f_cost[neighbor], neighbor))

    return None, 0

path, f_cost=a_star('A', 'H')
if path:
    for n in path:
        print(n)
    print(f_cost)
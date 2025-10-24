graph = {
    "Goxmont": [("Zrusall", 112), ("Adaset", 103), ("Niaphia", 212)],
    "Zrusall": [("Goxmont", 112), ("Adaset", 15), ("Strento", 121)],
    "Adaset": [("Zrusall", 15), ("Goxmont", 103), ("Ertonwell", 130)],
    "Ertonwell": [("Adaset", 130), ("Niaphia", 56), ("Duron", 121)],
    "Niaphia": [("Goxmont", 212), ("Ertonwell", 56), ("Lagos", 300)],
    "Lagos": [("Niaphia", 300), ("Duron", 119)],
    "Duron": [("Ertonwell", 121), ("Lagos", 119), ("Blebus", 160)],
    "Blebus": [("Duron", 160), ("Togend", 121), ("Ontdale", 165), ("Oriaron", 291)],
    "Togend": [("Blebus", 121), ("Ontdale", 210)],
    "Ontdale": [("Togend", 210), ("Goding", 98), ("Oriaron", 219), ("Blebus", 165)],
    "Goding": [("Ylane", 88), ("Ontdale", 98)],
    "Ylane": [("Goding", 88), ("Strento", 99), ("Oriaron", 117)],
    "Strento": [("Zrusall", 121), ("Ylane", 99), ("Oriaron", 221)],
    "Oriaron": [("Strento", 221), ("Ylane", 117), ("Ontdale", 219), ("Blebus", 291)]
}

def dfs(graph, start, goal):
    frontier=[]
    frontier.append(start)
    explored = set([start])
    parents={}
    parents[start]=(None, 0)
    while frontier:
        node=frontier.pop()
        if node==goal:
            path=[]
            total_cost=0
            while node:
                path.append(node)
                parent, cost = parents[node]
                total_cost+=cost
                node=parent
            return list(reversed(path)), total_cost
        for neighbor, cost in graph[node]:
            if neighbor not in explored:
                frontier.append(neighbor)
                explored.add(neighbor)
                parents[neighbor]=(node, cost)
        
    return None, float('inf')
    
path, cost=dfs(graph, 'Strento', 'Lagos')
if path:
    print("Ruta:", " -> ".join(path))
    print("Costo total:", cost)
else:
    print("No se encontró camino.")
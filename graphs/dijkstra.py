import heapq

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

def dijkstra(graph, start):
    distances={node: float('inf') for node in graph}
    distances[start]=0
    frontier = []
    heapq.heappush(frontier, (0, start))
    explored = set()
    parents = {}
    parents[start]=(None, 0)
    while frontier:
        cCurrent, vCurrent = heapq.heappop(frontier)
        distances[vCurrent] = min(distances[vCurrent], cCurrent)
        if vCurrent not in explored:
          explored.add(vCurrent)
          for neighbor, cost in graph[vCurrent]:
            cNew=cCurrent + cost
            heapq.heappush(frontier, (cNew, neighbor))
            if neighbor not in parents or cNew < parents[neighbor][1]:
              parents[neighbor]= (vCurrent, cNew)

    return distances, parents

distances, parents = dijkstra(graph, 'Goding')
for node in graph:
    tempNode=node
    path = []
    while tempNode is not None:
        path.append(tempNode)
        tempNode = parents[tempNode][0]
    path.reverse()
    print(f"Shortest path from Goding to {node}: {' -> '.join(path)} with a distance of {distances[node]}")
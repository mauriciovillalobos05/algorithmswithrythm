from collections import deque

def dinic(G, s, t):
    max_flow = 0

    # Copia del grafo con aristas residuales iniciales
    g_temp = {u: [] for u in G}
    for u in G:
        for v, w in G[u]:
            g_temp[u].append([v, w])
            # Agregar arista inversa si no existe
            if not any(x == u for x, _ in G.get(v, [])):
                g_temp[v].append([u, 0])

    # Construir grafo de niveles (BFS)
    def bfs_level():
        level = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            for v, w in g_temp[u]:
                if w > 0 and v not in level:
                    level[v] = level[u] + 1
                    q.append(v)
        return level

    # DFS en el grafo de niveles (flujo de bloqueo)
    def dfs(u, flow, level, next_edge):
        if u == t:
            return flow
        n = len(g_temp[u])
        while next_edge[u] < n:
            v, w = g_temp[u][next_edge[u]]
            if w > 0 and level.get(v, -1) == level[u] + 1:
                pushed = dfs(v, min(flow, w), level, next_edge)
                if pushed > 0:
                    # Reducir capacidad directa
                    g_temp[u][next_edge[u]][1] -= pushed
                    # Aumentar capacidad inversa
                    for j, (vv, ww) in enumerate(g_temp[v]):
                        if vv == u:
                            g_temp[v][j][1] += pushed
                            break
                    else:
                        g_temp[v].append([u, pushed])
                    return pushed
            next_edge[u] += 1
        return 0

    # Algoritmo principal
    while True:
        level = bfs_level()
        if t not in level:  # No hay camino s-t
            break
        next_edge = {u: 0 for u in g_temp}
        while True:
            pushed = dfs(s, float('inf'), level, next_edge)
            if pushed == 0:
                break
            max_flow += pushed

    return max_flow


grafo = {
    'A': [('B', 70), ('C', 80), ('F', 37)],
    'B': [('H', 72)],
    'C': [('D', 54)],
    'D': [('L', 82)],
    'E': [('C', 44), ('D', 69), ('L', 71)],
    'F': [('A', 43), ('E', 47), ('G', 24)],
    'G': [('F', 25), ('K', 76)],
    'H': [('B', 85), ('G', 61), ('I', 23)],
    'I': [('G', 82), ('J', 60)],
    'J': [('G', 42), ('N', 90)],
    'K': [('E', 66), ('L', 50), ('M', 42), ('N', 34)],
    'L': [('M', 66)],
    'M': [('N', 75)],
    'N': [('K', 55)]
}

print("Flujo máximo de A a N:", dinic(grafo, 'A', 'N'))
print("Flujo máximo de G a M:", dinic(grafo, 'G', 'M'))
print("Flujo máximo de B a H:", dinic(grafo, 'B', 'H'))
print("Flujo máximo de I a L:", dinic(grafo, 'I', 'L'))

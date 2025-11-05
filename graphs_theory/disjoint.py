import heapq

class DisjointSet:

    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}
        
        self.rank = {v: 0 for v in vertices}

    def find(self, i):
        if i==self.parent[i]:
            return i
        
        self.parent[i]=self.find(self.parent[i])
        return self.parent[i]
    
    def union(self, i, j):
        root_i, root_j = self.find(i), self.find(j)
        if self.find(i)==self.find(j):
            return False
        
        if self.rank[root_i] < self.rank[root_j]:
            self.parent[root_i] = root_j
        elif self.rank[root_i] > self.rank[root_j]:
            self.parent[root_j] = root_i
        else:
            self.parent[root_j] = root_i
            self.rank[root_i] += 1
        
        return True

ciudades = [
    "Ylane", "Strento", "Zrusall", "Goxmont", "Adaset", "Oriaron", 
    "Goding", "Ontdale", "Blebus", "Duron", "Ertonwell", "Niaphia", 
    "Lagos", "Togend"
]

aristas = [
    ("Goxmont", "Zrusall", 112),
    ("Goxmont", "Adaset", 103),
    ("Goxmont", "Niaphia", 212),
    ("Zrusall", "Adaset", 15),
    ("Zrusall", "Strento", 121),
    ("Adaset", "Ertonwell", 130),
    ("Niaphia", "Ertonwell", 56),
    ("Niaphia", "Lagos", 300),
    ("Ertonwell", "Duron", 121),
    ("Ertonwell", "Lagos", 119),
    ("Lagos", "Blebus", 160),
    ("Duron", "Blebus", 160),
    ("Duron", "Oriaron", 291),
    ("Blebus", "Togend", 121),
    ("Togend", "Ontdale", 210),
    ("Ontdale", "Goding", 98),
    ("Ontdale", "Oriaron", 165),
    ("Goding", "Ylane", 88),
    ("Goding", "Oriaron", 117),
    ("Ylane", "Strento", 99),
    ("Ylane", "Oriaron", 219),
    ("Strento", "Oriaron", 221),
]

grafo = {ciudad: [] for ciudad in ciudades}
for c1, c2, peso in aristas:
    grafo[c1].append((c2, peso))
    grafo[c2].append((c1, peso))

def Prim(grafo, inicio):
    visited=set()
    heap=[(0, inicio, "null")]
    mst=0
    mst_aristas=[]

    while heap:
        costo, ciudad, origen = heapq.heappop(heap)
        if ciudad in visited:
            continue
        visited.add(ciudad)
        mst+=costo
        mst_aristas.append((origen, ciudad, costo))
        for vecino, costo_vecino in grafo[ciudad]:
            if vecino not in visited:
                heapq.heappush(heap, (costo_vecino, vecino, ciudad))

    return mst, mst_aristas

def Kruskal(ciudades, aristas):
    aristas_ordenadas = sorted(aristas, key=lambda x: x[2]) #ordenar aristas dependiendo el peso
    uf=DisjointSet(ciudades) #inicializar disjoint set
    mst=0
    mst_aristas=[]
    for ciudad1, ciudad2, costo in aristas_ordenadas:
        if uf.union(ciudad1, ciudad2):
            mst+=costo
            mst_aristas.append((ciudad1, ciudad2, costo))
    
    return mst, mst_aristas

prim_mst, prim_aristas = Prim(grafo, "Goxmont")
kruskal_mst, kruskal_aristas = Kruskal(grafo, aristas)

print("=== Prim ===")
print("Costo total:", prim_mst)
print("Aristas usadas", len(prim_aristas)-1) #resto 1 porque la primera es de null hacia el origen
for e in prim_aristas:
    print(e)

print("\n=== Kruskal ===")
print("Costo total:", kruskal_mst)
print("Aristas usadas", len(kruskal_aristas))
for e in kruskal_aristas:
    print(e)
import random

class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

class RangeTree1D:
    def __init__(self, points):
        # Ordenamos los puntos para asegurar que el árbol esté balanceado
        sorted_points = sorted(points)
        self.root = self._build_tree(sorted_points)

    def _build_tree(self, points):
        if not points:
            return None
        
        # Encontrar el punto medio para que sea la raíz
        mid = len(points) // 2
        node = Node(points[mid])
        
        # Construir subárboles recursivamente
        node.left = self._build_tree(points[:mid])
        node.right = self._build_tree(points[mid+1:])
        
        return node

    def query(self, low, high):
        result = []
        self._query_recursive(self.root, low, high, result)
        return result

    def _query_recursive(self, node, low, high, result):
        if node is None:
            return

        # 1. Si el nodo actual está dentro del rango, lo añadimos
        if low <= node.val <= high:
            result.append(node.val)

        # 2. Si el valor del nodo es mayor que el límite inferior,
        # debemos buscar también en la izquierda.
        if node.val > low:
            self._query_recursive(node.left, low, high, result)

        # 3. Si el valor del nodo es menor que el límite superior,
        # debemos buscar también en la derecha.
        if node.val < high:
            self._query_recursive(node.right, low, high, result)


# 1. Generar 2000 valores aleatorios entre -10 y 10
data = [random.uniform(-10, 10) for _ in range(2000)]

# 2. Construir el Range Tree
tree = RangeTree1D(data)

# 3. Definir los rangos a buscar
search_ranges = [
    (-1, -0.5),
    (2, 4),
    (-5, -4),
    (-10, -9.3),
    (9, 9.5)
]

# 4. Ejecutar búsquedas e imprimir resultados
print(f"{'RANGO':<15} | {'CANTIDAD':<10} | {'EJEMPLOS (Primeros 5)'}")
print("-" * 60)

for r_min, r_max in search_ranges:
    # Realizamos la búsqueda
    found = tree.query(r_min, r_max)
    
    # Formateamos para mostrar
    count = len(found)
    examples = ", ".join([f"{x:.2f}" for x in found[:5]])
    if count > 5:
        examples += "..."
        
    print(f"[{r_min}, {r_max:<4}]   | {count:<10} | {examples}")
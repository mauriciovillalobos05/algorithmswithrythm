import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

# --- 1. Estructura de Datos: K-d Tree ---

class Node:
    def __init__(self, point, left=None, right=None, axis=0):
        self.point = point
        self.left = left
        self.right = right
        self.axis = axis

class KDTree:
    def __init__(self, points):
        self.k = len(points[0]) # Dimensión (2 para x,y)
        self.root = self._build(points, depth=0)

    def _build(self, points, depth):
        if not points:
            return None
        
        # Seleccionar eje basado en la profundidad (x=0, y=1)
        axis = depth % self.k
        
        # Ordenar puntos y elegir la mediana para balancear el árbol
        points.sort(key=lambda x: x[axis])
        median = len(points) // 2
        
        return Node(
            point=points[median],
            left=self._build(points[:median], depth + 1),
            right=self._build(points[median+1:], depth + 1),
            axis=axis
        )

    def range_search(self, x_range, y_range):
        found_points = []
        self._search(self.root, x_range, y_range, found_points)
        return found_points

    def _search(self, node, x_range, y_range, found_points):
        if node is None:
            return

        x, y = node.point
        
        # 1. Verificar si el punto actual está dentro del rango
        if (x_range[0] <= x <= x_range[1]) and (y_range[0] <= y <= y_range[1]):
            found_points.append(node.point)

        # 2. Determinar si debemos buscar a la izquierda o derecha (Poda del árbol)
        # Rango actual del eje correspondiente al nodo
        curr_range = x_range if node.axis == 0 else y_range
        curr_val = x if node.axis == 0 else y
        
        # Si el valor del nodo es mayor o igual al mínimo del rango, buscamos en la izquierda
        if curr_val >= curr_range[0]:
            self._search(node.left, x_range, y_range, found_points)
            
        # Si el valor del nodo es menor o igual al máximo del rango, buscamos en la derecha
        if curr_val <= curr_range[1]:
            self._search(node.right, x_range, y_range, found_points)

# --- 2. Generación de Datos ---

# Generamos 200 puntos en el plano [-10, 10] para asegurar cobertura
random.seed(42) # Semilla para reproducibilidad
points = [
    (round(random.uniform(-10, 10), 2), round(random.uniform(-10, 10), 2)) 
    for _ in range(200)
]

# Construimos el árbol
tree = KDTree(points)

# --- 3. Definición de Consultas (De tu imagen) ---

queries = [
    {"x": [-1, 1], "y": [-2, 2]},
    {"x": [-2, 1], "y": [3, 5]},
    {"x": [-7, 0], "y": [-6, 4]},
    {"x": [-2, 2], "y": [-3, 3]},
    {"x": [-7, 5], "y": [-3, 1]}
]

# --- 4. Visualización ---

fig, axs = plt.subplots(1, 5, figsize=(25, 5))
fig.suptitle(f'Búsquedas Multidimensionales con K-d Tree (Total Puntos: {len(points)})', fontsize=16)

for i, query in enumerate(queries):
    xr, yr = query["x"], query["y"]
    
    # Ejecutar búsqueda usando el KD-Tree
    result = tree.range_search(xr, yr)
    
    ax = axs[i]
    
    # Graficar todos los puntos (contexto)
    all_x, all_y = zip(*points)
    ax.scatter(all_x, all_y, c='lightgray', alpha=0.5, label='Datos')
    
    # Graficar puntos encontrados
    if result:
        res_x, res_y = zip(*result)
        ax.scatter(res_x, res_y, c='red', edgecolors='black', s=60, label='Encontrados')
    
    # Dibujar el rectángulo de búsqueda
    width = xr[1] - xr[0]
    height = yr[1] - yr[0]
    rect = patches.Rectangle((xr[0], yr[0]), width, height, linewidth=2, edgecolor='blue', facecolor='none')
    ax.add_patch(rect)
    
    # Formato del gráfico
    ax.set_title(f'Consulta {i+1}:\nx ∈ {xr}, y ∈ {yr}\nEncontrados: {len(result)}')
    ax.set_xlim(-11, 11)
    ax.set_ylim(-11, 11)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)

plt.tight_layout()
plt.show()
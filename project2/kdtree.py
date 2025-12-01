import osmnx as ox
import numpy as np
import time
from pyproj import Transformer
import matplotlib.pyplot as plt

class Nodo:
    """Nodo del KD-Tree"""
    def __init__(self, punto, id_nodo, eje, izq=None, der=None):
        self.punto = punto      # Coordenadas (x, y) en UTM
        self.id_nodo = id_nodo  # ID del nodo en el grafo
        self.eje = eje          # Eje de división (0=x, 1=y)
        self.izq = izq          # Subárbol izquierdo
        self.der = der          # Subárbol derecho

class KDTree:
    """Estructura de datos KD-Tree para búsqueda espacial optimizada"""
    def __init__(self, k=2):
        self.k = k
        self.raiz = None
    
    def construir(self, puntos):
        """Construye el KD-Tree a partir de una lista de puntos"""
        self.raiz = self._construir_recursivo(puntos, profundidad=0)
    
    def _construir_recursivo(self, puntos, profundidad):
        """Construcción recursiva del árbol"""
        if not puntos:
            return None
        
        # Determinar el eje de división
        eje = profundidad % self.k
        
        # Ordenar puntos por el eje actual y seleccionar la mediana
        puntos.sort(key=lambda p: p[0][eje])
        mediana_idx = len(puntos) // 2
        
        punto, id_nodo = puntos[mediana_idx]
        nodo = Nodo(punto=punto, id_nodo=id_nodo, eje=eje)
        
        # Construir subárboles recursivamente
        nodo.izq = self._construir_recursivo(puntos[:mediana_idx], profundidad + 1)
        nodo.der = self._construir_recursivo(puntos[mediana_idx+1:], profundidad + 1)
        
        return nodo
    
    def buscar_mas_cercano(self, punto_objetivo):
        """Encuentra el nodo más cercano al punto objetivo"""
        mejor = {'nodo': None, 'distancia': float('inf')}
        self._buscar_recursivo(self.raiz, punto_objetivo, mejor)
        return mejor['nodo'].id_nodo, mejor['distancia']
    
    def _buscar_recursivo(self, nodo, objetivo, mejor):
        """Búsqueda recursiva del punto más cercano"""
        if nodo is None:
            return
        
        # Calcular distancia euclidiana al nodo actual
        dist = np.sqrt(sum((a - b) ** 2 for a, b in zip(nodo.punto, objetivo)))
        
        # Actualizar mejor nodo si es necesario
        if dist < mejor['distancia']:
            mejor['distancia'] = dist
            mejor['nodo'] = nodo
        
        # Determinar qué lado explorar primero
        eje = nodo.eje
        if objetivo[eje] < nodo.punto[eje]:
            lado_cercano = nodo.izq
            lado_lejano = nodo.der
        else:
            lado_cercano = nodo.der
            lado_lejano = nodo.izq
        
        # Explorar lado cercano
        self._buscar_recursivo(lado_cercano, objetivo, mejor)
        
        # Explorar lado lejano solo si es necesario (poda)
        if abs(objetivo[eje] - nodo.punto[eje]) < mejor['distancia']:
            self._buscar_recursivo(lado_lejano, objetivo, mejor)


def latlon_a_utm(lat, lon):
    """Convierte coordenadas lat/lon (WGS84) a UTM"""
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32613", always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y


def obtener_coordenadas_nodo(grafo, node_id):
    """Obtiene las coordenadas lat/lon de un nodo del grafo"""
    lat = grafo.nodes[node_id]['y']
    lon = grafo.nodes[node_id]['x']
    return lat, lon


def busqueda_exhaustiva(grafo, lat, lon):
    """Búsqueda por fuerza bruta del nodo más cercano"""
    x_obj, y_obj = latlon_a_utm(lat, lon)
    
    mejor_nodo = None
    mejor_dist = float('inf')
    
    for node_id in grafo.nodes():
        lat_nodo, lon_nodo = obtener_coordenadas_nodo(grafo, node_id)
        x_nodo, y_nodo = latlon_a_utm(lat_nodo, lon_nodo)
        
        dist = np.sqrt((x_obj - x_nodo)**2 + (y_obj - y_nodo)**2)
        
        if dist < mejor_dist:
            mejor_dist = dist
            mejor_nodo = node_id
    
    return mejor_nodo, mejor_dist


# 20 lugares de interés en Guadalajara
LUGARES_GUADALAJARA = [
    ("Glorieta Chapultepec", 20.6737, -103.3627),
    ("Catedral de Guadalajara", 20.6777, -103.3475),
    ("Teatro Degollado", 20.6765, -103.3434),
    ("Hospicio Cabañas", 20.6744, -103.3372),
    ("Parque Agua Azul", 20.6697, -103.3394),
    ("Mercado San Juan de Dios", 20.6742, -103.3387),
    ("Plaza de Armas", 20.6773, -103.3464),
    ("Templo Expiatorio", 20.6785, -103.3572),
    ("Parque Revolución", 20.6724, -103.3549),
    ("Estadio Jalisco", 20.6654, -103.3233),
    ("Plaza Galerías", 20.6734, -103.3913),
    ("Andares", 20.6909, -103.3836),
    ("Plaza del Sol", 20.6588, -103.3788),
    ("Minerva", 20.6739, -103.3854),
    ("Arcos Vallarta", 20.6673, -103.4026),
    ("Parque Metropolitano", 20.7059, -103.3764),
    ("Zoológico Guadalajara", 20.6706, -103.3186),
    ("Universidad de Guadalajara", 20.6778, -103.3467),
    ("Hospital Civil", 20.6685, -103.3361),
    ("Trompo Mágico", 20.7039, -103.3518)
]


def main():
    print("=" * 80)
    print("COMPONENTE 1: BÚSQUEDA OPTIMIZADA CON KD-TREE")
    print("=" * 80)
    
    # 1. Descargar el grafo
    print("\n[1] Descargando grafo de Guadalajara...")
    center_point = (20.6737, -103.3627)  # Glorieta Chapultepec
    G = ox.graph_from_point(center_point, dist=7000, network_type='drive')
    print(f"    ✓ Grafo descargado: {len(G.nodes)} nodos, {len(G.edges)} aristas")
    
    # 2. Construir KD-Tree
    print("\n[2] Construyendo KD-Tree...")
    puntos_utm = []
    for node_id in G.nodes():
        lat, lon = obtener_coordenadas_nodo(G, node_id)
        x, y = latlon_a_utm(lat, lon)
        puntos_utm.append(((x, y), node_id))
    
    kd_tree = KDTree(k=2)
    
    inicio = time.time()
    kd_tree.construir(puntos_utm)
    tiempo_construccion = time.time() - inicio
    
    print(f"    ✓ KD-Tree construido en {tiempo_construccion:.4f} segundos")
    print(f"    ✓ {len(puntos_utm)} nodos indexados")
    
    # 3. Búsqueda con KD-Tree
    print("\n[3] Búsqueda de nodos más cercanos con KD-Tree:")
    print(f"    {'Lugar':<30} {'Tiempo (ms)':<15} {'Distancia (m)':<15}")
    print("    " + "-" * 60)
    
    tiempos_kd = []
    for nombre, lat, lon in LUGARES_GUADALAJARA:
        inicio = time.time()
        nodo_id, distancia = kd_tree.buscar_mas_cercano(latlon_a_utm(lat, lon))
        tiempo = (time.time() - inicio) * 1000  # Convertir a ms
        tiempos_kd.append(tiempo)
        print(f"    {nombre:<30} {tiempo:<15.6f} {distancia:<15.2f}")
    
    promedio_kd = np.mean(tiempos_kd)
    print(f"\n    ✓ Tiempo promedio KD-Tree: {promedio_kd:.6f} ms")
    
    # 4. Búsqueda exhaustiva
    print("\n[4] Búsqueda exhaustiva (fuerza bruta):")
    print(f"    {'Lugar':<30} {'Tiempo (ms)':<15} {'Distancia (m)':<15}")
    print("    " + "-" * 60)
    
    tiempos_exhaustiva = []
    for nombre, lat, lon in LUGARES_GUADALAJARA:
        inicio = time.time()
        nodo_id, distancia = busqueda_exhaustiva(G, lat, lon)
        tiempo = (time.time() - inicio) * 1000
        tiempos_exhaustiva.append(tiempo)
        print(f"    {nombre:<30} {tiempo:<15.6f} {distancia:<15.2f}")
    
    promedio_exhaustiva = np.mean(tiempos_exhaustiva)
    print(f"\n    ✓ Tiempo promedio búsqueda exhaustiva: {promedio_exhaustiva:.6f} ms")
    
    # 5. Comparación
    print("\n" + "=" * 80)
    print("RESULTADOS COMPARATIVOS")
    print("=" * 80)
    print(f"Tiempo de construcción del KD-Tree: {tiempo_construccion:.4f} segundos")
    print(f"Tiempo promedio KD-Tree:             {promedio_kd:.6f} ms")
    print(f"Tiempo promedio búsqueda exhaustiva: {promedio_exhaustiva:.6f} ms")
    print(f"Aceleración (speedup):               {promedio_exhaustiva/promedio_kd:.2f}x")
    print(f"Mejora porcentual:                   {((promedio_exhaustiva-promedio_kd)/promedio_exhaustiva)*100:.2f}%")
    
    # 6. Visualización
    print("\n[5] Generando visualización...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Gráfico de tiempos por lugar
    x = range(len(LUGARES_GUADALAJARA))
    ax1.plot(x, tiempos_kd, 'o-', label='KD-Tree', linewidth=2, markersize=6, color='#2ecc71')
    ax1.plot(x, tiempos_exhaustiva, 's-', label='Exhaustiva', linewidth=2, markersize=6, color='#e74c3c')
    ax1.set_xlabel('Lugar', fontsize=12)
    ax1.set_ylabel('Tiempo (ms)', fontsize=12)
    ax1.set_title('Comparación de tiempos de búsqueda por lugar', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(range(0, len(LUGARES_GUADALAJARA), 2))
    
    # Gráfico de barras comparativo
    labels = ['KD-Tree', 'Exhaustiva']
    tiempos = [promedio_kd, promedio_exhaustiva]
    colors = ['#2ecc71', '#e74c3c']
    bars = ax2.bar(labels, tiempos, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax2.set_ylabel('Tiempo promedio (ms)', fontsize=12)
    ax2.set_title('Tiempo promedio de búsqueda', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    for i, v in enumerate(tiempos):
        ax2.text(i, v + max(tiempos)*0.02, f'{v:.4f} ms', 
                ha='center', fontweight='bold', fontsize=11)
    
    # Agregar texto con el speedup
    speedup_text = f'Aceleración: {promedio_exhaustiva/promedio_kd:.2f}x'
    ax2.text(0.5, max(tiempos)*0.85, speedup_text, 
            ha='center', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('comparacion_busqueda.png', dpi=300, bbox_inches='tight')
    print("    ✓ Gráfico guardado como 'comparacion_busqueda.png'")
    
    print("\n" + "=" * 80)
    print("CONCLUSIÓN")
    print("=" * 80)
    print(f"El KD-Tree es {promedio_exhaustiva/promedio_kd:.2f}x más rápido que la búsqueda exhaustiva.")
    print(f"Esto representa una mejora del {((promedio_exhaustiva-promedio_kd)/promedio_exhaustiva)*100:.2f}%.")
    print(f"Para {len(G.nodes)} nodos, el KD-Tree es esencial para búsquedas eficientes.")
    
    plt.show()


if __name__ == "__main__":
    main()
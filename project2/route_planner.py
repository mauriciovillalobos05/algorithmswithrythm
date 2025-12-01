import osmnx as ox
import numpy as np
import time
import geopy.distance
import networkx as nx
from simpleai.search import SearchProblem, breadth_first, depth_first, uniform_cost, astar
import matplotlib.pyplot as plt
import pandas as pd
from kdtree import KDTree, latlon_a_utm, obtener_coordenadas_nodo


# -------------------------
# Utilidad: convertir a tipos nativos
# -------------------------
def to_native(x):
    """Convierte tipos numpy a tipos nativos de Python"""
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, bytes):
        return x.decode()
    if isinstance(x, (list, tuple)):
        return tuple(to_native(v) for v in x)
    return x


# --------------------------------------------------------------------
# PROBLEMA DE BÚSQUEDA DE RUTAS (SimpleAI)
# --------------------------------------------------------------------
class RutaGrafoProblem(SearchProblem):
    """Problema de búsqueda de rutas en un grafo de calles (compatible con SimpleAI)."""

    def __init__(self, grafo, nodo_inicio, nodo_meta):
        self.grafo = grafo
        self.nodo_meta = to_native(nodo_meta)
        nodo_inicio = to_native(nodo_inicio)
        
        # SimpleAI solo requiere el estado inicial
        super().__init__(nodo_inicio)

    def actions(self, state):
        """Retorna las acciones posibles desde un estado (nodos vecinos)"""
        state = to_native(state)
        try:
            vecinos = list(self.grafo.successors(state))
        except Exception:
            try:
                vecinos = list(self.grafo.successors(int(state)))
            except Exception:
                vecinos = []
        return [to_native(v) for v in vecinos]

    def result(self, state, action):
        """Retorna el estado resultante de aplicar una acción"""
        return to_native(action)

    def is_goal(self, state):
        """Verifica si el estado actual es la meta"""
        return to_native(state) == self.nodo_meta

    def cost(self, state, action, state2):
        """Calcula el costo de ir de state a state2 (distancia en metros)"""
        s = to_native(state)
        t = to_native(state2)

        try:
            edge_data = self.grafo.get_edge_data(s, t)
            if edge_data:
                if isinstance(edge_data, dict):
                    first = next(iter(edge_data.values()))
                    length = first.get("length", 1)
                else:
                    length = edge_data.get("length", 1)
                return float(to_native(length))
        except Exception:
            pass
        return 1.0

    def heuristic(self, state):
        """Heurística: distancia geodésica desde el estado actual hasta la meta"""
        s = to_native(state)
        g = self.nodo_meta
        try:
            lat1, lon1 = obtener_coordenadas_nodo(self.grafo, s)
            lat2, lon2 = obtener_coordenadas_nodo(self.grafo, g)
            return float(geopy.distance.distance((lat1, lon1), (lat2, lon2)).m)
        except Exception:
            return 0.0


# ============================================================================
# IDDFS - Iterative Deepening Depth-First Search (implementación propia)
# ============================================================================
def iddfs_custom(grafo, nodo_inicio, nodo_meta, max_depth=50, timeout=5):
    import signal

    def handler(signum, frame):
        raise TimeoutError("IDDFS Timeout")

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)

    inicio = to_native(nodo_inicio)
    meta = to_native(nodo_meta)

    nodos_explorados = 0

    def dls(node, depth, path, visited):
        nonlocal nodos_explorados
        nodos_explorados += 1

        if to_native(node) == meta:
            return path + [to_native(node)]
        if depth <= 0:
            return None

        try:
            vecinos = list(grafo.successors(node))
        except:
            vecinos = []

        for vecino in vecinos:
            vn = to_native(vecino)
            if vn not in visited:
                result = dls(vn, depth - 1, path + [node], visited | {node})
                if result:
                    return result
        return None

    for depth in range(max_depth + 1):
        result = dls(inicio, depth, [], set())
        if result:
            signal.alarm(0)
            return result, nodos_explorados

    signal.alarm(0)
    return None, nodos_explorados



# ============================================================================
# Calcular distancia entre nodos
# ============================================================================
def calcular_distancia_nodos(grafo, nodo1, nodo2):
    """Calcula la distancia geodésica entre dos nodos"""
    lat1, lon1 = obtener_coordenadas_nodo(grafo, to_native(nodo1))
    lat2, lon2 = obtener_coordenadas_nodo(grafo, to_native(nodo2))
    return geopy.distance.distance((lat1, lon1), (lat2, lon2)).m


def calcular_longitud_ruta(grafo, ruta):
    """Calcula la longitud total de una ruta usando los pesos de las aristas del grafo"""
    if not ruta or len(ruta) < 2:
        return 0.0
    
    longitud_total = 0.0
    for i in range(len(ruta) - 1):
        nodo_actual = to_native(ruta[i])
        nodo_siguiente = to_native(ruta[i + 1])
        
        try:
            # Obtener datos de la arista
            edge_data = grafo.get_edge_data(nodo_actual, nodo_siguiente)
            if edge_data:
                if isinstance(edge_data, dict):
                    # Si hay múltiples aristas, tomar la primera
                    first = next(iter(edge_data.values()))
                    length = first.get("length", 0)
                else:
                    length = edge_data.get("length", 0)
                longitud_total += float(to_native(length))
            else:
                # Si no hay datos de arista, usar distancia geodésica como fallback
                longitud_total += calcular_distancia_nodos(grafo, nodo_actual, nodo_siguiente)
        except Exception:
            # Fallback: usar distancia geodésica
            longitud_total += calcular_distancia_nodos(grafo, nodo_actual, nodo_siguiente)
    
    return longitud_total


# ============================================================================
# Selección de parejas de nodos por distancia
# ============================================================================
def seleccionar_parejas_por_distancia(grafo, min_dist, max_dist, num_parejas=5):
    """
    Selecciona parejas de nodos que estén dentro de un rango de distancia específico
    y que tengan un camino conectado entre ellos
    """
    # Obtener el componente fuertemente conectado más grande
    if not nx.is_strongly_connected(grafo):
        largest_scc = max(nx.strongly_connected_components(grafo), key=len)
        nodos = list(largest_scc)
        print(f"      Usando componente conectado con {len(nodos)} nodos")
    else:
        nodos = list(grafo.nodes())

    parejas = []
    intentos = 0
    max_intentos = 10000

    while len(parejas) < num_parejas and intentos < max_intentos:
        nodo1 = to_native(np.random.choice(nodos))
        nodo2 = to_native(np.random.choice(nodos))
        intentos += 1

        if nodo1 == nodo2:
            continue
        
        try:
            dist = calcular_distancia_nodos(grafo, nodo1, nodo2)
        except Exception:
            continue

        if min_dist <= dist <= max_dist:
            try:
                # Verificar que exista un camino
                if nx.has_path(grafo, nodo1, nodo2):
                    parejas.append((nodo1, nodo2, dist))
                    print(f"      ✓ Pareja {len(parejas)}: {dist:.0f}m")
            except Exception:
                pass

        if intentos % 500 == 0 and len(parejas) < num_parejas:
            print(f"      ... buscando (intentos: {intentos}, encontradas: {len(parejas)})")

    return parejas


# --------------------------------------------------------------------
# Parser de resultados de SimpleAI (versión corregida y robusta)
# --------------------------------------------------------------------
def _parse_simpleai_result(res, problema=None):
    """
    Extrae la ruta (lista de nodos) desde el resultado de SimpleAI de forma robusta.
    - Acepta: lista de estados, lista de (action,state), o objetos con atributo 'state'.
    - Si se pasa 'problema', valida que la ruta comienza en inicio y termina en meta;
      si no, intenta invertir la ruta.
    """
    if res is None:
        return []

    ruta = []

    # 1) Intentar obtener path() si existe
    try:
        if hasattr(res, "path"):
            steps = res.path()
            # steps puede ser: [start, n1, n2, ...] o [(action, state), ...]
            for s in steps:
                if isinstance(s, tuple) and len(s) == 2:
                    ruta.append(to_native(s[1]))
                else:
                    ruta.append(to_native(s))
        else:
            # Si no hay path(), intentar obtener atributo 'solution' o lista en res
            if hasattr(res, "solution"):
                sol = res.solution
                if isinstance(sol, (list, tuple)):
                    for s in sol:
                        ruta.append(to_native(s))
            elif isinstance(res, (list, tuple)):
                for s in res:
                    ruta.append(to_native(s))
    except Exception:
        # fallback silencioso
        pass

    # 2) Si no encontramos nada pero res tiene 'state' (nodos encadenados), tratar de seguirlos
    if not ruta and hasattr(res, "state"):
        try:
            node = res
            visited = []
            while node is not None:
                if hasattr(node, "state"):
                    visited.append(to_native(node.state))
                elif hasattr(node, "value"):
                    visited.append(to_native(node.value))
                else:
                    break
                node = getattr(node, "parent", None)
            ruta = list(reversed(visited))
        except Exception:
            ruta = []

    # 3) Limpiar duplicados consecutivos
    ruta_limpia = []
    for r in ruta:
        if len(ruta_limpia) == 0 or ruta_limpia[-1] != r:
            ruta_limpia.append(r)

    # 4) Asegurar orden start -> goal si tenemos el problema
    if problema is not None and len(ruta_limpia) >= 2:
        try:
            start = to_native(problema.initial_state)
            goal = to_native(problema.nodo_meta)
            if ruta_limpia[0] != start and ruta_limpia[-1] == start:
                ruta_limpia.reverse()
            # Si ninguno de los extremos coincide con start, no forzamos nada (posible fallo)
        except Exception:
            pass

    return ruta_limpia

# ============================================================================
# Ejecutar todos los algoritmos y medir tiempos
# ============================================================================
# --------------------------------------------------------------------
# Ejecutar y medir (reemplaza la función run_and_measure dentro de ejecutar_algoritmos)
# --------------------------------------------------------------------
def ejecutar_algoritmos(grafo, nodo_inicio, nodo_meta):
    problema = RutaGrafoProblem(grafo, nodo_inicio, nodo_meta)
    resultados = {}

    def run_and_measure(fn, label, timeout=5):
        import signal

        def handler(signum, frame):
            raise TimeoutError("Tiempo límite excedido")

        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)

            t0 = time.time()
            # Para SimpleAI: pasar graph_search=True suele ser correcto; mantenerlo.
            res = fn(problema, graph_search=True)
            tiempo = time.time() - t0

            signal.alarm(0)

            # --- parsear ruta y contar nodos en la ruta ---
            ruta_nodos = _parse_simpleai_result(res, problema=problema)
            nodos_en_ruta = len(ruta_nodos) if ruta_nodos else 0

            # --- obtener nodos expandidos con heurística robusta ---
            nodos_explorados = 0
            try:
                stats = None
                # SimpleAI a veces tiene res.stats() (callable) o res.stats (dict)
                if hasattr(res, "stats"):
                    stats_attr = res.stats
                    stats = stats_attr() if callable(stats_attr) else stats_attr
                elif hasattr(res, "get_stats"):
                    stats = res.get_stats()

                if isinstance(stats, dict):
                    # probar varias claves comunes
                    for key in ("expanded", "expanded_nodes", "expanded_count",
                                "nodes_expanded", "expanded_n", "visited",
                                "explored"):
                        if key in stats:
                            try:
                                nodos_explorados = int(stats[key])
                                break
                            except Exception:
                                continue
                    # fallback: buscar el primer entero en dict.values()
                    if nodos_explorados == 0:
                        for v in stats.values():
                            if isinstance(v, int):
                                nodos_explorados = v
                                break
            except Exception:
                nodos_explorados = 0

            if ruta_nodos:
                longitud = calcular_longitud_ruta(grafo, ruta_nodos)
                encontrada = True
            else:
                longitud = None
                encontrada = False

            return {
                'tiempo': tiempo,
                'longitud': longitud,
                'encontrada': encontrada,
                'nodos_explorados': nodos_explorados,
                'nodos_en_ruta': nodos_en_ruta
            }

        except TimeoutError:
            return {
                'tiempo': None,
                'longitud': None,
                'encontrada': False,
                'nodos_explorados': 0,
                'nodos_en_ruta': 0,
                'error': f"TIMEOUT ({timeout}s)"
            }
        except Exception as e:
            return {
                'tiempo': None,
                'longitud': None,
                'encontrada': False,
                'nodos_explorados': 0,
                'nodos_en_ruta': 0,
                'error': repr(e)
            }

    # Ejecutar algoritmos (igual que antes)
    resultados['BFS'] = run_and_measure(breadth_first, 'BFS')
    resultados['DFS'] = run_and_measure(depth_first, 'DFS')
    resultados['UCS'] = run_and_measure(uniform_cost, 'UCS')

    # IDDFS (tu implementación local)
    try:
        inicio = time.time()
        ruta, nodos_iddfs = iddfs_custom(grafo, nodo_inicio, nodo_meta, max_depth=30)
        tiempo = time.time() - inicio

        if ruta:
            longitud = calcular_longitud_ruta(grafo, ruta)
            encontrada = True
        else:
            longitud = None
            encontrada = False

        resultados['IDDFS'] = {
            'tiempo': tiempo,
            'longitud': longitud,
            'encontrada': encontrada,
            'nodos_explorados': nodos_iddfs,
            'nodos_en_ruta': len(ruta) if ruta else 0
        }

    except Exception as e:
        resultados['IDDFS'] = {
            'tiempo': None,
            'longitud': None,
            'encontrada': False,
            'nodos_explorados': 0,
            'nodos_en_ruta': 0,
            'error': repr(e)
        }

    resultados['A*'] = run_and_measure(astar, 'A*')

    return resultados

# ============================================================================
# MAIN - Programa principal
# ============================================================================
def main():
    print("=" * 80)
    print("COMPONENTE 2: EVALUACIÓN DE ALGORITMOS DE BÚSQUEDA DE RUTAS")
    print("=" * 80)

    # 1. Descargar grafo de Guadalajara
    print("\n[1] Descargando grafo de Guadalajara...")
    center_point = (20.6737, -103.3627)  # Glorieta Chapultepec
    G = ox.graph_from_point(center_point, dist=7000, network_type='drive')
    print(f"    ✓ Grafo descargado: {len(G.nodes)} nodos, {len(G.edges)} aristas")

    # Fijar semilla para reproducibilidad
    np.random.seed(42)

    # 2. Seleccionar parejas de nodos por rangos de distancia
    print("\n[2] Seleccionando parejas de nodos...")
    
    print("    - Parejas cortas (< 1000m)...")
    parejas_cortas = seleccionar_parejas_por_distancia(G, 0, 1000, 5)
    
    print("    - Parejas medias (1000-5000m)...")
    parejas_medias = seleccionar_parejas_por_distancia(G, 1000, 5000, 5)
    
    print("    - Parejas largas (> 5000m)...")
    parejas_largas = seleccionar_parejas_por_distancia(G, 5000, 15000, 5)

    # Organizar grupos de parejas
    todos_los_grupos = [
        ("Cortas (<1000m)", parejas_cortas),
        ("Medias (1000-5000m)", parejas_medias),
        ("Largas (>5000m)", parejas_largas)
    ]

    resultados_completos = []

    # 3. Evaluar algoritmos para cada grupo
    for nombre_grupo, parejas in todos_los_grupos:
        print(f"\n[3] Evaluando {nombre_grupo}...")
        print("    " + "-" * 70)
        
        for idx, (nodo1, nodo2, dist) in enumerate(parejas, 1):
            print(f"\n    Pareja {idx}: Distancia geodésica = {dist:.2f}m")
            resultados = ejecutar_algoritmos(G, nodo1, nodo2)
            
            for alg, res in resultados.items():
                if res.get('tiempo') is not None and res.get('encontrada'):
                    longitud_str = f"{res['longitud']:.2f}m" if res['longitud'] is not None else "N/A"
                    nodos_ruta = res.get('nodos_en_ruta', 0)
                    nodos_str = f"{nodos_ruta} nodos"
                    print(f"      {alg:<10} | Tiempo: {res['tiempo']*1000:>8.3f}ms | "
                        f"Longitud: {longitud_str:>12} | {nodos_str}")
                elif res.get('error'):
                    print(f"      {alg:<10} | ERROR: {res.get('error')}")
                else:
                    print(f"      {alg:<10} | No encontró ruta")
                
                # Guardar resultados para análisis
                resultados_completos.append({
                    'Grupo': nombre_grupo,
                    'Pareja': idx,
                    'Distancia_Geodesica': dist,
                    'Algoritmo': alg,
                    'Tiempo_ms': res['tiempo'] * 1000 if res['tiempo'] else None,
                    'Longitud_Ruta': res['longitud'],
                    'Encontrada': res['encontrada'],
                    'Nodos_Ruta': res.get('nodos_en_ruta', 0)
                })

    # 4. Análisis de resultados
    df = pd.DataFrame(resultados_completos)
    
    if df.empty:
        print("\n⚠️  ERROR: No se encontraron parejas de nodos válidas.")
        return
    
    df_valid = df[df['Tiempo_ms'].notna()]
    
    if df_valid.empty:
        print("\n⚠️  ERROR: Ningún algoritmo pudo encontrar rutas.")
        return

    print("\n" + "=" * 80)
    print("ANÁLISIS DE RESULTADOS")
    print("=" * 80)
    
    print("\nTiempo promedio (ms) por algoritmo y grupo de distancia:")
    pivot_tiempo = df_valid.pivot_table(
        values='Tiempo_ms',
        index='Algoritmo',
        columns='Grupo',
        aggfunc='mean'
    )
    print(pivot_tiempo.to_string())

    print("\n\nLongitud promedio de ruta (m) por algoritmo y grupo:")
    pivot_longitud = df_valid[df_valid['Longitud_Ruta'].notna()].pivot_table(
        values='Longitud_Ruta',
        index='Algoritmo',
        columns='Grupo',
        aggfunc='mean'
    )
    print(pivot_longitud.to_string())

    print("\n\nTiempo promedio general por algoritmo:")
    promedio_gral = df_valid.groupby('Algoritmo')['Tiempo_ms'].mean().sort_values()
    for alg, tiempo in promedio_gral.items():
        print(f"  {alg:<10} {tiempo:>10.3f} ms")

    # 5. Visualización
    print("\n[4] Generando visualizaciones...")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Gráfico 1: Tiempo por algoritmo y grupo
    ax1 = axes[0, 0]
    pivot_tiempo.T.plot(kind='bar', ax=ax1, width=0.8)
    ax1.set_title('Tiempo de ejecución por algoritmo y grupo de distancia',
                  fontsize=12, fontweight='bold')
    ax1.set_xlabel('Grupo de distancia', fontsize=10)
    ax1.set_ylabel('Tiempo (ms)', fontsize=10)
    ax1.legend(title='Algoritmo', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.tick_params(axis='x', rotation=45)

    # Gráfico 2: Tiempo promedio general
    ax2 = axes[0, 1]
    promedio_gral.plot(kind='barh', ax=ax2, color='skyblue', edgecolor='black')
    ax2.set_title('Tiempo promedio general por algoritmo',
                  fontsize=12, fontweight='bold')
    ax2.set_xlabel('Tiempo (ms)', fontsize=10)
    ax2.set_ylabel('Algoritmo', fontsize=10)
    ax2.grid(True, alpha=0.3, axis='x')

    # Gráfico 3: Longitud de ruta vs Tiempo
    ax3 = axes[1, 0]
    for alg in df_valid['Algoritmo'].unique():
        data = df_valid[df_valid['Algoritmo'] == alg]
        ax3.scatter(data['Longitud_Ruta'], data['Tiempo_ms'],
                   label=alg, alpha=0.6, s=50)
    ax3.set_title('Longitud de ruta vs Tiempo de ejecución',
                  fontsize=12, fontweight='bold')
    ax3.set_xlabel('Longitud de ruta (m)', fontsize=10)
    ax3.set_ylabel('Tiempo (ms)', fontsize=10)
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Gráfico 4: Distribución de tiempos (boxplot)
    ax4 = axes[1, 1]
    df_valid.boxplot(column='Tiempo_ms', by='Algoritmo', ax=ax4)
    ax4.set_title('Distribución de tiempos por algoritmo',
                  fontsize=12, fontweight='bold')
    ax4.set_xlabel('Algoritmo', fontsize=10)
    ax4.set_ylabel('Tiempo (ms)', fontsize=10)
    plt.sca(ax4)
    plt.xticks(rotation=45)
    plt.suptitle('')  # Remover título automático de pandas

    plt.tight_layout()
    plt.savefig('comparacion_algoritmos_rutas.png', dpi=300, bbox_inches='tight')
    print("    ✓ Gráficos guardados como 'comparacion_algoritmos_rutas.png'")

    # 6. Recomendación final
    mejor_algoritmo = promedio_gral.index[0]
    mejor_tiempo = promedio_gral.iloc[0]
    
    print("\n" + "=" * 80)
    print("RECOMENDACIÓN FINAL")
    print("=" * 80)
    print(f"\n🎯 Algoritmo recomendado: {mejor_algoritmo}")
    print(f"   Tiempo promedio: {mejor_tiempo:.3f} ms")
    print(f"\n   Justificación:")
    print(f"   - Es el algoritmo más rápido en promedio")
    print(f"   - Garantiza encontrar la ruta óptima" if mejor_algoritmo in ['A*', 'UCS'] else "")
    print(f"   - Ideal para sistemas de navegación en tiempo real")
    
    plt.show()


if __name__ == "__main__":
    main()
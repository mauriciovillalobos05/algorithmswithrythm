import osmnx as ox
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from scipy.spatial import Voronoi, voronoi_plot_2d
import geopy.distance
from kdtree import KDTree, latlon_a_utm, obtener_coordenadas_nodo
from route_planner import RutaGrafoProblem, to_native, calcular_longitud_ruta
from simpleai.search import astar


# HOSPITALES EN GUADALAJARA
HOSPITALES_GUADALAJARA = [
    ("Hospital Civil Fray Antonio Alcalde", 20.6685, -103.3361),
    ("Hospital Civil Juan I. Menchaca", 20.6595, -103.3289),
    ("Hospital General de Occidente", 20.6234, -103.4156),
    ("Hospital Ángel Leaño", 20.7421, -103.4589),
    ("Hospital San Javier", 20.6729, -103.3913),
    ("Hospital México Americano", 20.6794, -103.3871),
    ("Hospital Real San José", 20.6581, -103.3762),
    ("Hospital Bernardette", 20.7048, -103.3695),
    ("Hospital Puerta de Hierro", 20.6398, -103.4298),
    ("Hospital Santa Margarita", 20.6945, -103.3521)
]


class VoronoiHospitales:
    def __init__(self, hospitales_coords, grafo, kd_tree):
        """
        hospitales_coords: lista de (nombre, lat, lon)
        grafo: grafo de OSMnx
        kd_tree: KDTree construido con los nodos del grafo
        """
        self.hospitales_coords = hospitales_coords
        self.grafo = grafo
        self.kd_tree = kd_tree
        self.hospitales_nodos = []
        self.hospitales_utm = []
        self.voronoi = None
        
    def encontrar_nodos_hospitales(self):
        """Encuentra el nodo más cercano del grafo para cada hospital"""
        print("\n[2] Encontrando nodos más cercanos a hospitales...")
        print(f"    {'Hospital':<40} {'Nodo ID':<15} {'Distancia (m)':<15}")
        print("    " + "-" * 70)
        
        for nombre, lat, lon in self.hospitales_coords:
            x, y = latlon_a_utm(lat, lon)
            nodo_id, distancia = self.kd_tree.buscar_mas_cercano((x, y))
            self.hospitales_nodos.append((nombre, nodo_id))
            self.hospitales_utm.append((x, y))
            print(f"    {nombre:<40} {nodo_id:<15} {distancia:<15.2f}")
        
        print(f"\n    ✓ {len(self.hospitales_nodos)} hospitales mapeados a nodos del grafo")
    
    def construir_voronoi(self):
        """Construye el diagrama de Voronoi con las coordenadas UTM de los hospitales"""
        print("\n[3] Construyendo diagrama de Voronoi...")
        
        inicio = time.time()
        puntos = np.array(self.hospitales_utm)
        self.voronoi = Voronoi(puntos)
        tiempo = time.time() - inicio
        
        print(f"    ✓ Diagrama de Voronoi construido en {tiempo:.4f} segundos")
        print(f"    ✓ {len(self.voronoi.regions)} regiones generadas")
        print(f"    ✓ {len(self.voronoi.vertices)} vértices de Voronoi")
        
        return tiempo
    
    def encontrar_hospital_mas_cercano(self, lat, lon):
        """
        Encuentra el hospital más cercano a una ubicación dada
        usando el diagrama de Voronoi
        """
        x, y = latlon_a_utm(lat, lon)
        punto = np.array([x, y])
        
        # Encontrar el punto (hospital) más cercano
        distancias = np.linalg.norm(self.voronoi.points - punto, axis=1)
        idx_hospital = np.argmin(distancias)
        
        nombre_hospital = self.hospitales_coords[idx_hospital][0]
        nodo_hospital = self.hospitales_nodos[idx_hospital][1]
        
        return nombre_hospital, nodo_hospital, idx_hospital
    
    def visualizar_voronoi(self, casos_emergencia=None):
        """Visualiza el diagrama de Voronoi con los hospitales y casos de emergencia"""
        fig, ax = plt.subplots(figsize=(14, 12))
        
        # Graficar el diagrama de Voronoi
        voronoi_plot_2d(self.voronoi, ax=ax, show_vertices=False, 
                       line_colors='blue', line_width=2, line_alpha=0.6,
                       point_size=0)
        
        # Colores para cada región
        colores = plt.cm.tab10(np.linspace(0, 1, len(self.hospitales_coords)))
        
        # Rellenar las regiones de Voronoi
        for idx, region_idx in enumerate(self.voronoi.point_region):
            region = self.voronoi.regions[region_idx]
            if not -1 in region and len(region) > 0:
                polygon_vertices = [self.voronoi.vertices[i] for i in region]
                polygon = MplPolygon(polygon_vertices, alpha=0.2, 
                                    facecolor=colores[idx], edgecolor='none')
                ax.add_patch(polygon)
        
        # Marcar los hospitales
        for idx, (x, y) in enumerate(self.hospitales_utm):
            nombre = self.hospitales_coords[idx][0]
            ax.plot(x, y, 'r^', markersize=15, markeredgecolor='darkred', 
                   markeredgewidth=2, label='Hospital' if idx == 0 else '')
            ax.text(x, y + 200, nombre.split()[1], fontsize=8, 
                   ha='center', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        # Marcar casos de emergencia si se proporcionan
        if casos_emergencia:
            for idx, caso in enumerate(casos_emergencia):
                nombre_lugar, lat, lon, _, _ = caso
                x, y = latlon_a_utm(lat, lon)
                ax.plot(x, y, 'go', markersize=10, markeredgecolor='darkgreen',
                       markeredgewidth=2, label='Emergencia' if idx == 0 else '')
                ax.text(x, y - 200, f"E{idx+1}", fontsize=9,
                       ha='center', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.8))
        
        ax.set_xlabel('Coordenada X (UTM)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Coordenada Y (UTM)', fontsize=12, fontweight='bold')
        ax.set_title('Diagrama de Voronoi - Áreas de Influencia de Hospitales\nGuadalajara, Jalisco',
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        plt.savefig('voronoi_hospitales.png', dpi=300, bbox_inches='tight')
        print("    ✓ Visualización guardada como 'voronoi_hospitales.png'")
        
        return fig, ax


def encontrar_ruta_hospital(grafo, kd_tree, lat_emergencia, lon_emergencia, 
                            nodo_hospital):
    """Encuentra la ruta desde una emergencia hasta un hospital"""
    # Encontrar nodo más cercano a la emergencia
    x_emerg, y_emerg = latlon_a_utm(lat_emergencia, lon_emergencia)
    nodo_emergencia, dist_nodo = kd_tree.buscar_mas_cercano((x_emerg, y_emerg))
    
    # Calcular ruta con A*
    problema = RutaGrafoProblem(grafo, nodo_emergencia, nodo_hospital)
    
    inicio = time.time()
    resultado = astar(problema, graph_search=True)
    tiempo = time.time() - inicio
    
    # Parsear ruta
    ruta = []
    if resultado and hasattr(resultado, 'path'):
        steps = resultado.path()
        for s in steps:
            if isinstance(s, tuple) and len(s) == 2:
                ruta.append(to_native(s[1]))
            else:
                ruta.append(to_native(s))
    
    # Calcular longitud de la ruta
    longitud = calcular_longitud_ruta(grafo, ruta) if ruta else None
    
    return {
        'nodo_emergencia': nodo_emergencia,
        'nodo_hospital': nodo_hospital,
        'ruta': ruta,
        'longitud': longitud,
        'tiempo_calculo': tiempo,
        'num_nodos': len(ruta) if ruta else 0
    }


# CASOS DE EMERGENCIA DE PRUEBA
CASOS_EMERGENCIA = [
    ("Centro Histórico", 20.6770, -103.3470),
    ("Chapalita", 20.6796, -103.3950),
    ("Zapopan Centro", 20.7208, -103.3932),
    ("Tlaquepaque Centro", 20.6413, -103.3123),
    ("Plaza del Sol", 20.6588, -103.3788),
    ("Glorieta Colón", 20.6738, -103.3627),
    ("Zona Industrial", 20.6892, -103.3245),
    ("López Mateos Sur", 20.6234, -103.3567),
    ("Av. Patria", 20.7121, -103.4156),
    ("Periférico Sur", 20.6145, -103.3912)
]


def main():
    print("=" * 80)
    print("COMPONENTE 3: SERVICIO DE EMERGENCIAS CON VORONOI")
    print("=" * 80)
    
    # 1. Descargar grafo
    print("\n[1] Descargando grafo de Guadalajara...")
    center_point = (20.6737, -103.3627)
    G = ox.graph_from_point(center_point, dist=10000, network_type='drive')
    print(f"    ✓ Grafo descargado: {len(G.nodes)} nodos, {len(G.edges)} aristas")
    
    # 1.1 Construir KD-Tree
    print("\n    Construyendo KD-Tree para búsqueda eficiente...")
    puntos_utm = []
    for node_id in G.nodes():
        lat, lon = obtener_coordenadas_nodo(G, node_id)
        x, y = latlon_a_utm(lat, lon)
        puntos_utm.append(((x, y), node_id))
    
    kd_tree = KDTree(k=2)
    kd_tree.construir(puntos_utm)
    print(f"    ✓ KD-Tree construido con {len(puntos_utm)} nodos")
    
    # 2. Crear sistema de Voronoi
    sistema_voronoi = VoronoiHospitales(HOSPITALES_GUADALAJARA, G, kd_tree)
    sistema_voronoi.encontrar_nodos_hospitales()
    tiempo_voronoi = sistema_voronoi.construir_voronoi()
    
    # 3. Procesar casos de emergencia
    print("\n[4] Procesando casos de emergencia...")
    print("    " + "=" * 76)
    
    resultados_emergencias = []
    tiempos_busqueda = []
    tiempos_ruta = []
    
    for idx, (nombre, lat, lon) in enumerate(CASOS_EMERGENCIA, 1):
        print(f"\n    CASO {idx}: {nombre}")
        print("    " + "-" * 76)
        
        # Encontrar hospital más cercano con Voronoi
        inicio_voronoi = time.time()
        hospital, nodo_hosp, idx_hosp = sistema_voronoi.encontrar_hospital_mas_cercano(lat, lon)
        tiempo_voronoi_busq = (time.time() - inicio_voronoi) * 1000
        tiempos_busqueda.append(tiempo_voronoi_busq)
        
        print(f"      Hospital asignado: {hospital}")
        print(f"      Tiempo de asignación: {tiempo_voronoi_busq:.4f} ms")
        
        # Calcular ruta
        print(f"      Calculando ruta óptima...")
        resultado_ruta = encontrar_ruta_hospital(G, kd_tree, lat, lon, nodo_hosp)
        tiempos_ruta.append(resultado_ruta['tiempo_calculo'] * 1000)
        
        if resultado_ruta['ruta']:
            print(f"      ✓ Ruta encontrada:")
            print(f"        - Longitud: {resultado_ruta['longitud']:.2f} metros")
            print(f"        - Nodos en ruta: {resultado_ruta['num_nodos']}")
            print(f"        - Tiempo de cálculo: {resultado_ruta['tiempo_calculo']*1000:.3f} ms")
            print(f"        - Tiempo estimado: {resultado_ruta['longitud']/8.33:.1f} segundos (30 km/h)")
        else:
            print(f"      ✗ No se pudo encontrar ruta")
        
        resultados_emergencias.append({
            'caso': nombre,
            'lat': lat,
            'lon': lon,
            'hospital': hospital,
            'tiempo_asignacion_ms': tiempo_voronoi_busq,
            'longitud_ruta': resultado_ruta['longitud'],
            'tiempo_calculo_ms': resultado_ruta['tiempo_calculo'] * 1000,
            'nodos_ruta': resultado_ruta['num_nodos']
        })
    
    # 4. Visualización
    print("\n[5] Generando visualizaciones...")
    casos_viz = [(c['caso'], c['lat'], c['lon'], c['hospital'], c['longitud_ruta']) 
                 for c in resultados_emergencias]
    sistema_voronoi.visualizar_voronoi(casos_viz)
    
    # 5. Gráficos de análisis
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Gráfico 1: Distribución de hospitales asignados
    ax1 = axes[0, 0]
    hospitales_asignados = [r['hospital'] for r in resultados_emergencias]
    hospital_counts = {}
    for h in hospitales_asignados:
        nombre_corto = h.split()[1] if len(h.split()) > 1 else h
        hospital_counts[nombre_corto] = hospital_counts.get(nombre_corto, 0) + 1
    
    ax1.bar(range(len(hospital_counts)), list(hospital_counts.values()), 
           color='steelblue', edgecolor='black', linewidth=1.5)
    ax1.set_xticks(range(len(hospital_counts)))
    ax1.set_xticklabels(list(hospital_counts.keys()), rotation=45, ha='right')
    ax1.set_ylabel('Número de casos asignados', fontsize=11)
    ax1.set_title('Distribución de Casos por Hospital', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Gráfico 2: Tiempos de procesamiento
    ax2 = axes[0, 1]
    x = range(len(CASOS_EMERGENCIA))
    ax2.plot(x, tiempos_busqueda, 'o-', label='Asignación (Voronoi)', 
            linewidth=2, markersize=8, color='#2ecc71')
    ax2.plot(x, tiempos_ruta, 's-', label='Cálculo de ruta (A*)', 
            linewidth=2, markersize=8, color='#e74c3c')
    ax2.set_xlabel('Caso de emergencia', fontsize=11)
    ax2.set_ylabel('Tiempo (ms)', fontsize=11)
    ax2.set_title('Tiempos de Procesamiento por Caso', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # Gráfico 3: Longitudes de ruta
    ax3 = axes[1, 0]
    longitudes = [r['longitud_ruta'] for r in resultados_emergencias if r['longitud_ruta']]
    casos_validos = [r['caso'] for r in resultados_emergencias if r['longitud_ruta']]
    
    colores_barras = plt.cm.viridis(np.linspace(0.3, 0.9, len(longitudes)))
    bars = ax3.barh(range(len(longitudes)), longitudes, color=colores_barras, 
                    edgecolor='black', linewidth=1.5)
    ax3.set_yticks(range(len(casos_validos)))
    ax3.set_yticklabels(casos_validos, fontsize=9)
    ax3.set_xlabel('Longitud de ruta (metros)', fontsize=11)
    ax3.set_title('Distancia al Hospital Asignado', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='x')
    
    # Gráfico 4: Estadísticas generales
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    stats_text = f"""
    ESTADÍSTICAS DEL SISTEMA
    {'='*40}
    
    Hospitales registrados:     {len(HOSPITALES_GUADALAJARA)}
    Casos procesados:           {len(CASOS_EMERGENCIA)}
    
    TIEMPOS DE CONSTRUCCIÓN:
    • Voronoi:                  {tiempo_voronoi*1000:.3f} ms
    
    TIEMPOS PROMEDIO:
    • Asignación (Voronoi):     {np.mean(tiempos_busqueda):.4f} ms
    • Cálculo de ruta (A*):     {np.mean(tiempos_ruta):.3f} ms
    • Total por caso:           {np.mean(tiempos_busqueda)+np.mean(tiempos_ruta):.3f} ms
    
    DISTANCIAS:
    • Promedio a hospital:      {np.mean(longitudes):.0f} metros
    • Mínima:                   {np.min(longitudes):.0f} metros
    • Máxima:                   {np.max(longitudes):.0f} metros
    
    EFICIENCIA:
    • Casos con ruta exitosa:   {len(longitudes)}/{len(CASOS_EMERGENCIA)}
    • Tasa de éxito:            {len(longitudes)/len(CASOS_EMERGENCIA)*100:.1f}%
    """
    
    ax4.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
            family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('analisis_emergencias.png', dpi=300, bbox_inches='tight')
    print("    ✓ Análisis guardado como 'analisis_emergencias.png'")
    
    # 6. Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DEL SERVICIO DE EMERGENCIAS")
    print("=" * 80)
    print(f"\nTiempo de construcción del diagrama de Voronoi: {tiempo_voronoi*1000:.3f} ms")
    print(f"Tiempo promedio de asignación de hospital:      {np.mean(tiempos_busqueda):.4f} ms")
    print(f"Tiempo promedio de cálculo de ruta:             {np.mean(tiempos_ruta):.3f} ms")
    print(f"Tiempo total promedio por emergencia:           {np.mean(tiempos_busqueda)+np.mean(tiempos_ruta):.3f} ms")
    print(f"\nDistancia promedio al hospital más cercano:     {np.mean(longitudes):.0f} metros")
    print(f"Distancia mínima:                                {np.min(longitudes):.0f} metros")
    print(f"Distancia máxima:                                {np.max(longitudes):.0f} metros")
    
    
    plt.show()


if __name__ == "__main__":
    main()

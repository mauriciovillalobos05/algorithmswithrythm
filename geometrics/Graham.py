#NOTE: THIS CODE WAS GENERATED TO BE EXECUTED IN GOOGLE COLAB

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from IPython.display import HTML

# ===========================================
#      1. LISTA DE PUNTOS
# ===========================================
puntos = np.array([
    (-19, -17), (-15, 3), (-12, 11), (-8, -5), (-7, 14),
    (-3, -9), (-1, 0), (2, 18), (4, -13), (6, 7),
    (9, -16), (11, 5), (13, -2), (16, 12), (18, -7),
    (-20, 6), (-14, -18), (-9, 9), (-4, -12), (-2, 15),
    (1, -14), (3, 10), (7, -8), (12, 19), (17, -4)
])

# ===========================================
#      2. FUNCIONES DE GRAHAM SCAN
# ===========================================
def orientacion(p, q, r):
    return (q[0] - p[0]) * (r[1] - p[1]) - \
           (q[1] - p[1]) * (r[0] - p[0])

def distancia(p, q):
    return (p[0] - q[0])**2 + (p[1] - q[1])**2

def graham_scan(puntos):
    pasos = []
    p0 = min(puntos, key=lambda p: (p[1], p[0]))
    pasos.append(("pivote", [p0]))
    
    pts = [p for p in puntos if tuple(p) != tuple(p0)]
    pts.sort(key=lambda p: (np.arctan2(p[1]-p0[1], p[0]-p0[0]), distancia(p, p0)))
    pasos.append(("ordenados", [p0] + pts))
    
    casco = [p0, pts[0]]
    
    for p in pts[1:]:
        pasos.append(("evaluando", [p], casco.copy()))
        
        while len(casco) >= 2 and orientacion(casco[-2], casco[-1], p) <= 0:
            eliminado = casco.pop()
            pasos.append(("pop", [eliminado], casco.copy()))
        
        casco.append(p)
        pasos.append(("push", casco.copy()))
    
    pasos.append(("final", casco.copy()))
    return pasos

pasos = graham_scan(puntos)

# ===========================================
#      3. ANIMACIÓN
# ===========================================
plt.close('all')  # Cerrar figuras previas
fig, ax = plt.subplots(figsize=(7, 7))
ax.set_xlim(min(puntos[:,0]) - 2, max(puntos[:,0]) + 2)
ax.set_ylim(min(puntos[:,1]) - 2, max(puntos[:,1]) + 2)
ax.set_aspect('equal')

line, = ax.plot([], [], 'r-', lw=2)
titulo = ax.text(0.5, 1.03, "", ha="center", transform=ax.transAxes, fontsize=14)

def animar(i):
    # Limpiar solo los scatters anteriores, no la línea
    while len(ax.collections) > 0:
        ax.collections[0].remove()
    
    # Dibujar todos los puntos en negro
    ax.scatter(puntos[:,0], puntos[:,1], color='black', s=50, zorder=1)
    
    tipo = pasos[i][0]
    titulo.set_text(f"Paso {i+1}/{len(pasos)}: {tipo}")
    
    # Manejar diferentes tipos de pasos
    if tipo == "pivote":
        pts = np.array(pasos[i][1])
        ax.scatter(pts[:,0], pts[:,1], color='red', s=150, marker='*', zorder=3)
        line.set_data([], [])
    
    elif tipo == "ordenados":
        pts = np.array(pasos[i][1])
        ax.scatter(pts[0][0], pts[0][1], color='red', s=150, marker='*', zorder=3)
        ax.scatter(pts[1:,0], pts[1:,1], color='orange', s=80, zorder=2)
        line.set_data([], [])
    
    elif tipo == "evaluando":
        pt_eval = np.array(pasos[i][1])
        casco = np.array(pasos[i][2])
        ax.scatter(pt_eval[:,0], pt_eval[:,1], color='blue', s=150, marker='o', zorder=3)
        if len(casco) > 1:
            casco_cerrado = np.vstack([casco, casco[0]])
            line.set_data(casco_cerrado[:,0], casco_cerrado[:,1])
        else:
            line.set_data([], [])
    
    elif tipo == "pop":
        eliminado = np.array(pasos[i][1])
        casco = np.array(pasos[i][2])
        ax.scatter(eliminado[:,0], eliminado[:,1], color='red', s=150, marker='x', zorder=3)
        if len(casco) > 1:
            casco_cerrado = np.vstack([casco, casco[0]])
            line.set_data(casco_cerrado[:,0], casco_cerrado[:,1])
        else:
            line.set_data([], [])
    
    elif tipo == "push":
        casco = np.array(pasos[i][1])
        if len(casco) > 1:
            casco_cerrado = np.vstack([casco, casco[0]])
            line.set_data(casco_cerrado[:,0], casco_cerrado[:,1])
        else:
            line.set_data([], [])
    
    elif tipo == "final":
        casco = np.array(pasos[i][1])
        ax.scatter(casco[:,0], casco[:,1], color='green', s=100, zorder=2)
        if len(casco) > 1:
            casco_cerrado = np.vstack([casco, casco[0]])
            line.set_data(casco_cerrado[:,0], casco_cerrado[:,1])
    
    return [line, titulo]

ani = animation.FuncAnimation(
    fig, animar,
    frames=len(pasos),
    interval=800,
    repeat=True,
    blit=False
)

HTML(ani.to_jshtml())
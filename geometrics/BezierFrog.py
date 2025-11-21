import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Arc, PathPatch
from matplotlib.path import Path

fig, ax = plt.subplots(figsize=(6, 6))


def bezier_patch(points, closed=False, color="green", linewidth=2, fill=False):
    """points: [ (x0,y0), (c1x,c1y), (c2x,c2y), (x1,y1) ]"""
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    if closed:
        codes.append(Path.CLOSEPOLY)
        points.append(points[0])
    path = Path(points, codes)
    patch = PathPatch(path, facecolor="none", edgecolor=color, linewidth=linewidth)
    ax.add_patch(patch)


# -----------------------------
# CUERPO (curvas Bézier)
# -----------------------------
bezier_patch([
    (0, 0), (-2, 3), (2, 3), (0, 0)   # curva superior
], color="green")

bezier_patch([
    (0, -1), (-2, -3), (2, -3), (0, -1)  # curva inferior
], color="green")

# -----------------------------
# PATAS TRASERAS
# -----------------------------
bezier_patch([
    (-1.5, -0.5), (-3, -1), (-3, -2), (-1.5, -1.5)
], color="green")

bezier_patch([
    (1.5, -0.5), (3, -1), (3, -2), (1.5, -1.5)
], color="green")

# -----------------------------
# PATAS DELANTERAS
# -----------------------------
bezier_patch([
    (-1, -0.2), (-2, 0), (-2, -1), (-1, -1)
], color="green")

bezier_patch([
    (1, -0.2), (2, 0), (2, -1), (1, -1)
], color="green")


# -----------------------------
# OJOS (elipses)
# -----------------------------
eye1 = Ellipse((-0.7, 1.5), width=0.6, height=0.9, edgecolor="black", facecolor="white", linewidth=2)
eye2 = Ellipse((0.7, 1.5), width=0.6, height=0.9, edgecolor="black", facecolor="white", linewidth=2)
pupil1 = Ellipse((-0.7, 1.55), width=0.2, height=0.3, color="black")
pupil2 = Ellipse((0.7, 1.55), width=0.2, height=0.3, color="black")

ax.add_patch(eye1)
ax.add_patch(eye2)
ax.add_patch(pupil1)
ax.add_patch(pupil2)

# -----------------------------
# BOCA (arco)
# -----------------------------
mouth = Arc((0, 0.5), width=1.5, height=0.8, theta1=200, theta2=340, linewidth=2)
ax.add_patch(mouth)

# -----------------------------
# DEDOS (líneas simples)
# -----------------------------
fingers = [
    [(-1.5, -1.5), (-2, -2)], [(-1.5, -1.5), (-1, -2)],  # izquierda atrás
    [(1.5, -1.5), (2, -2)], [(1.5, -1.5), (1, -2)],      # derecha atrás
]

for f in fingers:
    xs, ys = zip(*f)
    ax.plot(xs, ys, color="green", linewidth=2)

# Ajustes finales
ax.set_xlim(-4, 4)
ax.set_ylim(-4, 4)
ax.set_aspect("equal")
ax.axis("off")

plt.show()

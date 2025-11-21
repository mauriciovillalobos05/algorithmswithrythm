import numpy as np
import matplotlib.pyplot as plt


# ============================================================
#          CLASE DE TRANSFORMACIÓN AFIN 4x4 EN 3D
# ============================================================

class AffineTransformation:
    def __init__(self):
        self.M = np.eye(4)

    def _apply_left(self, T):
        self.M = T @ self.M

    @staticmethod
    def _normalize(v):
        return v / np.linalg.norm(v)

    # ---------------- Escalamiento ----------------
    def add_scaling(self, sx, sy, sz):
        T = np.array([
            [sx, 0,  0, 0],
            [0, sy,  0, 0],
            [0,  0, sz, 0],
            [0,  0,  0, 1]
        ])
        self._apply_left(T)

    # ---------------- Rotaciones por ejes ----------------
    def add_rotation_x(self, angle_rad):
        c, s = np.cos(angle_rad), np.sin(angle_rad)
        T = np.array([
            [1, 0,  0, 0],
            [0, c, -s, 0],
            [0, s,  c, 0],
            [0, 0,  0, 1]
        ])
        self._apply_left(T)

    def add_rotation_y(self, angle_rad):
        c, s = np.cos(angle_rad), np.sin(angle_rad)
        T = np.array([
            [ c, 0, s, 0],
            [ 0, 1, 0, 0],
            [-s, 0, c, 0],
            [ 0, 0, 0, 1]
        ])
        self._apply_left(T)

    def add_rotation_z(self, angle_rad):
        c, s = np.cos(angle_rad), np.sin(angle_rad)
        T = np.array([
            [c, -s, 0, 0],
            [s,  c, 0, 0],
            [0,  0, 1, 0],
            [0,  0, 0, 1]
        ])
        self._apply_left(T)

    # -------- Rotación alrededor de un vector unitario -------
    def add_rotation_axis(self, axis, angle_rad):
        axis = self._normalize(np.array(axis))
        x, y, z = axis
        c, s = np.cos(angle_rad), np.sin(angle_rad)
        C = 1 - c

        T = np.array([
            [c + x*x*C,     x*y*C - z*s, x*z*C + y*s, 0],
            [y*x*C + z*s,   c + y*y*C,   y*z*C - x*s, 0],
            [z*x*C - y*s,   z*y*C + x*s, c + z*z*C,   0],
            [0, 0, 0, 1]
        ])
        self._apply_left(T)

    # ------------------ Cizallamientos ------------------
    def add_shear(self, xy=0, xz=0, yx=0, yz=0, zx=0, zy=0):
        T = np.array([
            [1,  xy, xz, 0],
            [yx, 1,  yz, 0],
            [zx, zy, 1,  0],
            [0,  0,  0,  1]
        ])
        self._apply_left(T)

    # ----------------- Traslación ------------------------
    def add_translation(self, tx, ty, tz):
        T = np.array([
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1]
        ])
        self._apply_left(T)

    # --------------- Transformar puntos -------------------
    def transform_points(self, pts):
        pts = np.array(pts)
        n = pts.shape[0]
        homo = np.hstack([pts, np.ones((n,1))])
        res = (self.M @ homo.T).T
        return res[:, :3]

    # ----------- Transformar puntos con la inversa --------
    def inverse_transform_points(self, pts):
        inv = np.linalg.inv(self.M)
        pts = np.array(pts)
        n = pts.shape[0]
        homo = np.hstack([pts, np.ones((n,1))])
        res = (inv @ homo.T).T
        return res[:, :3]

    def get_matrix(self):
        return self.M.copy()

    def get_inverse_matrix(self):
        return np.linalg.inv(self.M)


# ============================================================
#                  BLOQUE DE PRUEBAS
# ============================================================

# 1. Generar 100 puntos aleatorios
np.random.seed(0)
points = np.random.uniform(-5, 5, size=(100, 3))

# 2. Crear transformación compleja
T = AffineTransformation()
T.add_scaling(1.2, 0.8, 1.5)
T.add_rotation_axis([1, 1, 1], np.pi / 5)
T.add_shear(xy=0.3, yz=0.1)
T.add_translation(3, -2, 1)

# 3. Transformar y recuperar
transformed = T.transform_points(points)
recovered = T.inverse_transform_points(transformed)

# 4. Medir error numérico
error = np.linalg.norm(points - recovered, axis=1)
print("Error promedio:", error.mean())
print("Error máximo:", error.max())

# 5. Graficar puntos originales y transformados
fig = plt.figure(figsize=(12,6))

ax1 = fig.add_subplot(121, projection='3d')
ax1.scatter(points[:,0], points[:,1], points[:,2])
ax1.set_title("Original Points")

ax2 = fig.add_subplot(122, projection='3d')
ax2.scatter(transformed[:,0], transformed[:,1], transformed[:,2])
ax2.set_title("Transformed Points")

plt.show()

# 6. Graficar originales vs recuperados
fig = plt.figure(figsize=(12,6))

ax3 = fig.add_subplot(121, projection='3d')
ax3.scatter(points[:,0], points[:,1], points[:,2])
ax3.set_title("Original Points")

ax4 = fig.add_subplot(122, projection='3d')
ax4.scatter(recovered[:,0], recovered[:,1], recovered[:,2])
ax4.set_title("Recovered After Inverse")

plt.show()
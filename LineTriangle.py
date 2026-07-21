import math
import numpy as np
from PySide6.QtGui import  QVector3D


def round3(value):
    """Округление до 3 знаков"""
    return round(value * 1000) / 1000


class Point3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x:float = x
        self.y:float = y
        self.z:float = z
    def __str__(self):
        return f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

    @staticmethod
    def midPoint(p1, p2):
        return Point3( (p1.x+p2.x)/2., (p1.y+p2.y)/2., (p1.z+p2.z)/2. )

    @staticmethod
    def distance3d(p1, p2):
        """Расстояние между двумя точками в 3D"""
        return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)


class Line3d:
    """Трехмерная линия по 2 точкам
       вида (x-x1)/X = (y-y1)/Y = (z-z1)/Z"""
    
    def __init__(self, p1=None, p2=None):
        if p1 is None:
            p1 = Point3()
        if p2 is None:
            p2 = Point3()
            
        self.p1:Point3 = p1
        self.p2:Point3 = p2
        self.X = p2.x - p1.x
        self.Y = p2.y - p1.y
        self.Z = p2.z - p1.z
        self.length = Point3.distance3d(p1, p2)
    
    def getX(self):
        return self.X
    
    def getY(self):
        return self.Y
    
    def getZ(self):
        return self.Z


def plane_equation(p1:Point3, p2:Point3, p3:Point3):
    """Ур-е плоскости по 3 точкам вида Ax+By+Cz+D=0"""
    # Матрица a в C++ коде
    a = [
        [0, 0, 0],
        [p2.x - p1.x, p2.y - p1.y, p2.z - p1.z],
        [p3.x - p1.x, p3.y - p1.y, p3.z - p1.z]
    ]
    
    i = a[1][1] * a[2][2] - a[1][2] * a[2][1]
    j = a[1][2] * a[2][0] - a[1][0] * a[2][2]
    k = a[1][0] * a[2][1] - a[1][1] * a[2][0]
    
    A = i
    B = j
    C = k
    D = -i * p1.x - j * p1.y - k * p1.z
    
    return A, B, C, D

def plane_equation(p1:QVector3D, p2:QVector3D, p3:QVector3D):
    """Ур-е плоскости по 3 точкам вида Ax+By+Cz+D=0"""
    # Матрица a в C++ коде
    a = [
        [0, 0, 0],
        [p2.x() - p1.x(), p2.y() - p1.y(), p2.z() - p1.z()],
        [p3.x() - p1.x(), p3.y() - p1.y(), p3.z() - p1.z()]
    ]
    
    i = a[1][1] * a[2][2] - a[1][2] * a[2][1]
    j = a[1][2] * a[2][0] - a[1][0] * a[2][2]
    k = a[1][0] * a[2][1] - a[1][1] * a[2][0]
    
    A = i
    B = j
    C = k
    D = -i * p1.x() - j * p1.y() - k * p1.z()
    
    return A, B, C, D


def normalize_vector(v):
    """Normalize a vector [x, y, z] to unit length"""
    magnitude = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if magnitude < 1e-10:
        raise ValueError("Cannot normalize zero vector")
    return [v[0]/magnitude, v[1]/magnitude, v[2]/magnitude]


def dot_product(v1, v2):
    """Calculate dot product of two 3D vectors"""
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]


def cross_product(v1, v2):
    """Calculate cross product of two 3D vectors"""
    return [
        v1[1]*v2[2] - v1[2]*v2[1],
        v1[2]*v2[0] - v1[0]*v2[2],
        v1[0]*v2[1] - v1[1]*v2[0]
    ]


def create_plane_rotation_matrix(p1: Point3, p2: Point3, p3: Point3):
    """
    Create a rotation matrix that transforms from world coordinates to plane-local coordinates.
    
    Local coordinate system:
    - Origin at p1
    - X-axis along p1→p2 (normalized)
    - XY-plane contains p1, p2, p3
    - Z-axis is normal to the plane (right-hand rule)
    
    Returns:
        tuple: (rotation_matrix_3x3, translation_vector) as numpy arrays
    """
    # Vector from p1 to p2 (X-axis)
    v_x = [p2.x - p1.x, p2.y - p1.y, p2.z - p1.z]
    x_axis = normalize_vector(v_x)
    
    # Vector from p1 to p3
    v_xy = [p3.x - p1.x, p3.y - p1.y, p3.z - p1.z]
    
    # Z-axis is the normal to the plane (cross product of x and xy vectors)
    z_axis = cross_product(x_axis, v_xy)
    z_axis = normalize_vector(z_axis)
    
    # Y-axis completes the orthonormal basis (right-hand rule)
    y_axis = cross_product(z_axis, x_axis)
    y_axis = normalize_vector(y_axis)
    
    # Create rotation matrix (rows are the basis vectors)
    rotation_matrix = np.array([
        x_axis,
        y_axis,
        z_axis
    ], dtype=float)
    
    # Translation vector (origin at p1)
    translation = np.array([p1.x, p1.y, p1.z], dtype=float)
    
    return rotation_matrix, translation


def transform_to_plane_coords(point: Point3, rotation_matrix, translation):
    """
    Transform a 3D point from world coordinates to plane-local coordinates.
    
    Args:
        point: Point3 object in world coordinates
        rotation_matrix: 3x3 rotation matrix from create_plane_rotation_matrix
        translation: translation vector (p1) from create_plane_rotation_matrix
    
    Returns:
        tuple: (x_local, y_local, z_local) in plane coordinate system
    """
    # Translate point relative to p1
    point_vec = np.array([point.x, point.y, point.z]) - translation
    
    # Apply rotation (multiply by transpose of rotation matrix to get inverse rotation)
    local_coords = rotation_matrix @ point_vec
    
    return Point3(local_coords[0], local_coords[1], local_coords[2])


def transform_from_plane_coords(x_local, y_local, z_local, rotation_matrix, translation):
    """
    Transform a point from plane-local coordinates back to world coordinates.
    
    Args:
        x_local, y_local, z_local: coordinates in plane local system
        rotation_matrix: 3x3 rotation matrix from create_plane_rotation_matrix
        translation: translation vector (p1) from create_plane_rotation_matrix
    
    Returns:
        Point3: point in world coordinates
    """
    local_coords = np.array([x_local, y_local, z_local])
    
    # Apply inverse rotation (transpose of rotation matrix)
    world_vec = rotation_matrix.T @ local_coords
    
    # Add translation
    world_coords = world_vec + translation
    
    return Point3(world_coords[0], world_coords[1], world_coords[2])


class Plane:
    def __init__(self, A=None, B=None, C=None, D=None):
        self.p1:Point3 = None
        self.p2:Point3 = None
        self.p3:Point3 = None
        self.A:float = A
        self.B:float = B
        self.C:float = C
        self.D:float = D
        self.rotation_matrix = None
        self.translation = None

    def from3Points(self, p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.A, self.B, self.C, self.D = plane_equation(p1, p2, p3)
        # Pre-compute rotation matrix and translation for later use
        self.rotation_matrix, self.translation = create_plane_rotation_matrix(p1, p2, p3)
        р=0

    def getParallPlanes(self, dist:float):
        L = math.sqrt(self.A**2 + self.B**2 + self.C**2)
        self.D + dist*L
        return Plane(self.A, self.B, self.C, self.D+dist*L), Plane(self.A, self.B, self.C, self.D-dist*L)
    
    def to_local_coords(self, point: Point3):
        """
        Transform world coordinates to plane-local coordinates.
        Returns (x_local, y_local, z_local)
        """
        if self.rotation_matrix is None:
            raise ValueError("Plane coordinate system not initialized. Call from3Points() first.")
        return transform_to_plane_coords(point, self.rotation_matrix, self.translation)
    
    def from_local_coords(self, x_local, y_local, z_local):
        """
        Transform plane-local coordinates back to world coordinates.
        Returns Point3 in world coordinates.
        """
        if self.rotation_matrix is None:
            raise ValueError("Plane coordinate system not initialized. Call from3Points() first.")
        return transform_from_plane_coords(x_local, y_local, z_local, self.rotation_matrix, self.translation)
        


def line_plane_intersec(line:Line3d, pl:Plane) -> Point3:
    """Точка пересечения линии с плоскостью"""
    A, B, C, D = pl.A, pl.B, pl.C, pl.D
    
    X = line.getX()
    Y = line.getY()
    Z = line.getZ()
    
    P1 = line.p1
    x1, y1, z1 = P1.x, P1.y, P1.z
    
    # Проверка на деление на ноль
    denominator = C + (A * X) / Z + (B * Y) / Z
    if denominator == 0:
        raise ValueError("Линия параллельна плоскости или лежит в ней")

    ret = Point3()
    ret.z = ((A * (X * z1 - Z * x1)) / Z - D + (B * (Y * z1 - Z * y1)) / Z) / denominator
    ret.x = (X * ret.z - X * z1 + Z * x1) / Z
    ret.y = (Y * ret.z - Y * z1 + Z * y1) / Z
    
    return ret

"""
# Пример использования
if __name__ == "__main__":
    # Создаем точки
    p1 = Point3(0, 0, 0)
    p2 = Point3(1, 1, 1)
    p3 = Point3(1, 0, 0)
    p4 = Point3(0, 1, 0)
    
    # Создаем линию и плоскость
    line = Line3d(p1, p2)
    plane = Plane()
    plane.from3Points(p1, p2, p3)
    
    # Находим точку пересечения
    try:
        intersection = line_plane_intersec(line, plane)
        print(f"Точка пересечения: ({intersection.x:.3f}, {intersection.y:.3f}, {intersection.z:.3f})")
    except ValueError as e:
        print(f"Ошибка: {e}")
    
    # Используем функцию округления
    rounded_x = round3(intersection.x)
    print(f"Округленное значение x: {rounded_x}")
    
    # Example: Transform a point to plane-local coordinates
    test_point = Point3(1, 1, 1)
    x_local, y_local, z_local = plane.to_local_coords(test_point)
    print(f"Point in plane local coords: ({x_local:.3f}, {y_local:.3f}, {z_local:.3f})")
    
    # Transform back to world coordinates
    back_to_world = plane.from_local_coords(x_local, y_local, z_local)
    print(f"Back to world coords: ({back_to_world.x:.3f}, {back_to_world.y:.3f}, {back_to_world.z:.3f})")
    """
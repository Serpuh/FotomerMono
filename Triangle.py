from dataclasses import dataclass
import sys
import math
from typing import Optional, Tuple
from PySide6.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene, 
    QMainWindow, QGraphicsItem, QVBoxLayout, QWidget,
    QLabel, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QLineF
from PySide6.QtGui import (
    QPen, QBrush, QColor, QPainter, QPainterPath, 
    QFont, QFontMetrics, QTransform, QVector3D 
)


class Triangle(QGraphicsItem):
    """A triangle graphics item with vertices at 3 points and 3D coordinate storage"""   

    def __init__(self, point1: QPointF = None, point2: QPointF = None, point3: QPointF = None,
                 P1: QVector3D = None, P2: QVector3D = None, P3: QVector3D = None,
                 textSize: int = 10, bBoundAll=False):
        super().__init__()
        
        # Triangle vertices (2D screen points)
        self._point1 = point1 if point1 else QPointF(0, 0)
        self._point2 = point2 if point2 else QPointF(100, 0)
        self._point3 = point3 if point3 else QPointF(50, 100)
        
        # Triangle vertices (3D world coordinates)
        self.P1: QVector3D = P1
        self.P2: QVector3D = P2
        self.P3: QVector3D = P3

        self.bBoundAll = bBoundAll

        # Visual properties
        self._line_color = QColor(255, 0, 255)  # Magenta color for triangle
        self._fill_color = QColor(255, 0, 255, 30)  # Semi-transparent magenta
        self._line_width = 1.0
        self._text_color = QColor(96, 240, 245)
        self._text_bg_color = QColor(255, 255, 255, 220)  # Semi-transparent white
        
        self.textSize = textSize
        # Arrow properties        
        self._arrow_size = textSize
        
        # Text properties
        self._font = QFont("Arial", self.textSize)
        self._text = self._calculate_area_text_3d()
        
        # Selection state
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Update bounding rect
        self._update_bounding_rect()

    def getArea(self):
        """Calculate and return the area of the triangle in 3D space"""
        if self.P1 is None or self.P2 is None or self.P3 is None:
            return 0.0
        
        # Calculate vectors from P1 to P2 and P1 to P3
        v1 = self.P2 - self.P1
        v2 = self.P3 - self.P1
        
        # Cross product gives twice the area
        cross = QVector3D.crossProduct(v1, v2)
        area = cross.length() / 2.0
        return area

    def changeTextSize(self, textSize):        
        self.textSize = textSize
        self._font = QFont("Arial", self.textSize)
        self._arrow_size = self.textSize
        self._update_bounding_rect()
        self.update()        
        
    def getScreenPoints(self):
        """Return the three screen coordinates of the triangle vertices"""
        return self._point1, self._point2, self._point3
    
    def set_points(self, point1: QPointF, point2: QPointF, point3: QPointF,
                   P1: QVector3D, P2: QVector3D, P3: QVector3D):
        """Set the three vertices of the triangle (both 2D and 3D)"""
        self.prepareGeometryChange()
        self._point1 = point1
        self._point2 = point2
        self._point3 = point3
        self.P1 = P1
        self.P2 = P2
        self.P3 = P3
        self._text = self._calculate_area_text_3d()
        self._update_bounding_rect()
        self.update()

    def _calculate_area_text_3d(self) -> str:
        """Calculate the area of the triangle and format as text"""
        area = self.getArea()
        
        # Format based on area size
        if area < 1:
            return f"{area:.3f}"
        elif area < 10:
            return f"{area:.2f}"
        elif area < 100:
            return f"{area:.1f}"
        else:
            return f"{int(area)}"

    def _update_bounding_rect(self):
        """Update the bounding rectangle based on current points"""
        # Find bounding box of all three points
        min_x = min(self._point1.x(), self._point2.x(), self._point3.x())
        min_y = min(self._point1.y(), self._point2.y(), self._point3.y())
        max_x = max(self._point1.x(), self._point2.x(), self._point3.x())
        max_y = max(self._point1.y(), self._point2.y(), self._point3.y())
        
        # Create bounding rect
        rect = QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
        
        # Get text dimensions for area label
        font_metrics = QFontMetrics(self._font)
        text_rect = font_metrics.boundingRect(self._text)
        text_height = text_rect.height()
        
        # Inflate to include arrows and text
        inflate_amount = max(self._arrow_size * 2, text_height)
        rect.adjust(-inflate_amount, -inflate_amount, inflate_amount, inflate_amount)
        
        self._bounding_rect = rect

    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the item"""
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        """Return a shape used for selection/hit-tests"""
        path = QPainterPath()
        
        # Create triangle path for hit-testing
        path.moveTo(self._point1)
        path.lineTo(self._point2)
        path.lineTo(self._point3)
        path.closeSubpath()
        
        return path

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def paint(self, painter: QPainter, option, widget=None):
        """Paint the triangle with filled area and outline"""
        # Set up painter
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw filled triangle
        triangle_path = QPainterPath()
        triangle_path.moveTo(self._point1)
        triangle_path.lineTo(self._point2)
        triangle_path.lineTo(self._point3)
        triangle_path.closeSubpath()
        
        # Fill the triangle with semi-transparent color
        painter.setBrush(QBrush(self._fill_color))
        painter.setPen(QPen(self._line_color, self._line_width))
        painter.drawPath(triangle_path)
        
        # Draw vertices as small circles
        vertex_radius = self._arrow_size / 2.0
        vertex_pen = QPen(self._line_color, self._line_width)
        vertex_pen.setCosmetic(True)
        painter.setPen(vertex_pen)
        
        for point in [self._point1, self._point2, self._point3]:
            painter.drawEllipse(point, vertex_radius, vertex_radius)
        
        # Draw area text in the centroid of the triangle
        self._draw_area_text(painter)
        
        # Draw selection highlight if selected
        if self.isSelected():
            selection_pen = QPen(Qt.red, 2, Qt.DashLine)
            selection_pen.setCosmetic(True)
            painter.setPen(selection_pen)
            painter.drawPath(triangle_path)

    def _draw_area_text(self, painter: QPainter):
        """Draw the area text at the centroid of the triangle"""
        # Calculate centroid
        centroid_x = (self._point1.x() + self._point2.x() + self._point3.x()) / 3.0
        centroid_y = (self._point1.y() + self._point2.y() + self._point3.y()) / 3.0
        centroid = QPointF(centroid_x, centroid_y)
        
        # Get text dimensions
        font_metrics = QFontMetrics(self._font)
        text_rect = font_metrics.boundingRect(self._text)
        w = text_rect.width()
        h = text_rect.height()
        
        # Draw text background
        painter.save()
        painter.setBrush(QBrush(self._text_bg_color))
        bg_pen = QPen(self._text_color)
        bg_pen.setCosmetic(True)
        painter.setPen(bg_pen)
        bg_rect = QRectF(centroid.x() - w/2 - 2, centroid.y() - h/2 - 2, w + 4, h + 4)
        painter.drawRect(bg_rect)
        
        # Draw text
        painter.setFont(self._font)
        painter.setPen(QPen(self._text_color))
        painter.drawText(bg_rect, Qt.AlignCenter, self._text)
        
        painter.restore()

    def clone(self) -> "Triangle":
        """Return a new independent Triangle with the same visual/state properties"""
        # Copy screen points
        p1 = QPointF(self._point1)
        p2 = QPointF(self._point2)
        p3 = QPointF(self._point3)

        # Copy 3D points
        P1_copy = QVector3D(self.P1.x(), self.P1.y(), self.P1.z()) if self.P1 is not None else None
        P2_copy = QVector3D(self.P2.x(), self.P2.y(), self.P2.z()) if self.P2 is not None else None
        P3_copy = QVector3D(self.P3.x(), self.P3.y(), self.P3.z()) if self.P3 is not None else None

        # Create new instance
        new = Triangle(point1=p1, point2=p2, point3=p3, P1=P1_copy, P2=P2_copy, P3=P3_copy,
                      textSize=self.textSize)

        # Copy visual properties
        new._line_color = QColor(self._line_color)
        new._fill_color = QColor(self._fill_color)
        new._line_width = float(self._line_width)
        new._text_color = QColor(self._text_color) if isinstance(self._text_color, QColor) else self._text_color
        new._text_bg_color = QColor(self._text_bg_color)
        new._arrow_size = float(self._arrow_size)
        new._font = QFont(self._font)
        new._text = str(self._text)

        # Copy flags
        new.setFlag(QGraphicsItem.ItemIsSelectable, bool(self.flags() & QGraphicsItem.ItemIsSelectable))
        new.setFlag(QGraphicsItem.ItemIsMovable, bool(self.flags() & QGraphicsItem.ItemIsMovable))
        new.setFlag(QGraphicsItem.ItemSendsGeometryChanges, bool(self.flags() & QGraphicsItem.ItemSendsGeometryChanges))

        # Copy transform properties
        new.setZValue(self.zValue())
        new.setPos(self.pos())
        new.setTransform(self.transform())
        new.setRotation(self.rotation())
        new.setScale(self.scale())

        # Update bounding rect and return
        new._update_bounding_rect()
        return new

    # ----------------------------
    # Point-by-point comparison
    # ----------------------------
    @staticmethod
    def _points_equal(p1: QPointF, p2: QPointF, tol: float = 1e-6) -> bool:
        """Compare two QPointF objects coordinate-wise within tolerance"""
        if p1 is None and p2 is None:
            return True
        if p1 is None or p2 is None:
            return False
        return (math.isclose(p1.x(), p2.x(), rel_tol=0.0, abs_tol=tol) and 
                math.isclose(p1.y(), p2.y(), rel_tol=0.0, abs_tol=tol))

    def __eq__(self, other: object) -> bool:
        """Equality compares all three points point-by-point (with tolerance)"""
        if not isinstance(other, Triangle):
            return NotImplemented
        return (self._points_equal(self._point1, other._point1) and
                self._points_equal(self._point2, other._point2) and
                self._points_equal(self._point3, other._point3))

    def __ne__(self, other: object) -> bool:
        """Negation of __eq__"""
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented
        return not eq

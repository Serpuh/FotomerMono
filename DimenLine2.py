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

@dataclass
class Point3d:
    x: float = None
    y: float = None
    y: float = None

class QGraphicsDimensionalLine(QGraphicsItem):
    """A dimension line graphics item with arrows and text"""
    
    def __init__(self, start_point: QPointF = None, end_point: QPointF = None):
        super().__init__()
        
        # Line properties
        P1: QVector3D = None
        P2: QVector3D = None

        self._start_point = start_point if start_point else QPointF(0, 0)
        self._end_point = end_point if end_point else QPointF(100, 100)
        
        # Visual properties
        self._line_color = QColor(0, 100, 200)  # Blue color
        self._line_width = 1.0
        self._text_color = Qt.red
        self._text_bg_color = QColor(255, 255, 255, 220)  # Semi-transparent white
        
        # Arrow properties
        self._arrow_size = 10
        self._arrow_angle = 15  # degrees
        
        # Text properties
        self._font = QFont("Arial", 10)
        self._text = self._calculate_distance_text()
        
        # Selection state
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Update bounding rect
        self._update_bounding_rect()
    
    def _calculate_distance_text(self) -> str:
        """Calculate the distance between points and format as text"""
        line = QLineF(self._start_point, self._end_point)
        distance = line.length()
        
        # Format based on distance
        if distance < 10:
            return f"{distance:.2f}"
        elif distance < 100:
            return f"{distance:.1f}"
        else:
            return f"{int(distance)}"
    
    def _update_bounding_rect(self):
        """Update the bounding rectangle based on current points and text"""
        # Create a line for calculations
        line = QLineF(self._start_point, self._end_point)
        
        # Get text dimensions
        font_metrics = QFontMetrics(self._font)
        text_rect = font_metrics.boundingRect(self._text)
        
        # Calculate text position (middle of the line)
        mid_point = line.pointAt(0.5)
        
        # Add padding around text
        text_rect.adjust(-5, -5, 5, 5)
        text_rect.moveCenter(mid_point.toPoint())
        
        # Create a bounding rect that includes line, arrows, and text
        line_rect = QRectF(self._start_point, self._end_point).normalized()
        
        # Inflate to include arrows and text
        inflate_amount = max(self._arrow_size * 2, text_rect.height() / 2)
        line_rect.adjust(-inflate_amount, -inflate_amount, inflate_amount, inflate_amount)
        
        # Combine with text rect
        self._bounding_rect = line_rect.united(QRectF(text_rect))
        #self._bounding_rect = text_rect
    
    def set_points(self, start_point: QPointF, end_point: QPointF):
        """Set the start and end points of the dimension line"""
        self.prepareGeometryChange()
        self._start_point = start_point
        self._end_point = end_point
        self._text = self._calculate_distance_text()
        self._update_bounding_rect()
        self.update()
    
    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the item"""
        return self._bounding_rect
    
    def paint(self, painter: QPainter, option, widget=None):
        """Paint the dimension line, arrows, and text"""
        # Set up painter
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the dimension line
        line_pen = QPen(self._line_color, self._line_width)
        line_pen.setCosmetic(True)  # Makes line width independent of zoom
        painter.setPen(line_pen)
        
        # Draw main line
        painter.drawLine(self._start_point, self._end_point)
        
        # Draw arrows
        self._draw_arrow(painter, self._start_point, self._end_point)
        self._draw_arrow(painter, self._end_point, self._start_point)
        
        # Draw dimension text
        self._draw_dimension_text(painter)
        
        # Draw selection highlight if selected
        if self.isSelected():
            selection_pen = QPen(Qt.red, 1, Qt.DashLine)
            selection_pen.setCosmetic(True)
            painter.setPen(selection_pen)
            painter.drawRect(self.boundingRect())
    
    def _draw_arrow(self, painter: QPainter, arrow_tip: QPointF, line_end: QPointF):
        """Draw an arrow at the specified point"""
        # Calculate arrow direction
        line = QLineF(arrow_tip, line_end)
        angle = math.atan2(line.dy(), line.dx())
        
        # Calculate arrow points
        arrow_angle_rad = math.radians(self._arrow_angle)
        
        # Arrow left wing
        arrow_p1 = QPointF(
            arrow_tip.x() + self._arrow_size * math.cos(angle + arrow_angle_rad),
            arrow_tip.y() + self._arrow_size * math.sin(angle + arrow_angle_rad)
        )
        
        # Arrow right wing
        arrow_p2 = QPointF(
            arrow_tip.x() + self._arrow_size * math.cos(angle - arrow_angle_rad),
            arrow_tip.y() + self._arrow_size * math.sin(angle - arrow_angle_rad)
        )
        
        # Draw arrow as filled polygon
        arrow_path = QPainterPath()
        arrow_path.moveTo(arrow_tip)
        arrow_path.lineTo(arrow_p1)
        arrow_path.lineTo(arrow_p2)
        arrow_path.closeSubpath()
        
        painter.save()
        painter.setBrush(QBrush(self._line_color))
        painter.setPen(Qt.NoPen)
        painter.drawPath(arrow_path)
        painter.restore()
    
    def _draw_dimension_text(self, painter: QPainter):
        """Draw the dimension text in the middle of the line"""
        # Calculate text position (middle of the line)
        line = QLineF(self._start_point, self._end_point)
        mid_point = line.pointAt(0.5)
        
        # Calculate text angle (parallel to the line)
        angle = math.degrees(math.atan2(line.dy(), line.dx()))
        
        # Keep text upright (0-180 degrees)
        if angle > 90:
            angle -= 180
        elif angle < -90:
            angle += 180
        
        # Get text dimensions
        font_metrics = QFontMetrics(self._font)
        text_rect = font_metrics.boundingRect(self._text)
        
        # Center the text rect at mid point
        text_rect.moveCenter(mid_point.toPoint())
        
        # Add padding
        
        #padding = 4
        #bg_rect = text_rect.adjusted(-padding, -padding, padding, padding)
        
        # Save painter state
        painter.save()
        
        # Draw text background
        #painter.setPen(Qt.NoPen)
        #painter.setBrush(QBrush(self._text_bg_color))
        #painter.drawRect(bg_rect)
        
        
        # Draw text
        painter.setFont(self._font)
        painter.setPen(QPen(self._text_color))
        painter.translate(mid_point)
        painter.rotate(angle)
        painter.drawText(-text_rect.width()/2, text_rect.height()/4, self._text)
        
        # Restore painter state
        painter.restore()
    
    @property
    def start_point(self) -> QPointF:
        return self._start_point
    
    @property
    def end_point(self) -> QPointF:
        return self._end_point


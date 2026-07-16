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


class DimenLine(QGraphicsItem):
    """A dimension line graphics item with arrows and text"""   

    def __init__(self, start_point: QPointF = None, end_point: QPointF = None, P1: QVector3D = None, P2: QVector3D = None, textSize: int =10, bBoundAll = False):
        super().__init__()
        
        # Line properties
        self.P1: QVector3D = P1
        self.P2: QVector3D = P2

        self.bBoundAll = bBoundAll

        self._start_point = start_point if start_point else QPointF(0, 0)
        self._end_point = end_point if end_point else QPointF(100, 100)
        
        # Visual properties
        #self._line_color = QColor(0, 100, 200)  # Blue color
        self._line_color = QColor(0, 255, 0)  # Blue color
        self._line_width = 1.0
        self._text_color = QColor(96, 240, 245)
        self._text_bg_color = QColor(255, 255, 255, 220)  # Semi-transparent white
        
        self.textSize = textSize
        # Arrow properties        
        self._arrow_size = textSize
        self._arrow_angle = 15  # degrees
        
        # Text properties
        self._font = QFont("Arial", self.textSize)        
        self._text = self._calculate_distance_text_3d()
        
        # Store rotated text properties for painting and bounding calculations
        self._text_angle = 0.0  # degrees
        self._text_rect_local = QRectF(0, 0, 0, 0)  # rect centered at origin used when drawing rotated text
        self._bounding_rect_text = QRectF()  # axis-aligned bounding box that encloses the rotated text (for selection fallback)
        
        # Selection state
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Update bounding rect
        self._update_bounding_rect()

    def getDistance(self):
        return self.distance

    def changeTextSize(self, textSize):        
        self.textSize = textSize
        self._font = QFont("Arial", self.textSize)
        self._arrow_size = self.textSize
        self._update_bounding_rect()
        self.update()        
        
        
    def getScreenPoints(self):
        return self._start_point, self._end_point
    
    def set_points(self, start_point: QPointF, end_point: QPointF, P1: QVector3D, P2: QVector3D):
        """Set the start and end points of the dimension line"""
        self.prepareGeometryChange()
        self._start_point = start_point
        self._end_point = end_point
        self.P1 = P1
        self.P2 = P2
        self._text = self._calculate_distance_text_3d()
        self._update_bounding_rect()
        self.update()


    def _calculate_distance_text_3d(self) -> str:
        """Calculate the distance between points and format as text"""
        line = QLineF(self._start_point, self._end_point)
        self.distance = self.P1.distanceToPoint(self.P2)
        dist = self.distance
        # Format based on distance
        if dist < 1:
            return f"{dist:.3f}"
        elif dist < 10:
            return f"{dist:.2f}"
        elif dist < 100:
            return f"{dist:.1f}"
        else:
            return f"{int(dist)}"

    
    def _update_bounding_rect(self):
        """Update the bounding rectangle based on current points and text.
        Also compute a local text rect and text angle so the text background/selection
        rectangle can be drawn rotated (parallel to the slanted text)."""
        # Create a line for calculations
        line = QLineF(self._start_point, self._end_point)
        
        # Get text dimensions
        font_metrics = QFontMetrics(self._font)
        text_rect = font_metrics.boundingRect(self._text)
        w = text_rect.width()
        h = text_rect.height()
        
        # Calculate text position (middle of the line)
        mid_point = line.pointAt(0.5)
        
        # Keep text upright similarly to paint() logic:
        angle_deg = math.degrees(math.atan2(line.dy(), line.dx()))
        if angle_deg > 90:
            angle_deg -= 180
        elif angle_deg < -90:
            angle_deg += 180
        angle_rad = math.radians(angle_deg)
        
        # Save angle and local text rect (centered at origin) for painting
        self._text_angle = angle_deg
        padding = 1
        # local rect centered at origin
        self._text_rect_local = QRectF(-w/2 - padding, -h/2 - padding, w + 2*padding, h + 2*padding)
        
        # Compute axis-aligned bounding box of the rotated text rect (centered at mid_point)
        half_w = (w + 2*padding) / 2.0
        half_h = (h + 2*padding) / 2.0
        abs_cos = abs(math.cos(angle_rad))
        abs_sin = abs(math.sin(angle_rad))
        half_width_rotated = half_w * abs_cos + half_h * abs_sin
        half_height_rotated = half_w * abs_sin + half_h * abs_cos
        
        text_aabb = QRectF(
            mid_point.x() - half_width_rotated,
            mid_point.y() - half_height_rotated,
            2 * half_width_rotated,
            2 * half_height_rotated
        )
        
        # Create a bounding rect that includes line, arrows, and rotated text
        line_rect = QRectF(self._start_point, self._end_point).normalized()
        
        # Inflate to include arrows
        inflate_amount = max(self._arrow_size * 2, (h + 2*padding) / 2)
        line_rect.adjust(-inflate_amount, -inflate_amount, inflate_amount, inflate_amount)
        
        # Combine with text rect (axis-aligned envelope)
        self._bounding_rect = line_rect.united(text_aabb)
        # Also keep the unrotated text rect centered at the midpoint (useful for non-selection fallback)
        # Store as axis-aligned rect (centered at midpoint)
        self._bounding_rect_text = QRectF(mid_point.x() - w/2 - padding, mid_point.y() - h/2 - padding, w + 2*padding, h + 2*padding)
    
    
    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the item"""
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        """Return a shape used for selection/hit-tests. Limit it to the text's axis-aligned rect so
        selection only occurs when interacting with the text area (self._bounding_rect_text)."""
        path = QPainterPath()
        rect = self._bounding_rect_text
        if rect is None or rect.isNull():
            return path
        # Map the rect from scene coordinates into the item's local coordinates
        tl = self.mapFromScene(rect.topLeft())
        br = self.mapFromScene(rect.bottomRight())
        local_rect = QRectF(tl, br).normalized()
        path.addRect(local_rect)
        return path

    def mousePressEvent(self, event):
        """Only allow selection/dragging if the mouse press occurred inside the text's axis-aligned rect.
        Clicks outside that rect won't select the item (so isSelected() remains False)."""
        # event is a QGraphicsSceneMouseEvent
        # Only handle left button selection here; other buttons fallback to default behavior
        try:
            scene_pt = event.scenePos()
        except Exception:
            # If for some reason scenePos isn't available, fallback to default behavior
            return super().mousePressEvent(event)

        if event.button() == Qt.LeftButton:
            if self._bounding_rect_text.contains(scene_pt):
                # Inside text area: allow normal processing (selection / dragging)
                super().mousePressEvent(event)
            else:
                # Outside text area: ensure not selected and ignore the press so the item won't be selected
                if self.isSelected():
                    self.setSelected(False)
                event.ignore()
                # Do NOT call super().mousePressEvent(event) — this prevents selection when clicking outside text.
        else:
            super().mousePressEvent(event)

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
            selection_pen = QPen(Qt.red, 2, Qt.DashLine)
            selection_pen.setCosmetic(True)
            painter.setPen(selection_pen)
            # Draw rotated selection rectangle so it's parallel to the slanted text.
            # Compute mid_point again
            line = QLineF(self._start_point, self._end_point)
            mid_point = line.pointAt(0.5)
            painter.save()
            painter.translate(mid_point)
            painter.rotate(self._text_angle)
            painter.drawRect(self._text_rect_local)
            painter.restore()
    
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
        w = text_rect.width()
        h = text_rect.height()
        
        # Center the text rect at mid point (used for drawing text)
        text_rect.moveCenter(mid_point.toPoint())
        
        # Save painter state
        painter.save()
        
        # Draw text (no filled background by default here)
        painter.setFont(self._font)
        painter.setPen(QPen(self._text_color))
        painter.translate(mid_point)
        painter.rotate(angle)
        # drawText uses x,y baseline; place roughly vertically centered
        painter.drawText(-w/2, h/4, self._text)
        
        # Restore painter state
        painter.restore()
    """
    @property
    def start_point(self) -> QPointF:
        return self._start_point
    
    @property
    def end_point(self) -> QPointF:
        return self._end_point
    """

    def clone(self) -> "DimenLine":
        """Return a new independent DimenLine with the same visual/state properties."""
        # copy start/end points
        sp = QPointF(self._start_point)
        ep = QPointF(self._end_point)

        # copy QVector3D points (create new QVector3D objects)
        P1_copy = QVector3D(self.P1.x(), self.P1.y(), self.P1.z()) if self.P1 is not None else None
        P2_copy = QVector3D(self.P2.x(), self.P2.y(), self.P2.z()) if self.P2 is not None else None

        # create new instance
        new = DimenLine(start_point=sp, end_point=ep, P1=P1_copy, P2=P2_copy, textSize=self.textSize)

        # copy visual properties
        new._line_color = QColor(self._line_color)
        new._line_width = float(self._line_width)
        # _text_color may be Qt.GlobalColor or QColor - normalize
        new._text_color = QColor(self._text_color) if isinstance(self._text_color, QColor) else self._text_color
        new._text_bg_color = QColor(self._text_bg_color)
        new._arrow_size = float(self._arrow_size)
        new._arrow_angle = float(self._arrow_angle)
        new._font = QFont(self._font)
        new._text = str(self._text)

        # copy flags, z-value, transform, position, rotation, scale
        new.setFlag(QGraphicsItem.ItemIsSelectable, bool(self.flags() & QGraphicsItem.ItemIsSelectable))
        new.setFlag(QGraphicsItem.ItemIsMovable, bool(self.flags() & QGraphicsItem.ItemIsMovable))
        new.setFlag(QGraphicsItem.ItemSendsGeometryChanges, bool(self.flags() & QGraphicsItem.ItemSendsGeometryChanges))

        new.setZValue(self.zValue())
        new.setPos(self.pos())
        new.setTransform(self.transform())
        new.setRotation(self.rotation())
        new.setScale(self.scale())

        # update bounding rect and return
        new._update_bounding_rect()
        return new

    # ----------------------------
    # Point-by-point comparison
    # ----------------------------
    @staticmethod
    def _points_equal(p1: QPointF, p2: QPointF, tol: float = 1e-6) -> bool:
        """Compare two QPointF objects coordinate-wise within tolerance."""
        if p1 is None and p2 is None:
            return True
        if p1 is None or p2 is None:
            return False
        return math.isclose(p1.x(), p2.x(), rel_tol=0.0, abs_tol=tol) and math.isclose(p1.y(), p2.y(), rel_tol=0.0, abs_tol=tol)

    def __eq__(self, other: object) -> bool:
        """Equality compares start and end points point-by-point (with tolerance)."""
        if not isinstance(other, DimenLine):
            return NotImplemented
        return (self._points_equal(self._start_point, other._start_point) and
                self._points_equal(self._end_point, other._end_point))

    def __ne__(self, other: object) -> bool:
        """Negation of __eq__."""
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented
        return not eq

   
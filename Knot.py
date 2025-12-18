from PySide6.QtCore import ( Qt, Signal, QRectF, QPointF )

from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsEllipseItem, QGraphicsDropShadowEffect,
    QStyleOptionGraphicsItem, QWidget, QStyle
)


from PySide6.QtGui import (
    QPainter, QPainterPath, QPen, QBrush, QColor,
    QPainterPathStroker, QRadialGradient
)

class Knot(QGraphicsItem):
    """A more advanced knot item with custom shape."""
    
    positionChanged = Signal(QPointF)
    
    def __init__(self, x=0, y=0, size=12):
        super().__init__()
        
        self.size = size
        self._is_dragging = False
        
        # Colors
        self.fill_color = QColor(66, 135, 245, 200)
        self.border_color = QColor(30, 60, 120)
        self.hover_color = QColor(245, 66, 66, 200)
        
        # Set position
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(100)
        
    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle."""
        margin = 2  # Extra margin for painting
        return QRectF(-self.size/2 - margin, -self.size/2 - margin,
                     self.size + margin*2, self.size + margin*2)
    
    def shape(self) -> QPainterPath:
        """Define the clickable shape."""
        path = QPainterPath()
        path.addEllipse(-self.size/2, -self.size/2, self.size, self.size)
        
        # Optional: Make shape slightly larger than visual for easier clicking
        stroker = QPainterPathStroker()
        stroker.setWidth(4)
        return stroker.createStroke(path)
    
    def paint(self, painter: QPainter, option, widget=None):
        """Custom painting."""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Choose color based on state
        if option.state & QStyle.StateFlag.State_MouseOver:
            color = self.hover_color
        else:
            color = self.fill_color
        
        # Draw outer circle
        painter.setPen(QPen(self.border_color, 1.5))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(-self.size/2, -self.size/2, self.size, self.size)
        
        # Draw inner circle for depth effect
        painter.setPen(Qt.NoPen)
        inner_color = color.lighter(120)
        painter.setBrush(QBrush(inner_color))
        painter.drawEllipse(-self.size/4, -self.size/4, self.size/2, self.size/2)
    
    def mousePressEvent(self, event):
        """Handle mouse press."""
        self._is_dragging = True
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self._is_dragging = False
        super().mouseReleaseEvent(event)
    
    def itemChange(self, change, value):
        """Handle item changes."""
        if change == QGraphicsItem.ItemPositionChange and self._is_dragging:
            self.positionChanged.emit(value)
        return super().itemChange(change, value)
from PySide6.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsSceneMouseEvent
from PySide6.QtCore import Qt, QPointF, QRectF, Signal

from PySide6.QtGui import QBrush, QPen, QColor, QPainter, QPainterPath

class Knot(QGraphicsEllipseItem):
    """A draggable knot/control point for graphics scenes."""
    
    # Custom signals
    
    knotPressed = Signal()
    knotReleased = Signal()
    positionChanged = Signal(QPoint)
    
    def __init__(self, x=0, y=0, radius=5, parent=None):
        """
        Initialize a knot item.
        
        Args:
            x: X coordinate
            y: Y coordinate
            radius: Radius of the knot
            parent: Parent graphics item
        """
        super().__init__(parent)
        
        # Set default properties
        self.radius = radius
        self.setRect(-radius, -radius, radius * 2, radius * 2)
        self.setPos(x, y)
        
        # Make the knot selectable and movable
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Appearance settings
        self.normal_color = QColor(0, 150, 255)  # Blue
        self.selected_color = QColor(255, 100, 0)  # Orange
        self.hover_color = QColor(255, 50, 150)  # Pink
        
        # Set initial appearance
        self.setBrush(QBrush(self.normal_color))
        self.setPen(QPen(Qt.black, 1))
        
        # Interactive states
        self.setAcceptHoverEvents(True)
        self.is_dragging = False
        
        # Optional: add a crosshair for better visibility
        self.show_crosshair = True
        
    def paint(self, painter: QPainter, option, widget=None):
        """Custom painting to add visual feedback."""
        # Call parent paint method for the ellipse
        super().paint(painter, option, widget)
        
        # Draw crosshair if enabled
        if self.show_crosshair and self.isSelected():
            painter.save()
            painter.setPen(QPen(Qt.black, 1, Qt.DashLine))
            painter.drawLine(-self.radius - 5, 0, self.radius + 5, 0)
            painter.drawLine(0, -self.radius - 5, 0, self.radius + 5)
            painter.restore()
    
    def itemChange(self, change, value):
        """Handle item changes, especially position changes."""
        if change == QGraphicsItem.ItemPositionChange:
            # Emit signal when position changes
            self.positionChanged.emit(value)
            
        elif change == QGraphicsItem.ItemSelectedChange:
            # Change color when selection changes
            if value:
                self.setBrush(QBrush(self.selected_color))
            else:
                self.setBrush(QBrush(self.normal_color))
                
        return super().itemChange(change, value)
    
    def hoverEnterEvent(self, event):
        """Handle hover enter events."""
        if not self.isSelected():
            self.setBrush(QBrush(self.hover_color))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Handle hover leave events."""
        if not self.isSelected():
            self.setBrush(QBrush(self.normal_color))
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.knotPressed.emit()
            
            # Visual feedback
            self.setBrush(QBrush(self.selected_color))
            
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle mouse move events."""
        if self.is_dragging:
            # Update position (parent class handles actual movement)
            pass
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.knotReleased.emit()
            
            # Reset to normal color if not selected
            if not self.isSelected():
                self.setBrush(QBrush(self.normal_color))
                
        super().mouseReleaseEvent(event)
    
    def setRadius(self, radius: float):
        """Set the radius of the knot."""
        self.radius = radius
        self.setRect(-radius, -radius, radius * 2, radius * 2)
        self.update()
    
    def getPosition(self) -> QPointF:
        """Get the current position of the knot."""
        return self.pos()
    
    def setPosition(self, x: float, y: float):
        """Set the position of the knot."""
        self.setPos(x, y)
    
    def connectToItem(self, item: QGraphicsItem):
        """Connect this knot to another graphics item."""
        if item:
            item.setParentItem(self)
    
    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the knot."""
        # Add some margin for selection and hover effects
        margin = 2.0
        return super().boundingRect().adjusted(-margin, -margin, margin, margin)
    
    def shape(self) -> QPainterPath:
        """Return the shape of the knot for accurate collision detection."""
        path = QPainterPath()
        path.addEllipse(self.rect())
        return path
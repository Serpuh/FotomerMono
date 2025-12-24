from PySide6.QtCore import Qt, QPointF, QRectF, QLineF, Signal, QObject
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath, QBrush
from PySide6.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem

class DimenLine1(QGraphicsItem, QObject):
    """A graphics item that displays a dimensional line with text and arrows."""
    
    # Signal emitted when the dimension value changes
    valueChanged = Signal(float)
    
    def __init__(self, start_point: QPointF, end_point: QPointF, value: float = None, 
                 text: str = None, parent=None):
        """
        Initialize the dimension line.
        
        Args:
            start_point: Starting point of the dimension line
            end_point: Ending point of the dimension line
            value: Optional dimension value (auto-calculated if None)
            text: Optional custom text to display
            parent: Parent graphics item
        """
        super().__init__(parent)
        QObject.__init__(self)
        
        # Set initial points
        self._start_point = start_point
        self._end_point = end_point
        
        # Calculate value if not provided
        if value is None:
            self._value = self._calculate_distance(start_point, end_point)
        else:
            self._value = value
            
        # Set text
        self._text = text if text is not None else f"{self._value:.2f}"
        
        # Set default appearance properties
        self._line_color = QColor(0, 100, 200)  # Blue
        self._text_color = QColor(0, 0, 0)       # Black
        self._line_width = 2.0
        self._text_size = 10
        self._arrow_size = 10
        self._offset_distance = 20  # Distance from measured line
        self._text_background = QColor(255, 255, 255, 200)  # Semi-transparent white
        
        # Enable selection and movable
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Cache the bounding rectangle
        self.update_bounding_rect()
    
    def _calculate_distance(self, p1: QPointF, p2: QPointF) -> float:
        """Calculate Euclidean distance between two points."""
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        return (dx**2 + dy**2)**0.5
    
    def update_bounding_rect(self):
        """Update the bounding rectangle based on current geometry."""
        # Calculate the line for offset
        line = QLineF(self._start_point, self._end_point)
        
        # Create perpendicular offset vector
        dx = self._end_point.x() - self._start_point.x()
        dy = self._end_point.y() - self._start_point.y()
        
        # Normalize and rotate 90 degrees for offset
        length = (dx**2 + dy**2)**0.5
        if length > 0:
            offset_x = -dy / length * self._offset_distance
            offset_y = dx / length * self._offset_distance
        else:
            offset_x, offset_y = 0, self._offset_distance
        
        # Calculate offset points
        offset_start = QPointF(self._start_point.x() + offset_x, 
                              self._start_point.y() + offset_y)
        offset_end = QPointF(self._end_point.x() + offset_x, 
                            self._end_point.y() + offset_y)
        
        # Calculate text position (middle of offset line)
        text_pos = QPointF((offset_start.x() + offset_end.x()) / 2,
                          (offset_start.y() + offset_end.y()) / 2)
        
        # Estimate text rectangle
        font = QFont()
        font.setPointSizeF(self._text_size)
        text_width = len(self._text) * self._text_size * 0.6
        text_height = self._text_size * 1.2
        
        # Create a rectangle that encompasses everything
        margin = self._arrow_size + 5
        all_points = [
            self._start_point, self._end_point,
            offset_start, offset_end,
            QPointF(text_pos.x() - text_width/2 - margin, text_pos.y() - text_height/2 - margin),
            QPointF(text_pos.x() + text_width/2 + margin, text_pos.y() + text_height/2 + margin)
        ]
        
        # Find min/max coordinates
        xs = [p.x() for p in all_points]
        ys = [p.y() for p in all_points]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        self._bounding_rect = QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
    
    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the item."""
        return self._bounding_rect
    
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        """Paint the dimension line with arrows and text."""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate the main line
        line = QLineF(self._start_point, self._end_point)
        
        # Create perpendicular offset vector
        dx = self._end_point.x() - self._start_point.x()
        dy = self._end_point.y() - self._start_point.y()
        
        # Normalize and rotate 90 degrees for offset
        length = (dx**2 + dy**2)**0.5
        if length > 0:
            offset_x = -dy / length * self._offset_distance
            offset_y = dx / length * self._offset_distance
        else:
            offset_x, offset_y = 0, self._offset_distance
        
        # Calculate offset points
        offset_start = QPointF(self._start_point.x() + offset_x, 
                              self._start_point.y() + offset_y)
        offset_end = QPointF(self._end_point.x() + offset_x, 
                            self._end_point.y() + offset_y)
        
        # Draw extension lines (from actual points to offset line)
        painter.setPen(QPen(self._line_color, 1, Qt.DashLine))
        painter.drawLine(self._start_point, offset_start)
        painter.drawLine(self._end_point, offset_end)
        
        # Draw main dimension line
        painter.setPen(QPen(self._line_color, self._line_width, Qt.SolidLine))
        painter.drawLine(offset_start, offset_end)
        
        # Draw arrows
        self._draw_arrow(painter, offset_start, line.angle())
        self._draw_arrow(painter, offset_end, line.angle() + 180)  # Opposite direction
        
        # Draw text background
        text_pos = QPointF((offset_start.x() + offset_end.x()) / 2,
                          (offset_start.y() + offset_end.y()) / 2)
        
        # Set up font
        font = QFont()
        font.setPointSizeF(self._text_size)
        painter.setFont(font)
        
        # Calculate text bounding box
        text_rect = painter.boundingRect(QRectF(), Qt.AlignCenter, self._text)
        text_rect.moveCenter(text_pos)
        
        # Add padding to background
        padding = 4
        bg_rect = text_rect.adjusted(-padding, -padding, padding, padding)
        
        # Draw background
        painter.setBrush(QBrush(self._text_background))
        painter.setPen(Qt.NoPen)
        painter.drawRect(bg_rect)
        
        # Draw text
        painter.setPen(self._text_color)
        painter.drawText(bg_rect, Qt.AlignCenter, self._text)
        
        # Draw selection highlight if selected
        if self.isSelected():
            painter.setPen(QPen(Qt.yellow, 1, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.boundingRect())
    
    def _draw_arrow(self, painter: QPainter, position: QPointF, angle: float):
        """Draw an arrow at the specified position and angle."""
        arrow_size = self._arrow_size
        
        # Calculate arrow points
        arrow_p1 = QPointF(
            position.x() + arrow_size * 0.5,
            position.y() + arrow_size * 0.25
        )
        arrow_p2 = QPointF(
            position.x() + arrow_size * 0.5,
            position.y() - arrow_size * 0.25
        )
        
        # Create arrow path
        arrow_path = QPainterPath()
        arrow_path.moveTo(position)
        arrow_path.lineTo(arrow_p1)
        arrow_path.moveTo(position)
        arrow_path.lineTo(arrow_p2)
        
        # Rotate arrow to match line angle
        transform = painter.transform()
        painter.save()
        
        painter.translate(position)
        painter.rotate(-angle)  # Negative because Qt's Y axis is inverted
        painter.translate(-position)
        
        # Draw arrow
        painter.setPen(QPen(self._line_color, self._line_width, Qt.SolidLine))
        painter.drawPath(arrow_path)
        
        painter.restore()
    
    def set_points(self, start_point: QPointF, end_point: QPointF):
        """Update the dimension line points."""
        self._start_point = start_point
        self._end_point = end_point
        self._value = self._calculate_distance(start_point, end_point)
        self._text = f"{self._value:.2f}"
        self.update_bounding_rect()
        self.update()
        self.valueChanged.emit(self._value)
    
    def set_text(self, text: str):
        """Set custom text for the dimension."""
        self._text = text
        self.update_bounding_rect()
        self.update()
    
    def set_value(self, value: float):
        """Set the dimension value."""
        self._value = value
        self._text = f"{value:.2f}"
        self.update_bounding_rect()
        self.update()
        self.valueChanged.emit(value)
    
    def set_appearance(self, line_color: QColor = None, text_color: QColor = None,
                      line_width: float = None, text_size: float = None,
                      arrow_size: float = None, offset_distance: float = None,
                      text_background: QColor = None):
        """Update appearance properties."""
        if line_color is not None:
            self._line_color = line_color
        if text_color is not None:
            self._text_color = text_color
        if line_width is not None:
            self._line_width = line_width
        if text_size is not None:
            self._text_size = text_size
        if arrow_size is not None:
            self._arrow_size = arrow_size
        if offset_distance is not None:
            self._offset_distance = offset_distance
        if text_background is not None:
            self._text_background = text_background
        
        self.update_bounding_rect()
        self.update()
    
    def get_points(self):
        """Get the current start and end points."""
        return self._start_point, self._end_point
    
    def get_value(self) -> float:
        """Get the current dimension value."""
        return self._value
    
    def get_text(self) -> str:
        """Get the current text."""
        return self._text
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle mouse move events for dragging."""
        if self.isSelected():
            # Update position based on mouse movement
            super().mouseMoveEvent(event)
            # Recalculate bounding rect
            self.update_bounding_rect()
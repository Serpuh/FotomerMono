from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt, QObject, QRectF, QPointF

class Knot3(QGraphicsItem, QObject):
    def __init__(self, text="", size=20, color=Qt.red, parent=None):
        super().__init__(parent)
        QObject.__init__(self)  # Explicitly initialize QObject
        self._text = text
        self._size = size
        self._color = color
        self._pen_width = 2
        
        # Create text item as child
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setDefaultTextColor(color)
        
        # Center the text
        self.text_item.adjustSize()
        self.updateTextPosition()
        
        # Enable selection and movement
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
    def boundingRect(self):
        """Return the bounding rectangle of the item"""
        # Add some margin for the lines and text
        margin = self._size * 0.6
        return QRectF(-margin, -margin, 
                     2 * margin + self.text_item.boundingRect().width(),
                     2 * margin + self.text_item.boundingRect().height())
    
    def shape(self):
        """Define the clickable area (optional, uses boundingRect by default)"""
        path = QPainterPath()
        # Create a circular shape around the knot for easier clicking
        path.addEllipse(-self._size * 0.75, -self._size * 0.75, 
                        self._size * 1.5, self._size * 1.5)
        return path
    
    def paint(self, painter, option, widget=None):
        """Draw the knot with 2-line sight and text"""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set pen for drawing lines
        pen = QPen(self._color, self._pen_width)
        pen.setCosmetic(True)  # Makes the line width independent of zoom
        painter.setPen(pen)
        
        # Draw horizontal line
        painter.drawLine(-self._size, 0, self._size, 0)
        
        # Draw vertical line
        painter.drawLine(0, -self._size, 0, self._size)
        
        # Draw central circle
        painter.setBrush(QBrush(self._color))
        painter.drawEllipse(QPointF(0, 0), self._pen_width * 1.5, self._pen_width * 1.5)
        
        # If selected, draw a selection rectangle
        if self.isSelected():
            painter.setPen(QPen(Qt.blue, 1, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.boundingRect())
    
    def updateTextPosition(self):
        """Update text position relative to the knot"""
        text_rect = self.text_item.boundingRect()
        # Position text below the knot with some offset
        self.text_item.setPos(-text_rect.width() / 2, self._size * 1.2)
    
    def setText(self, text):
        """Set the text displayed with the knot"""
        self._text = text
        self.text_item.setPlainText(text)
        self.text_item.adjustSize()
        self.updateTextPosition()
        self.update()
    
    def getText(self):
        """Get the current text"""
        return self._text
    
    def setSize(self, size):
        """Set the size of the sight lines"""
        self._size = size
        self.updateTextPosition()
        self.update()
    
    def getSize(self):
        """Get the current size"""
        return self._size
    
    def setColor(self, color):
        """Set the color of the knot and text"""
        self._color = color
        self.text_item.setDefaultTextColor(color)
        self.update()
    
    def getColor(self):
        """Get the current color"""
        return self._color
    
    def setPenWidth(self, width):
        """Set the pen width for the lines"""
        self._pen_width = width
        self.update()
    
    def getPenWidth(self):
        """Get the current pen width"""
        return self._pen_width
    
    def type(self):
        """Return the type of this item (useful for custom items)"""
        return UserType + 1 if hasattr(QGraphicsItem, 'UserType') else 1001
    
    def itemChange(self, change, value):
        """Handle item changes"""
        if change == QGraphicsItem.ItemSelectedChange:
            # Optionally change appearance when selected
            pass
        return super().itemChange(change, value)

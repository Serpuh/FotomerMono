from PySide6.QtCore import ( Qt, QObject, Signal, Slot, QRectF, QPointF )

from PySide6.QtCore import Signal as ss

from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsEllipseItem, QGraphicsDropShadowEffect,
    QStyleOptionGraphicsItem, QWidget, QStyle
)


from PySide6.QtGui import (
    QPainter, QPainterPath, QPen, QBrush, QColor,
    QPainterPathStroker, QRadialGradient
)


class Knot2( QGraphicsEllipseItem ):
  
    positionChanged2 = Signal()
    
    def __init__(self):
        super().__init__()        
        self.positionChanged2.connect(self.testSignal)  # test link
        self.positionChanged2.emit()

    def testSignal(self):
        print("my signal test from init fire")
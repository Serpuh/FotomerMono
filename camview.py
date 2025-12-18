# This Python file uses the following encoding: utf-8
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMessageBox, QAbstractScrollArea
from PySide6.QtGui import QPainter, QPixmap, QTransform
from PySide6.QtCore import Qt, QRectF, Signal, QPointF

import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import cv2
import math

from Knot import Knot

class CamView(QGraphicsView):

    transformChanged = Signal()
    scrollChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)

        self.setMouseTracking(True)

        #self.setDragMode(QGraphicsView.ScrollHandDrag)

        #self.setMouseTracking(True)
        #self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        #self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        #self.viewport().setMouseTracking(True)
        #self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)        
        
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)
        
        #self.setMouseTracking(True)
        #self.viewport().setMouseTracking(True)
        #self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy)

        #self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        #self.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate)
        
        #self.setDragMode(QGraphicsView.ScrollHandDrag)

        #self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        #self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        #self.setRenderHints(Qt.renderHints() | Qt.Antialiasing)

        self.knot1 = Knot(500, 500, size=50)
        self.knot1.positionChanged.connect(lambda: self.on_knot_moved)
        self.knot1.positionChanged
        self.scene.addItem(self.knot1)   
            
        
        # for panning
        self._last_mouse_pos = None
        self.currMousePos = None

        # ensure transform anchor for zoom at mouse
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)

        # enable scroll signals
        self.horizontalScrollBar().valueChanged.connect(self._emit_scroll_changed)
        self.verticalScrollBar().valueChanged.connect(self._emit_scroll_changed)  
        
        self.mogeExr = None

    def on_knot_moved(self, pos):
        """Update line when knots move."""
        sender = self.sender()
        
        """
        if sender == self.knot1:
            # Update line from knot1 to knot2
            self.line.setLine(
                self.knot1.pos().x(), self.knot1.pos().y(),
                self.knot2.pos().x(), self.knot2.pos().y()
            )
        else:
            # Update line from knot2 to knot1
            self.line.setLine(
                self.knot2.pos().x(), self.knot2.pos().y(),
                self.knot1.pos().x(), self.knot1.pos().y()
            )
        """
        
                
        # Add to scene
             

    def on_knot_moved(self, pos):
       print(f"Knot moved to: {pos.x():.1f}, {pos.y():.1f}")
        

    def addImage(self, path):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Invalid image", path)
            return None           

        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)

        """
        self.knot1 = Knot(500, 500, size=50)
        self.knot1.positionChanged.connect(lambda: self.on_knot_moved)
        self.knot1.positionChanged.
        self.scene.addItem(self.knot1)   
        """
    
        # Set scene rect to image size
        #self.scene.setSceneRect(QRectF(pixmap.rect()))

        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

        return path    

    def addEXR(self, path, fov_x):
        self.mogeExr = cv2.imread(path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
        self.height, self.width = self.mogeExr.shape[:2]
        self.f_pix = (self.height/2.)/math.tan( math.radians(fov_x/2.) )
        self.height
        hh = 0
    
    def wheelEvent(self, event):        
        # zoom factor
        zoom_in = 1.1
        zoom_out = 1 / zoom_in
        factor = zoom_in if event.angleDelta().y() > 0 else zoom_out

        # map mouse to scene point
        #view_pt = event.position().toPoint()
        view_pt = self.currMousePos
        #print(f"self.currMousePos:  {self.currMousePos},   event.position().toPoint(): {event.position().toPoint()}")
        scene_pt = self.mapToScene(view_pt)

        # apply scale and keep scene_pt fixed
        self._zoom_at(scene_pt, factor)

        self.transformChanged.emit()

    def _zoom_at(self, scene_pt, factor):
        # view center before zoom
        before = self.mapToScene(self.viewport().rect().center())

        self.scale(factor, factor)

        # view center after zoom
        after = self.mapToScene(self.viewport().rect().center())
        #after = self.mapToScene(self.currMousePos)

        # compensate so that scene_pt stays under mouse
        delta = after - before
        #print("delta ",delta)
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._last_mouse_pos = event.pos()
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.currMousePos =  event.pos()
        scene_pt = self.mapToScene(self.currMousePos)
        #print(f"scene_pt {scene_pt}")
        if self._last_mouse_pos is not None:
            delta = event.pos() - self._last_mouse_pos
            self._last_mouse_pos = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            self.scrollChanged.emit()

        if(self.mogeExr is not None):
            cx_pix = self.width/2.
            cy_pix = self.height/2.
            #height, width = self.mogeExr.shape[:2]

            y1 = int(round(scene_pt.y()))
            x1 = int(round(scene_pt.x()))
                      
            if x1>=0 and x1<self.width and y1>=0 and y1<self.height:
                Z = self.mogeExr[ y1,x1 ]                

                if(math.isinf(Z)): print("No data")
                else:
                    X = (x1 - cx_pix) * Z / self.f_pix
                    Y = (y1 - cy_pix) * Z / self.f_pix
                    print(f"XYZ {X: .2f} {Y: .2f} {Z: .2f}")  

            else: print("Out of image")
                     
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._last_mouse_pos = None
            self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)

    def _emit_scroll_changed(self, *_):
        self.scrollChanged.emit()
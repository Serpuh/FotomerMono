# This Python file uses the following encoding: utf-8
from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMessageBox, 
                        QAbstractScrollArea, QGraphicsItem, QMainWindow, QStatusBar)
from PySide6.QtGui import QPainter, QPixmap, QTransform, QColor, QBrush, QPen, QPainterPath, QVector3D
from PySide6.QtCore import Qt, QRectF, Signal, QPointF, QObject

import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import cv2
import math

from Knot import Knot
from Knot2 import Knot2
from Knot3 import Knot3

from DimenLine2 import DimenLine


class CamView(QGraphicsView, QObject):

    transformChanged = Signal()
    scrollChanged = Signal()

    # Signal emitted when a dimension line is created
    dimension_line_created = Signal(DimenLine)

    def __init__(self, parent=None):
        super().__init__(parent)
        #QObject.__init__(self)  # Explicitly initialize QObject

        
        #self.pStatusBar.showMessage("from CamView")

        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)

        self.setMouseTracking(True)
        
        #self.setDragMode(QGraphicsView.ScrollHandDrag)

        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)
        
        # for panning
        self._last_mouse_pos = None
        self.currMousePos = None

        # enable scroll signals
        self.horizontalScrollBar().valueChanged.connect(self._emit_scroll_changed)
        self.verticalScrollBar().valueChanged.connect(self._emit_scroll_changed)  
        
        self.mogeExr = None

        # Dimension line creation state
        self.creating_dimension = False
        self.first_click_point = None
        self.temp_dimension_line = None
        self.first_click_point_3d: QVector3D = None           
        self.height_img: float = None
        self.width_img: float = None

        self.statusBar: QStatusBar = None


        self.ii=10

    def setSatusBar(self, statusBar):
        self.statusBar = statusBar
        self.statusBar.showMessage("From view")

    def on_knot_moved(self):
       #print(f"Knot moved to: {pos.x():.1f}, {pos.y():.1f}")
       print(f"Knot moved")
        

    def addImage(self, path):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Invalid image", path)
            return None           
           
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)
              
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

        #self.Ui_MainWindow.statusbar.showMessage("from CamView")

        return path    

    def addEXR(self, path, fov_x):
        self.mogeExr = cv2.imread(path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
        self.height_img, self.width_img = self.mogeExr.shape[:2]
        self.f_pix = (self.height_img/2.)/math.tan( math.radians(fov_x/2.) )
        
        hh = 0
    
    def wheelEvent(self, event):        
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(self.ViewportAnchor.AnchorUnderMouse)

        zoom_in = 1.1
        zoom_out = 1 / zoom_in
        factor = zoom_in if event.angleDelta().y() > 0 else zoom_out

        view_pt = self.currMousePos        
        mouse_pt = self.mapToScene(self.currMousePos)

        # apply scale and keep scene_pt fixed
        self._zoom_at(mouse_pt, factor)

        self.setTransformationAnchor(self.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(self.ViewportAnchor.NoAnchor)

        self.transformChanged.emit()

    def _zoom_at(self, scene_pt, factor):
        # view center before zoom
        before = self.mapToScene(self.viewport().rect().center())        
        self.scale(factor, factor)

        # view center after zoom
        after = self.mapToScene(self.viewport().rect().center())
        delta = after - before
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._last_mouse_pos = event.pos()
            self.setDragMode(QGraphicsView.ScrollHandDrag)

        """Handle mouse press events for dimension line creation"""
        if event.button() == Qt.LeftButton:
            # Convert to scene coordinates
            scene_pos = self.mapToScene(event.pos())
            
            if not self.creating_dimension:
                # Start creating a new dimension line
                self.creating_dimension = True
                self.first_click_point = scene_pos
                
                # Create temporary dimension line
                self.first_click_point_3d, bb = self.get_XYZ(self.first_click_point)
                vec3d2, bb = self.get_XYZ(scene_pos)
                self.temp_dimension_line = DimenLine(
                    self.first_click_point, scene_pos, self.first_click_point_3d, vec3d2
                )
                self.scene.addItem(self.temp_dimension_line)
                
                # Set it to be temporary (not selectable/movable)
                self.temp_dimension_line.setFlag(QGraphicsItem.ItemIsSelectable, False)
                self.temp_dimension_line.setFlag(QGraphicsItem.ItemIsMovable, False)
                
            else:
                # Second click - finish the dimension line
                if self.temp_dimension_line:
                    # Create the final dimension line
                    vec3d2, bb = self.get_XYZ(scene_pos)
                    final_dimension_line = DimenLine(
                        self.first_click_point, scene_pos, self.first_click_point_3d,vec3d2
                    )
                    self.scene.addItem(final_dimension_line)
                    
                    # Remove temporary line
                    self.scene.removeItem(self.temp_dimension_line)
                    self.temp_dimension_line = None
                    
                    # Emit signal
                    self.dimension_line_created.emit(final_dimension_line)
                
                # Reset creation state
                self.creating_dimension = False
                self.first_click_point = None
                self.first_click_point_3d = None
        super().mousePressEvent(event)

    def get_XYZ(self, scene_pt) -> tuple[QVector3D, bool]:
        cx_pix = self.width_img / 2
        cy_pix = self.height_img / 2

        y1 = int(round(scene_pt.y()))
        x1 = int(round(scene_pt.x()))
        X:float = None
        Y:float = None
        Z:float = None

        if x1>=0 and x1<self.width_img and y1>=0 and y1<self.height_img:
                Z = self.mogeExr[ y1,x1 ]                

                if(math.isinf(Z)): 
                    print("No data")
                    self.statusBar.showMessage("No data")
                    bb = False
                else:
                    X = (x1 - cx_pix) * Z / self.f_pix
                    Y = (y1 - cy_pix) * Z / self.f_pix
                    result = f"XYZ {X: .2f} {Y: .2f} {Z: .2f}"
                    self.statusBar.showMessage(result)
                    print(result)  
                    bb = True

        else: 
            print("Out of image")
            self.statusBar.showMessage("Out of image")
            bb = False

        if(bb): vv = QVector3D(X, Y, Z)
        else: vv = QVector3D(0, 0, 0)

        #return QVector3D(xpos=X, ypos=Y, zpos=Z), bb
        return vv, bb

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
            self.get_XYZ(scene_pt)            

        """Handle mouse move events to update temporary dimension line"""
        if self.creating_dimension and self.temp_dimension_line:
            # Update the end point of the temporary dimension line
            scene_pos = self.mapToScene(event.pos())
            vec3d2, bb = self.get_XYZ(scene_pos)            
            self.temp_dimension_line.set_points(self.first_click_point, scene_pos,  self.first_click_point_3d, vec3d2)
                     
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._last_mouse_pos = None
            self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape and self.creating_dimension:
            # Cancel dimension line creation
            self.creating_dimension = False
            if self.temp_dimension_line:
                self.scene.removeItem(self.temp_dimension_line)
                self.temp_dimension_line = None
            self.first_click_point = None
        
        # Call parent method
        super().keyPressEvent(event)

    def _emit_scroll_changed(self, *_):
        self.scrollChanged.emit()

    def _add_example_shapes(self):
        """Add some example shapes to the scene for demonstration"""
        # Add a rectangle
        rect_item = self.scene.addRect(-100, -50, 200, 100)
        rect_item.setPen(QPen(Qt.darkGreen, 2))
        rect_item.setBrush(QBrush(QColor(100, 200, 100, 100)))
        
        # Add a circle
        ellipse_item = self.scene.addEllipse(150, -75, 150, 150)
        ellipse_item.setPen(QPen(Qt.darkBlue, 2))
        ellipse_item.setBrush(QBrush(QColor(100, 100, 200, 100)))
        
        # Add a polygon
        from PySide6.QtGui import QPolygonF
        polygon = QPolygonF()
        polygon.append(QPointF(-200, 100))
        polygon.append(QPointF(-100, 200))
        polygon.append(QPointF(0, 150))
        polygon.append(QPointF(50, 250))
        polygon.append(QPointF(-150, 250))
        polygon_item = self.scene.addPolygon(polygon)
        polygon_item.setPen(QPen(Qt.darkRed, 2))
        polygon_item.setBrush(QBrush(QColor(200, 100, 100, 100)))
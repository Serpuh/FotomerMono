# This Python file uses the following encoding: utf-8
from calendar import c
from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMessageBox, 
                        QAbstractScrollArea, QGraphicsItem, QMainWindow, QStatusBar)
from PySide6.QtGui import QPainter, QPixmap, QTransform, QColor, QBrush, QPen, QPainterPath, QVector3D, QKeyEvent, QImage
from PySide6.QtCore import Qt, QRectF, Signal, QPointF, QObject, QXmlStreamReader, QXmlStreamWriter, QIODevice, QFile, QEvent

import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
import cv2

import math
from pathlib import Path

from Commands import Commands
from DimenLine2 import DimenLine

#from SettingsDlg import SettingsDlg

class CamView(QGraphicsView, QObject):

    transformChanged = Signal()
    scrollChanged = Signal()
    signalDimension = Signal(float)

    textSize = 10

    # Signal emitted when a dimension line is created
    dimension_line_created = Signal(DimenLine)

    def __init__(self, parent=None):
        super().__init__(parent)
        #QObject.__init__(self)  # Explicitly initialize QObject

        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)

        self.setMouseTracking(True)

        hh = math.degrees(math.atan(5184/2./5800))*2.
        hh2 = math.sqrt(4288*4288+2848*2848)

        f = (640./2.)/math.tan(math.radians(65./2.))
        
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
        self.img_path = None

        self.statusBar: QStatusBar = None

        #diag = math.sqrt(6.3*6.3 + 4.7*4.7)
                
        self.linkView: CamView = None
        self.linkView21: CamView = None
        self.xmlDict = {}
        self.command = None
        self.bOverExr: bool = False
        self.DimenLines = []
        ImgOpenLink = None
        self.SettingsDlg = None

        # enable drag & drop for image files
        self.setAcceptDrops(True)
        

    def removeMirorDimenLine(self, orig: DimenLine):
        all_items = self.scene.items()  
        for item in all_items:
            if(type(item)==DimenLine):
                if(item == orig):
                    self.scene.removeItem(item)   
                    #item.deleteLater()
                    del item   
        

    def clearAndReset(self):
        all_items = self.scene.items()  
        for item in all_items:
            self.scene.removeItem(item)   
            #item.deleteLater()
            del item   
        self.scene.clear()
        self.setScene(self.scene)
        self.scene.update()

        if(self.mogeExr is not None):
            del self.mogeExr
            self.mogeExr = None

        self.creating_dimension = False
        self.first_click_point = None
        self.temp_dimension_line = None
        self.first_click_point_3d: QVector3D = None           
        self.height_img: float = None
        self.width_img: float = None
        self.img_path = None

        self.xmlDict = {}
        
        self.bOverExr: bool = False
        self.DimenLines = []      

    def ClearExrView1(self):        
        all_items = self.scene.items()  
        
        for item in all_items:            
            if(type(item)==DimenLine):
                self.DimenLines.append(item)     
                
        self.DimenLines.reverse()

        for item in all_items:
            if(type(item)!=QGraphicsPixmapItem):
                self.scene.removeItem(item)   

        if(self.mogeExr is not None):
            del self.mogeExr
            self.mogeExr = None

    def ClearExrView2(self):        
        all_items = self.scene.items()  
        
        for item in all_items:            
            if(type(item)==DimenLine):
                self.DimenLines.append(item)        

        self.DimenLines.reverse()

        for item in all_items:
            self.scene.removeItem(item)   
            if(type(item)==QGraphicsPixmapItem):
                del item   

        
        if(self.mogeExr is not None):
            del self.mogeExr
            self.mogeExr = None

    def reduceDimLineText(self):
        if(CamView.textSize>3):
            CamView.textSize -=1 
            #print(CamView.textSize)
        all_items = self.scene.items()
        for item in all_items:
            if(type(item)==DimenLine):
                item.changeTextSize(CamView.textSize)
                item.update()

    def increaseDimLineText(self):
        CamView.textSize +=1 
        #print(CamView.textSize)
        all_items = self.scene.items()
        for item in all_items:
            if(type(item)==DimenLine):
                item.changeTextSize(CamView.textSize)
                item.update()

    def getDir(self):
        if(self.img_path is not None and len(self.img_path)!=0):      
            mPATH = Path(self.img_path)
            img_name = mPATH.name
            img_name_without_ext = mPATH.stem
            img_dir = mPATH.parent
            output_dir = Path(img_dir) / Path(img_name_without_ext)
            return output_dir, img_name_without_ext
        return None, None

    def printScene(self,path):
        rect = self.scene.sceneRect()    
        
        # Создаем изображение с размерами сцены
        image = QImage(rect.width(), rect.height(), QImage.Format_ARGB32)
        image.fill(Qt.transparent)  # Прозрачный фон
    
        # Рисуем сцену на изображение
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        self.scene.render(painter)
        painter.end()
    
        # Сохраняем изображение
        return image.save(path, "")
    

    def OnDimenLine(self, checked: bool):
        if(checked):
            self.command[0] = Commands.DIMENLINE            
        else:
            self.command[0] = Commands.NO
            event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key_Escape, Qt.NoModifier)
            self.keyPressEvent(event)            

    def loadXml(self, filename):
        file = QFile(filename)
        if not file.open(QIODevice.ReadOnly | QIODevice.Text):
            return False

        reader = QXmlStreamReader(file)
    
        while not reader.atEnd():
            reader.readNext()
        
            if reader.isStartElement():
                elname = reader.name()
                
                if(elname=="CamView"):
                    for attr in reader.attributes():
                        if(attr.name() == "textSize"):
                            CamView.textSize = int(attr.value())               

                if(elname == "DimenLine"):
                    b1, b2, b3, b4 = False,  False,  False,  False
                    for attr in reader.attributes():
                        
                        if(attr.name() == "x1"):
                            x1 = float(attr.value())
                            b1 = True
                        if(attr.name() == "y1"):
                            y1 = float(attr.value())
                            b2 = True
                        if(attr.name() == "x2"):
                            x2 = float(attr.value())
                            b3 = True
                        if(attr.name() == "y2"):
                            y2 = float(attr.value())
                            b4 = True                        

                    if(b1 and b2 and b3 and b4):
                        start_point = QPointF(x1,y1)
                        end_point = QPointF(x2,y2)
                        P1,bb1 = self.get_XYZ(start_point)
                        P2,bb2 = self.get_XYZ(end_point)
                        final_dimension_line = DimenLine(start_point, end_point, P1,P2, CamView.textSize)                                            
                        self.scene.addItem(final_dimension_line)
                        if(self.linkView != None):
                            self.linkView.scene.addItem(final_dimension_line.clone())

                    all_items = self.scene.items()
                    h=0
                            
            #elif reader.isEndElement():
             #   print(f"Конец элемента: {reader.name()}")
        
            elif reader.isCharacters() and not reader.isWhitespace():
                text = reader.text().strip()
                if text:                    
                    if(elname != "DimenLine"):
                        self.xmlDict[elname] = text
        
            elif reader.hasError():
                print(f"Ошибка xml: {reader.errorString()}")

        
    def saveXml(self, writer: QXmlStreamWriter):
        writer.writeStartElement("CamView")
        writer.writeAttribute("textSize", str(CamView.textSize))

        writer.writeTextElement("fov_x", str(self.fov_x)) 
        writer.writeTextElement("fx", str(self.fx))
        writer.writeTextElement("fy", str(self.fy)) 

        all_items = self.scene.items()      

        for item in all_items:
            if(type(item)==DimenLine):
                
                writer.writeStartElement("DimenLine")
                writer.writeAttribute("x1", str(item._start_point.x()) )
                writer.writeAttribute("y1", str(item._start_point.y()) )
                writer.writeAttribute("x2", str(item._end_point.x() ))
                writer.writeAttribute("y2", str(item._end_point.y() ))                
                writer.writeEndElement()

        writer.writeEndElement()


    def link12CamView(self,link):
        self.linkView = link

    def link21CamView(self,link):
        self.linkView21 = link

    def undo(self):        
        all_items = self.scene.items()     

        if len(all_items)>1:  
            last_item: DimenLine = all_items[0]
            self.scene.removeItem(last_item)           
            del last_item            
           

    def linkSatusBar(self, statusBar):
        self.statusBar = statusBar
        #self.statusBar.showMessage("From view")

    def fileImgOpenLink(self, link):
        self.ImgOpenLink = link

    def fileLoadForMainWindow(self,path):
        self.ImgOpenLink(path)
        h=0
        
    def Fit(self):
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def addImage(self, path):
        self.img_path = path
        pixmap = QPixmap(path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Invalid image", path)
            return None           
           
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)
        self.scene.setSceneRect( pixmap_item.boundingRect())              
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)   

        return path    

    def addEXR(self, path, fov_x, fx, fy):
        self.mogeExr = cv2.imread(path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
        self.height_img, self.width_img = self.mogeExr.shape[:2]
        self.fov_x = fov_x
        self.f_pix = (self.height_img/2.)/math.tan( math.radians(fov_x/2.) )*2     
        self.fx = fx
        self.fy = fy
        CamView.textSize = round(math.sqrt(self.width_img*self.width_img+self.height_img*self.height_img)*0.012)

        # reset DimenLine
        for item in self.DimenLines:
            begP, endP = item.getScreenPoints()
            P1, bb1 = self.get_XYZ(begP)
            P2, bb2 = self.get_XYZ(endP)
            if(bb1 and bb2):
                item.set_points(begP, endP, P1, P2)
            else:
                del item
            self.scene.addItem(item)
        self.DimenLines.clear()


        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
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
        if( self.img_path is None): return
        if event.button() == Qt.RightButton:
            self.Fit()
            if(self.linkView != None):
                self.linkView.Fit()
            if(self.linkView21 != None):
                self.linkView21.Fit()            
    
        if event.button() == Qt.MiddleButton:
            self._last_mouse_pos = event.pos()
            self.setDragMode(QGraphicsView.ScrollHandDrag)

        """Handle mouse press events for dimension line creation"""
        if (event.button() == Qt.LeftButton and self.command[0] == Commands.CALC):
            scene_pos = self.mapToScene(event.pos())
            item = self.scene.itemAt(scene_pos, self.transform())
            
            # Check if the item is a DimenLine
            if item and isinstance(item, DimenLine):            
                self.signalDimension.emit(item.getDistance())
            else:
                self.signalDimension.emit(-1.)
                

        # save click XYZ to file
        if (event.button() == Qt.LeftButton and self.command[0] == Commands.NO and self.bOverExr):
            scene_pos = self.mapToScene(event.pos())
            pp, bb = self.get_XYZ(scene_pos)
            currdir, _ = self.getDir()
            file_xyz = open(currdir/Path("red.txt"), 'w')
            file_xyz.write(f"{pp.x():.3f}\t{pp.y():.3f}\t{pp.z():.3f}\t")
            file_xyz.close()
            print(f"{pp.x():.3f}\t{pp.y():.3f}\t{pp.z():.3f}\t")

        if (event.button() == Qt.LeftButton and self.command[0] == Commands.DIMENLINE and self.bOverExr):
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
                    self.first_click_point, scene_pos, self.first_click_point_3d, vec3d2,CamView.textSize, True
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
                        self.first_click_point, scene_pos, self.first_click_point_3d,vec3d2,CamView.textSize
                    )
                    self.scene.addItem(final_dimension_line)
                    if(self.linkView != None):
                        self.linkView.scene.addItem(final_dimension_line.clone())
                        self.linkView.scene.update()
                    
                    # Remove temporary line
                    self.scene.removeItem(self.temp_dimension_line)
                    self.temp_dimension_line = None
                    
                    # Emit signal
                    self.dimension_line_created.emit(final_dimension_line)
                
                # Reset creation state
                self.creating_dimension = False
                self.first_click_point = None
                self.first_click_point_3d = None
        self.scene.update()
        super().mousePressEvent(event)

    def get_XYZ(self, scene_pt) -> tuple[QVector3D, bool]:
        if(self.mogeExr is None): return
        cx_pix = self.width_img / 2
        cy_pix = self.height_img / 2

        fx_pix = self.width_img * self.fx
        fy_pix = self.height_img * self.fy

        y1 = int(round(scene_pt.y()))
        x1 = int(round(scene_pt.x()))
        X:float = None
        Y:float = None
        Z:float = None

        if x1>=0 and x1<self.width_img and y1>=0 and y1<self.height_img:
                Z = self.mogeExr[ y1,x1 ]                

                if(math.isinf(Z)):                     
                    self.statusBar.showMessage("No data")
                    self.bOverExr = False
                else:
                    X = (x1 - cx_pix) * Z / fx_pix
                    Y = (y1 - cy_pix) * Z / fy_pix
                    dist = math.sqrt(X*X+Y*Y+Z*Z)
                    result = f"XYZ {X: .2f} {Y: .2f} {Z: .2f}     Distance{dist: .2f}"

                    self.statusBar.showMessage(result)                    
                    self.bOverExr = True

        else:             
            self.statusBar.showMessage("Out of image")
            self.bOverExr = False

        if(self.bOverExr): vv = QVector3D(X, Y, Z)
        else: vv = QVector3D(0, 0, 0)

        return vv, self.bOverExr

    def isExrCalc(self):
        if(self.mogeExr is not None):
            return True
        else:
            return False

    def mouseMoveEvent(self, event):
        self.currMousePos =  event.pos()
        scene_pt = self.mapToScene(self.currMousePos)        
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
        if self.creating_dimension and self.temp_dimension_line and  self.command[0] == Commands.DIMENLINE and self.bOverExr:
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
        if event.key() == Qt.Key.Key_Delete:
            all_items = self.scene.items()          
            for item in all_items:          
                if item.isSelected():
                    #self.linkView: CamView = None
                    #self.linkView21: CamView = None
                    if(self.linkView != None):
                        self.linkView.removeMirorDimenLine(item)

                    if(self.linkView21 != None):
                        self.linkView21.removeMirorDimenLine(item)

                    self.scene.removeItem(item)               
                    del item 
                    return

        # Call parent method
        self.scene.update()
        super().keyPressEvent(event)

    def _emit_scroll_changed(self, *_):
        self.scrollChanged.emit()


     # --- Drag & drop handlers for image files ---
    def dragEnterEvent(self, event):
        """Accept drag if it contains at least one supported local image file."""
        mime = event.mimeData()
        if mime.hasUrls():
            for url in mime.urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if Path(path).suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp', '.gif'):
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dragMoveEvent(self, event):
        """Allow moving over the widget when a supported file is being dragged."""
        mime = event.mimeData()
        if mime.hasUrls():
            for url in mime.urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if Path(path).suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp', '.gif'):
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dropEvent(self, event):
        """Handle drop: call fileLoadForMainWindow with the first supported image file."""
        mime = event.mimeData()
        if mime.hasUrls():
            for url in mime.urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if Path(path).suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp', '.gif'):
                        try:
                            self.fileLoadForMainWindow(path)
                        except Exception as e:
                            QMessageBox.warning(self, "Failed to open file", str(e))
                        event.acceptProposedAction()
                        return
        event.ignore()

    """
    def mouseDoubleClickEvent(self, event):        
        if event.button() == Qt.LeftButton and self.command[0] != Commands.DIMENLINE:
            # Get the item at the double-click position
            scene_pos = self.mapToScene(event.pos())
            item = self.scene.itemAt(scene_pos, self.transform())
            
            # Check if the item is a DimenLine
            if item and isinstance(item, DimenLine):
                # Handle double-click on DimenLine
                # You can add your custom logic here
                # For example: delete the dimension line, edit it, etc.
                self.scene.removeItem(item)
                del item
                self.scene.update()
                return
        
        super().mouseDoubleClickEvent(event)
        """
import os
import sys
import warnings

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PySide6.QtCore import QDir, Qt, QUrl, QXmlStreamReader, QXmlStreamWriter, QIODevice, QFile, QSaveFile
from PySide6.QtGui import QTransform, QAction, QKeySequence, QDesktopServices, QShortcut

from pathlib import Path

from SettingsDlg import SettingsDlg
from Commands import Commands

pathMainWinUp = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pathMainWinUp)

pathMainWin = os.path.dirname(os.path.abspath(__file__))

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
#os.environ["QT_DEBUG_PLUGINS"] = "1"

from ui_form import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionLoadImage.triggered.connect(self.OnFileImgOpen)
        self.ui.actionCalc1.triggered.connect(self.OnCalc1)
        self.ui.actionOpen_Folder.triggered.connect(self.OnFolderOpen)
             
        self.SettingsDlg = None
       
        self.file_img_path = None

        self.xmlDict = {}
        self.command = [Commands.NO]

        # sync signals
        self.ui.gView1.transformChanged.connect(
            lambda: self._sync_transform(self.ui.gView1, self.ui.gView2)
        )
        self.ui.gView2.transformChanged.connect(
            lambda: self._sync_transform(self.ui.gView2, self.ui.gView1)
        )
        self.ui.gView1.scrollChanged.connect(
            lambda: self._sync_scroll(self.ui.gView1, self.ui.gView2)
        )
        self.ui.gView2.scrollChanged.connect(
            lambda: self._sync_scroll(self.ui.gView2, self.ui.gView1)
        )
        #self.ui.statusbar.showMessage("test1")
        self.ui.gView1.pMainWindow = self
        self.statusBar().showMessage("No image")
               
        # Create undo action
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)  # Ctrl+Z
        self.undo_action.triggered.connect(self.undo)

        self.ui.actionHelp.triggered.connect(self.OnHelp)
        self.ui.actionPrint.triggered.connect(self.onPrint)
        self.ui.actionDimension.toggled.connect(self.on_dimension_toggled)

        # Add to menu bar
        self.addAction(self.undo_action)

        shortcut_std = QShortcut(QKeySequence.StandardKey.Save, self)
        shortcut_std.activated.connect(self.save)

        self.ui.gView1.fileImgOpenLink(self.OnFileImgOpen)
        self.ui.gView2.fileImgOpenLink(self.OnFileImgOpen)

        self.ui.gView1.command = self.command
        self.ui.gView2.command = self.command

    def onPrint(self):
        if self.save():
            self.OnFolderOpen()

    def settingsDlgEmitClose(self) :
         self.command[0] = Commands.NO 
         #print("self.command[0] = Commands.NO ")


    def clearAndReset(self):
        if(self.SettingsDlg != None):
            del self.SettingsDlg
            self.SettingsDlg = None

        self.ui.gView1.clearAndReset()
        self.ui.gView2.clearAndReset()
        self.ui.actionDimension.setChecked(False)


    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Escape):            
            self.ui.actionDimension.setChecked(False)

        if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            self.ui.gView1.increaseDimLineText()
            self.ui.gView2.increaseDimLineText()
        if event.key() == Qt.Key.Key_Minus:
            self.ui.gView1.reduceDimLineText()
            self.ui.gView2.reduceDimLineText()

    def on_dimension_toggled(self, checked: bool):
        if(checked):
            if(self.SettingsDlg != None):
                self.command[0] = Commands.DIMENLINE
                self.SettingsDlg.hide()
                #del self.SettingsDlg
                #self.SettingsDlg = None
        
        self.ui.gView1.OnDimenLine(checked)
        self.ui.gView2.OnDimenLine(checked)

    def closeEvent(self, event):
        self.save()
        # You can add custom logic here
        event.accept()  # Accept the close event
       
    def loadXml(self, filename):
        file = QFile(filename)
        if not file.open(QIODevice.ReadOnly | QIODevice.Text):
            return False
        size = file.size()  # Возвращает размер в байтах
        if size < 350:
            print ("Bad xml file")
            return False
        print(f"Размер файла XML: {size} байт")

        reader = QXmlStreamReader(file)
    
        while not reader.atEnd():
            reader.readNext()
        
            if reader.isStartElement():
                elname = reader.name()
        
            elif reader.isCharacters() and not reader.isWhitespace():
                text = reader.text().strip()
                if text:                    
                    if(elname != "DimenLine"):
                        self.xmlDict[elname] = text
        
            elif reader.hasError():
                print(f"Ошибка xml: {reader.errorString()}")
                return False
        return True



    def OnFileImgOpen(self, path1: str = None):            
        """
        Load image either via file dialog (when path is None) or directly by provided path.
        This keeps compatibility with QAction triggered (no args) and enables programmatic loading
        (e.g., via drag-and-drop which calls OnFileImgOpen(path)).
        """
        if isinstance(path1, bool):
            path1 = None

        if path1 is None or len(path1)==0:
            path1, selected_filter = QFileDialog.getOpenFileName(
                self,
                "Select a File",
                #"C:\\tmp3",
                "",
                "Images (*.png *.jpg *.jpeg *.bmp *.gif);;"            
            )
            if not path1:
                return
        else:
            # ensure it's a string and not a QUrl
            path1 = str(path1)

        if(path1 is not None and len(path1)!=0 ):
            self.save()

            if(self.SettingsDlg != None):
                self.SettingsDlg.close()
                del self.SettingsDlg
                self.SettingsDlg = None
                
            self.clearAndReset()
            self.file_img_path=path1
            self.ui.gView1.addImage(self.file_img_path)
            self.setWindowTitle(self.file_img_path)
            self.ui.gView1.linkSatusBar(self.statusBar())
            self.ui.gView2.linkSatusBar(self.statusBar())
            self.ui.gView1.link12CamView(self.ui.gView2)
            self.ui.gView2.link21CamView(self.ui.gView1)

            self.statusBar().showMessage("Image loaded")                  

            # check for EXR PNG XML
            output_dir, img_name_without_ext = self.getDir()
            if(QDir(output_dir).exists()):
                #check for png exr files
                exr_img = Path(output_dir) / Path(img_name_without_ext+".exr")
                png_img = Path(output_dir) / Path(img_name_without_ext+"_.png")
                data_file = Path(output_dir) / Path("data.xml")
                if(Path(exr_img).is_file() and Path(png_img).is_file() and Path(data_file).is_file()):
                    # load  png exr to view2                    
                    ret = self.loadXml(data_file)
                    if(not ret):
                        QMessageBox.warning(self, "Invalid or corrupt data.xml",  str("Recalculate project.")+str(output_dir))
                        return 
                    self.ui.gView2.addImage(png_img)

                    Device = self.xmlDict["Device"]
                    Quality = self.xmlDict["Quality"]
                    max_depth_m = float(self.xmlDict["max_depth_m"])
                    metric_scale_mnoj = float(self.xmlDict["metric_scale_mnoj"])
                    focal_X = float(self.xmlDict["fov_x"])
                    fx = float(self.xmlDict["fx"])
                    fy = float(self.xmlDict["fy"])

                    if "mesh_dense" in self.xmlDict:
                        mesh_dense = float(self.xmlDict["mesh_dense"])
                    else:
                        mesh_dense = 0.2

                    if(self.SettingsDlg != None):
                        del self.SettingsDlg
                    self.SettingsDlg = SettingsDlg(self)       
                    self.SettingsDlg.pFuncSave = self.save
                    self.SettingsDlg.setParam(Device, Quality, focal_X, max_depth_m, metric_scale_mnoj, mesh_dense)
                    self.ui.gView1.signalDimension.connect(self.SettingsDlg.funcAdjastDim)
                    self.ui.gView2.signalDimension.connect(self.SettingsDlg.funcAdjastDim)
                    self.SettingsDlg.onCloseSignal.connect(self.settingsDlgEmitClose)

                    self.ui.gView2.addEXR(exr_img,focal_X, fx, fy)
                    self.ui.gView1.addEXR(exr_img,focal_X, fx, fy)

                    self.ui.gView1.loadXml(data_file)
                    

    def save(self):
        if(self.file_img_path is not None and len(self.file_img_path)!=0 and self.ui.gView1.mogeExr is not None):
            mPATH = Path(self.file_img_path)
            img_name = mPATH.name
            img_name_without_ext = mPATH.stem
            img_dir = mPATH.parent        
            output_xml = Path(img_dir) / Path(img_name_without_ext) / Path("data.xml")
            #output_xml_copy = Path(img_dir) / Path(img_name_without_ext) / Path("data_copy.xml")

            if(output_xml.exists()):
                output_xml.unlink()

            file = QFile(output_xml)
            if not file.open(QIODevice.ReadWrite | QIODevice.Text):
                return False, f"Cannot open file: {output_xml}"

            writer = QXmlStreamWriter(file)
            writer.setAutoFormatting(True)
            writer.setAutoFormattingIndent(2)
            
            writer.writeStartDocument()
            writer.writeComment("Generated by FotomerMono")
            
            writer.writeStartElement("main")
            writer.writeAttribute("version", "1.0.0")

            self.SettingsDlg.saveXml(writer)
            self.ui.gView1.saveXml(writer)

            writer.writeEndElement()  # Close main
            writer.writeEndDocument()     

            file.close()
            #shutil.copy2(output_xml,output_xml_copy )

            if(self.ui.gView1.mogeExr is not None and self.ui.gView2.mogeExr is not None):
                output_dir = Path(img_dir) / Path(img_name_without_ext)
                path_s1 = str(Path.joinpath(output_dir,mPATH.name))
                path_s2 = str(Path.joinpath(output_dir,mPATH.stem+"_d"+mPATH.suffix))

                self.ui.gView1.printScene(path_s1)
                self.ui.gView2.printScene(path_s2) 

            print("Data saved")
            return True
        else: 
            print("No data to save")
            return False

    def getDir(self):
        if(self.file_img_path is not None and len(self.file_img_path)!=0):      
            mPATH = Path(self.file_img_path)
            img_name = mPATH.name
            img_name_without_ext = mPATH.stem
            img_dir = mPATH.parent
            output_dir = Path(img_dir) / Path(img_name_without_ext)
            return output_dir, img_name_without_ext
        return None, None

    def OnFolderOpen(self):
        if(self.file_img_path is not None):
            img_path = self.file_img_path       
            mPATH = Path(img_path)
            img_name = mPATH.name
            img_name_without_ext = mPATH.stem
            img_dir = mPATH.parent
            output_dir = Path(img_dir) / Path(img_name_without_ext)

            """
            if(self.ui.gView1.mogeExr is not None and self.ui.gView2.mogeExr is not None):
                path_s1 = str(Path.joinpath(output_dir,mPATH.name))
                path_s2 = str(Path.joinpath(output_dir,mPATH.stem+"_d"+mPATH.suffix))

                self.ui.gView1.printScene(path_s1)
                self.ui.gView2.printScene(path_s2)    
                """

            QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def _sync_transform(self, source, target):
        # block slot to avoid feedback
        target.transformChanged.disconnect()
        target.setTransform(source.transform())
        target.transformChanged.connect(
            lambda: self._sync_transform(target, source)
        )

    def _sync_scroll(self, source, target):
        # temporarily block
        target.scrollChanged.disconnect()
        target.horizontalScrollBar().setValue(
            source.horizontalScrollBar().value()
        )
        target.verticalScrollBar().setValue(
            source.verticalScrollBar().value()
        )
        target.scrollChanged.connect(
            lambda: self._sync_scroll(target, source)
        )

    def OnCalc1(self):
        self.on_dimension_toggled(False)
        self.ui.actionDimension.setChecked(False)
        if self.SettingsDlg is None:
            self.SettingsDlg = SettingsDlg(self)       
            self.SettingsDlg.pFuncSave = self.save  
            self.ui.gView1.signalDimension.connect(self.SettingsDlg.funcAdjastDim)
            self.ui.gView2.signalDimension.connect(self.SettingsDlg.funcAdjastDim)
            self.SettingsDlg.onCloseSignal.connect(self.settingsDlgEmitClose)

        self.SettingsDlg.file_img_path = self.file_img_path    
        self.SettingsDlg.show()
        self.SettingsDlg.setVisible(True)

        self.raise_()  # Поднять окно
        self.activateWindow()  # Активировать окно
        self.command[0] = Commands.CALC

      
    def connect_transformations(self):
        self.ui.gView1.transform().connect()(
            lambda: self.view2.setTransform(self.ui.gView1.transform())
        )
        self.ui.gView2.transform().connect()(
            lambda: self.ui.gView1.setTransform(self.ui.gView2.transform())
        )
        #self.ui.gView2.transform().scale()


    def connect_scrollbars(self):
        """Connect horizontal and vertical scroll bars between views"""
        # Connect horizontal scroll bars
        self.ui.gView1.horizontalScrollBar().valueChanged.connect(
            self.ui.gView2.horizontalScrollBar().setValue
        )
        self.ui.gView2.horizontalScrollBar().valueChanged.connect(
            self.ui.gView1.horizontalScrollBar().setValue
        )
        
        # Connect vertical scroll bars
        self.ui.gView1.verticalScrollBar().valueChanged.connect(
            self.ui.gView2.verticalScrollBar().setValue
        )
        self.ui.gView2.verticalScrollBar().valueChanged.connect(
            self.ui.gView1.verticalScrollBar().setValue
        )
        
        # Ensure they have same range initially
        self.sync_scrollbar_ranges()
        
    def sync_scrollbar_ranges(self):
        """Synchronize scroll bar ranges"""
        hbar1 = self.ui.gView1.horizontalScrollBar()
        hbar2 = self.ui.gView2.horizontalScrollBar()
        vbar1 = self.ui.gView1.verticalScrollBar()
        vbar2 = self.ui.gView2.verticalScrollBar()
        
        # Set same ranges
        hbar2.setRange(hbar1.minimum(), hbar1.maximum())
        vbar2.setRange(vbar1.minimum(), vbar1.maximum())
        
        # Set same page steps
        hbar2.setPageStep(hbar1.pageStep())
        vbar2.setPageStep(vbar1.pageStep())

    def on_zoom_changed(self, factor, scene_pos):
        # Sender’s already updated itself,
        # ensure the other one matches
        sender = self.sender()
        for v in (self.ui.gView1, self.ui.gView2):
            if v is not sender:
                v.zoom_at(scene_pos, factor)

    def undo(self):
        self.ui.gView1.undo()
        self.ui.gView2.undo()
        
    def OnHelp(self):
        img_dir = os.path.dirname(os.path.abspath(__file__))
        htm = Path(img_dir) / Path("help") / Path("help.htm")
        QDesktopServices.openUrl(QUrl.fromLocalFile(htm))

    # ----------------------
    # Drag & drop handling
    # ----------------------
    def dragEnterEvent(self, event):
        """Accept drag if it contains at least one supported local file URL."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if Path(path).suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.exr'):
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dropEvent(self, event):
        """Load the first dropped supported file."""
        if event.mimeData().hasUrls():
            # take first url only
            url = event.mimeData().urls()[0]
            if url.isLocalFile():
                path = url.toLocalFile()
                if Path(path).is_file() and Path(path).suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.exr'):
                    # call the same loader path used by File dialog
                    self.OnFileImgOpen(path)
                    event.acceptProposedAction()
                    return
        event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    #widget.setWindowState(Qt.WindowState.WindowMaximized)
    widget.show()
    sys.exit(app.exec())
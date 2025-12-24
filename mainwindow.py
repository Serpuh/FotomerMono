import os
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PySide6.QtCore import Qt

from PySide6.QtGui import QTransform

from SettingsDlg import SettingsDlg

path1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path1)

"""
from moge.model.v2 import MoGeModel
# from moge.model import import_model_class_by_version
from moge.utils.io import save_glb, save_ply
from moge.utils.vis import colorize_depth, colorize_normal
# from moge.utils.geometry_numpy import depth_occlusion_edge_numpy
"""

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
#os.environ["QT_DEBUG_PLUGINS"] = "1"


# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py
# C:\MoGe\MoGe\Moge2\Scripts\pyside6-uic C:\MoGe\MoGe\FotomerMono\form.ui -o C:\MoGe\MoGe\FotomerMono\ui_form.py
from ui_form import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionLoadImage.triggered.connect(self.OnFileImgOpen)
        self.ui.actionCalc1.triggered.connect(self.OnCalc1)
        self.SettingsDlg = None
        self.file_img_path = None

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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print(f"Left button pressed at view coordinates: {event.pos()}")

    def OnFileImgOpen(self):       
        self.file_img_path, selected_filter = QFileDialog.getOpenFileName(
            self,
            "Select a File",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;"            
        )
        if(self.file_img_path): 
            self.file_img_path = self.ui.gView1.addImage(self.file_img_path)

            self.ui.gView2.addImage(self.file_img_path)

            self.setWindowTitle(self.file_img_path)

            self.ui.gView1.setSatusBar(self.statusBar())
            self.ui.gView2.setSatusBar(self.statusBar())

            hh=10
            """
            QMessageBox.information(self, "qqq", self.file_img_path)
            self.calc1()
            """

    def OnCalc1(self):
        if self.SettingsDlg is None or not self.SettingsDlg.isVisible():
            self.SettingsDlg = SettingsDlg(self)            
            self.SettingsDlg.file_img_path = self.file_img_path
            #self.SettingsDlg.setModal(False)  # Explicitly set to non-modal
            self.SettingsDlg.show()  # Use show() instead of exec()
            #self.SettingsDlg.

      
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    #widget.setWindowState(Qt.WindowState.WindowMaximized)
    widget.show()
    sys.exit(app.exec())

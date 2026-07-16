import sys
import torch
import os

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import numpy as np
import utils3d
import math
from pathlib import Path
import time

path1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path1)

from moge.model.v2 import MoGeModel # type: ignore
from moge.utils.io import save_glb, save_ply # type: ignore
from moge.utils.vis import colorize_depth, colorize_normal # type: ignore

from PySide6.QtWidgets import QDialog, QApplication
from PySide6.QtCore import QUrl, QRegularExpression, QTimer, QObject, Signal, Slot, QXmlStreamWriter
from PySide6.QtGui import QDesktopServices, QDoubleValidator, QRegularExpressionValidator, QTextCursor, QCloseEvent

from ui_SettingsDlg import Ui_SettingsDlg
from ui_form import Ui_MainWindow
from Commands import Commands

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
import cv2

class SettingsDlg(QDialog, QObject):
    onCloseSignal = Signal()
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = Ui_SettingsDlg()
        self.ui.setupUi(self)

        self.ui.calcButton.clicked.connect(self.OnButtonCalc)
        self.file_img_path = None
        self.Ui_MainWindow = parent.ui
        
        self.ui.openFolderButton.clicked.connect(self.OnFolderOpen)

        self.ui.gpuComboBox.addItem("gpu")
        self.ui.gpuComboBox.addItem("cpu")
        self.ui.gpuComboBox.setCurrentIndex(0)
        #self.ui.text1.setEnabled(False)
        if(torch.cuda.is_available()):
            self.ui.gpuComboBox.setCurrentIndex(0)  
            self.ui.text1.setPlainText("GPU available")
            self.ui.text1.moveCursor(QTextCursor.End)
        else:
           self.ui.gpuComboBox.setCurrentIndex(1)
           self.ui.gpuComboBox.setEnabled(False)
           self.ui.text1.setPlainText("GPU not available")

        self.ui.qualityComboBox.addItem("small")
        self.ui.qualityComboBox.addItem("middle")
        self.ui.qualityComboBox.addItem("best")
        self.ui.qualityComboBox.setCurrentIndex(2)        
        
        self.ui.label_dimension.setEnabled(False)
        self.ui.dimenScale.setEnabled(False)

        #self.fov_x: float = 0
        self.fov_x: float = 0
        self.max_depth_m = 50
        self.metric_scale_mnoj = 1.
        # for dimension correction
        self.oldDim = 0.0
        self.newDim = 0.0
        self.mesh_dense = 0.2

        self.ui.fov_x.setText(f"{self.fov_x:.1f}")
        self.ui.max_depth_m.setText(f"{self.max_depth_m:.1f}")
        self.ui.metric_scale_mnoj.setText(f"{self.metric_scale_mnoj:.3f}")   
        self.ui.dimenScale.setText(f"{self.newDim:.1f}")
        self.ui.mesh_dense.setText(f"{self.mesh_dense:.2f}")

        validator = QDoubleValidator()     
        #validator.setNotation(QDoubleValidator.StandardNotation)
        validator = QRegularExpressionValidator(QRegularExpression(r"^(0|[1-9]\d*)(\.\d+)?$"))          
        #validator.setRange(0.1, 120.0, 2)
        self.ui.fov_x.setValidator(validator)
        self.ui.max_depth_m.setValidator(validator)
        self.ui.metric_scale_mnoj.setValidator(validator)
        self.ui.dimenScale.setValidator(validator)
        self.ui.mesh_dense.setValidator(validator)

        #self.Ui_MainWindow.gView1.saveJson()
        self.pFuncSave=None
        

    def funcAdjastDim(self, oldDim: float):
        if oldDim > 0:
            if oldDim < 1:
                str1 =  f"{oldDim:.3f}"
            elif oldDim < 10:
                str1 =  f"{oldDim:.2f}"
            elif oldDim < 100:
                str1 =  f"{oldDim:.1f}"

            self.ui.label_dimension.setText(f"{str1} adjast to ->");
            self.ui.label_dimension.setEnabled(True)
            self.ui.dimenScale.setEnabled(True)  
            self.oldDim = oldDim
        else:
            self.ui.label_dimension.setText(f"Adjast\ndimension");
            self.ui.label_dimension.setEnabled(False)
            self.ui.dimenScale.setEnabled(False)  
        #print(oldDim)
       

    def setParam(self, device, quality, fov_x, max_depth_m, metric_scale_mnoj, mesh_dense):
        if(device == "gpu"):
            self.ui.gpuComboBox.setCurrentIndex(0)
        else: 
            self.ui.gpuComboBox.setCurrentIndex(1)

        match quality:
            case "small":
                 self.ui.qualityComboBox.setCurrentIndex(0)
            case "middle":
                 self.ui.qualityComboBox.setCurrentIndex(1)
            case "best":
                 self.ui.qualityComboBox.setCurrentIndex(2)
            case _:
                self.ui.qualityComboBox.setCurrentIndex(1)

        self.fov_x=fov_x
        self.max_depth_m = max_depth_m
        self.metric_scale_mnoj = metric_scale_mnoj
        self.mesh_dense = mesh_dense

        self.ui.max_depth_m.setText(f"{self.max_depth_m:.1f}")
        self.ui.metric_scale_mnoj.setText(f"{self.metric_scale_mnoj:.3f}")
        self.ui.fov_x.setText(f"{self.fov_x:.1f}")
        self.ui.mesh_dense.setText(f"{self.mesh_dense:.2f}")
        h=0

    def saveXml(self, writer: QXmlStreamWriter):
        writer.writeStartElement("Settings")

        writer.writeTextElement("Device", self.ui.gpuComboBox.currentText())
        writer.writeTextElement("Quality", self.ui.qualityComboBox.currentText())
        #writer.writeTextElement("fov_x", str(self.fov_x))
        writer.writeTextElement("max_depth_m", str(self.max_depth_m))
        writer.writeTextElement("metric_scale_mnoj", str(self.metric_scale_mnoj))
        writer.writeTextElement("mesh_dense", str(self.mesh_dense))

        writer.writeEndElement()
        hh=10

    def show(self):
        # Можно изменить состояние перед показом
        if(self.file_img_path == None):
            self.ui.calcButton.setEnabled(False)
        else:
            self.ui.calcButton.setEnabled(True)

        """
        if(self.fov_x == None):
            self.ui.fov_x.setEnabled(False)
        else:
            self.ui.fov_x.setEnabled(True)
        """

        # Вызываем родительский метод
        super().show()
        
        # Дополнительные действия после показа
        self.after_show()
    
    def after_show(self):
        #print("The dialog is shown")
        hh=10
        # Дополнительная логика после показа

    def updateText(self):
        self.ui.text1.update()
        
    def OnButtonCalc(self):   
        # Disable the button to avoid re-entrance
        self.ui.calcButton.setEnabled(False)

        # Log start and ensure the widget updates immediately
        self.ui.text1.appendPlainText("Calculation start")
        self.ui.text1.moveCursor(QTextCursor.End)
        QApplication.processEvents()

        img_path = self.file_img_path       
        mPATH = Path(img_path)
        img_name = mPATH.name
        img_name_without_ext = mPATH.stem
        img_dir = mPATH.parent
        output_dir = Path(img_dir) / Path(img_name_without_ext)

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        dirPath = project_root
     

        match self.ui.qualityComboBox.currentText():
            case "best":
                modelPath = dirPath / Path("Models") / Path("model_best.pt")
            case "middle":
                modelPath = dirPath / Path("Models") / Path("model_middle.pt")
            case "small":
                modelPath = dirPath / Path("Models") / Path("model_small.pt")
            case _:
                modelPath = dirPath / Path("Models") / Path("model_middle.pt")

        start = time.time()

        cuda_available = torch.cuda.is_available()        
        print(f"cuda_available - {cuda_available}")

        device = torch.device("cpu")
        if(self.ui.gpuComboBox.currentText()=="gpu"):
            device = torch.device("cuda")
            b_use_fp16 = True
            print("use cuda")
        else:
            device = torch.device("cpu")
            b_use_fp16 = False
            print("use cpu")
        
        model = MoGeModel.from_pretrained(modelPath).to(device)
        
        end = time.time()
        print(f"Model loaded: {end - start:.2f} sec")

        # Append (don't overwrite) and force UI update
        self.ui.text1.appendPlainText(f"Model loaded: {end - start:.2f} sec")
        self.ui.text1.moveCursor(QTextCursor.End)
        QApplication.processEvents()
                
        input_image = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB) 
        input_image_t = torch.tensor(input_image / 255, dtype=torch.float32, device=device).permute(2, 0, 1)    
        
        if(self.fov_x is not None):
            self.fov_x = float(self.ui.fov_x.text())
        if(self.fov_x == 0):
            self.fov_x = None

        self.max_depth_m = float(self.ui.max_depth_m.text())
        self.metric_scale_mnoj = float(self.ui.metric_scale_mnoj.text())
        self.newDim = float(self.ui.dimenScale.text())    
        self.mesh_dense = float(self.ui.mesh_dense.text())    
        
        if(self.newDim>0.):
            sc = self.newDim/self.oldDim
            self.metric_scale_mnoj *= sc
            self.ui.metric_scale_mnoj.setText(f"{self.metric_scale_mnoj:.3f}")
            QApplication.processEvents()
            h=0

        start = time.time()
        """
        def infer(
        self, 
        image: torch.Tensor, 
        num_tokens: int = None,
        resolution_level: int = 9,
        force_projection: bool = True,
        apply_mask: bool = True,
        fov_x: Optional[Union[Number, torch.Tensor]] = None,
        use_fp16: bool = True,
        max_depth: Optional[Union[Number, torch.Tensor]] = None,
    ) -> Dict[str, torch.Tensor]:
        output = model.infer(input_image_t,None,9,True,True,None,4.,False)
        """
        # Log that inference is starting
        self.ui.text1.appendPlainText("Running inference...")
        self.ui.text1.moveCursor(QTextCursor.End)

        self.Ui_MainWindow.gView1.ClearExrView1()
        self.Ui_MainWindow.gView2.ClearExrView2()

        QApplication.processEvents()

        output = model.infer(
                input_image_t,
                num_tokens=None,
                resolution_level=9,
                force_projection=True,
                apply_mask=True,
                fov_x=self.fov_x,                
                use_fp16=b_use_fp16, # True-Gpu, False-CPU
                max_depth_m=self.max_depth_m,
                metric_scale_mnoj = self.metric_scale_mnoj)
        
        points, depth, mask, intrinsics, focal_X, fx, fy  = output['points'].cpu().numpy(), output['depth'].cpu().numpy(), output['mask'].cpu().numpy(), output['intrinsics'].cpu().numpy(),  output['focal'].cpu().numpy(),  output['fx'].cpu().numpy(),  output['fy'].cpu().numpy()
        
        self.fx=fx
        self.fy=fy
        fxx = intrinsics[0,0]
        fyy = intrinsics[1,1]
        normal = output['normal'].cpu().numpy()
        end = time.time()
        print("Calculation done "+img_name+f" {end - start: .2f} sec")
        print("focal_X "+f"{focal_X: .1f}")

        # Append results and update UI immediately
        self.ui.text1.appendPlainText(f"infer done {end - start: .2f} sec\nfocal_X {focal_X:.1f}\nSaving files...")
        self.ui.text1.moveCursor(QTextCursor.End)
        QApplication.processEvents()

        self.fov_x = focal_X
        self.ui.fov_x.setText(f"{self.fov_x:.1f}")

        start = time.time()
        cv2.imwrite(Path.joinpath(output_dir,img_name_without_ext+"_.png"), cv2.cvtColor(colorize_depth(depth), cv2.COLOR_RGB2BGR))
        cv2.imwrite(Path.joinpath(output_dir,img_name_without_ext+".exr"), depth, [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_FLOAT])        
        #cv2.imwrite(Path.joinpath(output_dir,'mask.png'), (mask * 255).astype(np.uint8))
        
        self.Ui_MainWindow.gView2.addImage(Path.joinpath(output_dir,img_name_without_ext+"_.png"))

        # ADD THIS BLOCK FOR REAL SENSE FORMAT
        #depth_mm = (depth * 1000).astype(np.uint16)  # Convert meters to mm, uint16
        #cv2.imwrite(Path.joinpath(output_dir,img_name_without_ext+"_rs.png"), depth_mm)  # PNG preserves uint16

        self.Ui_MainWindow.gView1.addEXR(Path.joinpath(output_dir,img_name_without_ext+".exr"),focal_X, fx, fy)
        self.Ui_MainWindow.gView2.addEXR(Path.joinpath(output_dir,img_name_without_ext+".exr"),focal_X, fx, fy)        
        
        end = time.time()
        print("Save time with no ply "+img_name+f" {end - start:.2f} sec")
                      

        if (self.ui.bPlyMake.isChecked()):
            mask_cleaned = mask & ~utils3d.np.depth_map_edge(depth, rtol=self.mesh_dense/2)
            height, width = input_image.shape[:2]
            faces, vertices, vertex_colors, vertex_uvs, vertex_normals = utils3d.np.build_mesh_from_map(
                    points,
                    input_image.astype(np.float32) / 255,
                    utils3d.np.uv_map(height, width),
                    normal,
                    mask=mask_cleaned,
                    tri=True
            )
            self.ui.text1.appendPlainText(f"Filtered {vertices.size} points cloud\n")
            self.ui.text1.moveCursor(QTextCursor.End)  
            img_name.lower()
            img_name = img_name.replace("jpg","ply")
            vertex_normals = vertex_normals * [1, -1, -1]
            save_ply(Path.joinpath(output_dir,img_name_without_ext+".ply"), vertices, np.zeros((0, 3), dtype=np.int32), vertex_colors, vertex_normals)
            print("ply file saved")
            self.ui.text1.appendPlainText("ply file saved")
            self.ui.text1.moveCursor(QTextCursor.End)
  
        
        path_s1 = str(Path.joinpath(output_dir,mPATH.name))
        path_s2 = str(Path.joinpath(output_dir,mPATH.stem+"_d"+mPATH.suffix))

        self.Ui_MainWindow.gView1.printScene(path_s1)
        self.Ui_MainWindow.gView2.printScene(path_s2)        

        self.ui.text1.appendPlainText(f"Files saved to {output_dir}")
        self.ui.text1.moveCursor(QTextCursor.End)
        
        self.ui.calcButton.setEnabled(True)
        self.ui.fov_x.setEnabled(True)
                
        self.pFuncSave()

        self.ui.label_dimension.setText(f"Adjast\ndimension");
        self.ui.label_dimension.setEnabled(False)
        self.ui.dimenScale.setEnabled(False)         
        self.newDim = 0.0
        self.ui.dimenScale.setText(f"{self.newDim:.1f}")

        self.raise_()  # Поднять окно
        self.activateWindow()  # Активировать окно
        

    def OnFolderOpen(self):
        if(self.file_img_path is not None):
            img_path = self.file_img_path       
            mPATH = Path(img_path)
            img_name = mPATH.name
            img_name_without_ext = mPATH.stem
            img_dir = mPATH.parent
            output_dir = Path(img_dir) / Path(img_name_without_ext)
            QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))

    def closeEvent(self, event: QCloseEvent):
        """Вызывается при попытке закрыть диалог"""
        # Здесь можно добавить логику перед закрытием
        #print("Dialog is about to close")
        #self.Ui_MainWindow.command[0] = Commands.NO       
        self.onCloseSignal.emit()
        # Пример: запросить подтверждение
        # from PySide6.QtWidgets import QMessageBox
        # reply = QMessageBox.question(self, 'Confirm', 
        #                              'Are you sure you want to close?',
        #                              QMessageBox.Yes | QMessageBox.No)
        # if reply == QMessageBox.Yes:
        #     event.accept()  # Принять закрытие
        # else:
        #     event.ignore()  # Игнорировать закрытие
        
        # Стандартное поведение - принять событие
        #event.accept()


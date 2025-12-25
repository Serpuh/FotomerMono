import sys
import torch

import numpy as np
import utils3d
import time
import os
import math
from pathlib import Path

import cv2
import time

path1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path1)

#from ..moge.model.v2 import MoGeModel
#from model.v2 import MoGeModel
#from ..moge import MoGeModel
from moge.model.v2 import MoGeModel
# from moge.model import import_model_class_by_version

from moge.utils.io import save_glb, save_ply
from moge.utils.vis import colorize_depth, colorize_normal

# from moge.utils.geometry_numpy import depth_occlusion_edge_numpy

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QUrl, QRegularExpression, QTimer
from PySide6.QtGui import QDesktopServices, QDoubleValidator, QRegularExpressionValidator, QTextCursor

from ui_SettingsDlg import Ui_SettingsDlg

from ui_form import Ui_MainWindow

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


class SettingsDlg(QDialog):
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
        self.ui.text1.setEnabled(False)
        if(torch.cuda.is_available()):
            self.ui.gpuComboBox.setCurrentIndex(0)  
            self.ui.text1.setPlainText("gpu available\n")
            self.ui.text1.moveCursor(QTextCursor.End)
        else:
           self.ui.gpuComboBox.setCurrentIndex(1)
           self.ui.gpuComboBox.setEnabled(False)
           self.ui.text1.setPlainText("gpu not available\n")
           self.text_edit.moveCursor(QTextCursor.End)

        self.ui.qualityComboBox.addItem("small")
        self.ui.qualityComboBox.addItem("middle")
        self.ui.qualityComboBox.addItem("best")
        self.ui.qualityComboBox.setCurrentIndex(1)
                

        self.fov_x=None
        self.max_depth_m = 100
        self.ui.max_depth_m.setText(f"{self.max_depth_m:.1f}")

        validator = QDoubleValidator()     
        #validator.setNotation(QDoubleValidator.StandardNotation)
        #validator = QRegularExpressionValidator(QRegularExpression(r"^(0|[1-9]\d*)(\.\d+)?$"))          
        validator.setRange(0.1, 120.0, 2)
        self.ui.fov_x.setValidator(validator)
        self.ui.max_depth_m.setValidator(validator)
        hh=10

    def show(self):
        # Дополнительные действия перед показом
        #print("The dialog will be shown")
        
        # Можно изменить состояние перед показом
        if(self.file_img_path == None):
            self.ui.calcButton.setEnabled(False)
        else:
            self.ui.calcButton.setEnabled(True)

        if(self.fov_x == None):
            self.ui.fov_x.setEnabled(False)
        else:
            self.ui.fov_x.setEnabled(True)
        
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
        self.ui.text1.setPlainText(f"Calculation start\n")
        self.ui.text1.moveCursor(QTextCursor.End)
        self.ui.text1.update()

        QTimer.singleShot(1000,self.updateText)       

        img_path = self.file_img_path       
        mPATH = Path(img_path)
        img_name = mPATH.name
        img_name_without_ext = mPATH.stem
        img_dir = mPATH.parent
        output_dir = Path(img_dir) / Path(img_name_without_ext)

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        dirPath = project_root
        #dirPath = Path(os.path.dirname(os.path.abspath(__file__)))
        modelQuality = 0
        modelPath = dirPath / Path("Models") / Path("model_best.pt")
        if(modelQuality == 1):
            modelPath = dirPath / Path("Models") / Path("model_middle.pt")
        if(modelQuality == 2):
            modelPath = dirPath / Path("Models") / Path("model_small.pt")

        start = time.time()

        cuda_available = torch.cuda.is_available()        
        print(f"cuda_available - {cuda_available}")

        device = torch.device("cpu")
        if(self.ui.gpuComboBox.currentText()=="gpu"):
            device = torch.device("cuda")
            print("use cuda")
        else:
            device = torch.device("cpu")
            print("use cpu")
        
        model = MoGeModel.from_pretrained(modelPath).to(device)
        #model.max_depth_m = 100
        end = time.time()
        print(f"model = MoGeModel.from_pretrained: {end - start:.2f} sec")

        self.ui.text1.setPlainText(f"model = MoGeModel.from_pretrained: {end - start:.2f} sec\n")
        self.ui.text1.moveCursor(QTextCursor.End)

        # Read the input image and convert to tensor (3, H, W) with RGB values normalized to [0, 1]
        input_image = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB) 
        #h,w = input_image.shape[:2]
        #newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 0, (w, h))
        #input_image_undst = cv2.undistort(input_image, camera_matrix, dist_coefs, None, newcameramtx)
        #input_image_undst = input_image
        input_image_t = torch.tensor(input_image / 255, dtype=torch.float32, device=device).permute(2, 0, 1)    


        #fov_1 = math.degrees(math.atan(float(2592)/float(5800)))*2
        #fov_1 = 1

        #diag = math.sqrt(h**2+w**2)
        #fov_1 = math.degrees(math.atan(float(diag/2)/float(5800)))*2
        #fov_1 = 55
        # Infer 
        
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
        output = model.infer(
                input_image_t,
                num_tokens=None,
                resolution_level=9,
                force_projection=True,
                apply_mask=True,
                fov_x=None,                
                use_fp16=False,
                max_depth_m=self.max_depth_m)
        #output = model.infer(input_image_t)
        points, depth, mask, intrinsics, focal_X  = output['points'].cpu().numpy(), output['depth'].cpu().numpy(), output['mask'].cpu().numpy(), output['intrinsics'].cpu().numpy(),  output['focal'].cpu().numpy()
        normal = output['normal'].cpu().numpy()
        end = time.time()
        print("Calculation done "+img_name+f" {end - start: .2f} sec")
        print("focal_X "+f"{focal_X: .1f}")

        self.ui.text1.setPlainText(f"infer done {end - start: .2f} sec\nfocal_X "+f"{focal_X: .1f}")
        self.ui.text1.moveCursor(QTextCursor.End)

        self.fov_x = focal_X
        self.ui.fov_x.setText(f"{self.fov_x:.1f}")
        

        start = time.time()
        cv2.imwrite(Path.joinpath(output_dir,img_name_without_ext+".png"), cv2.cvtColor(colorize_depth(depth), cv2.COLOR_RGB2BGR))
        cv2.imwrite(Path.joinpath(output_dir,img_name_without_ext+".exr"), depth, [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_FLOAT])
        #cv2.imwrite(str(save_path + 'depth.exr'), depth, [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_FLOAT])
        cv2.imwrite(Path.joinpath(output_dir,'mask.png'), (mask * 255).astype(np.uint8))

        self.Ui_MainWindow.gView2.addImage(Path.joinpath(output_dir,img_name_without_ext+".png"))
        self.Ui_MainWindow.gView2.addEXR(Path.joinpath(output_dir,img_name_without_ext+".exr"),focal_X)
        self.Ui_MainWindow.gView1.addEXR(Path.joinpath(output_dir,img_name_without_ext+".exr"),focal_X)
        

        #cv2.imwrite(str(save_pathtntdjqtntdPA110016 + 'points.exr'), cv2.cvtColor(points, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_FLOAT])
        #cv2.imwrite(str(save_path + 'points.jpg'), cv2.cvtColor(points, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 100])
        end = time.time()
        print("Save time with no ply "+img_name+f" {end - start:.2f} sec")

        mask_cleaned = mask & ~utils3d.np.depth_map_edge(depth, 0.4)

        height, width = input_image.shape[:2]

        faces, vertices, vertex_colors, vertex_uvs, vertex_normals = utils3d.np.build_mesh_from_map(
                points,
                input_image.astype(np.float32) / 255,
                utils3d.np.uv_map(height, width),
                normal,
                mask=mask_cleaned,
                tri=True
        )
        img_name.lower()
        img_name = img_name.replace("jpg","ply")
        vertex_normals = vertex_normals * [1, -1, -1]
        save_ply(Path.joinpath(output_dir,img_name_without_ext+".ply"), vertices, np.zeros((0, 3), dtype=np.int32), vertex_colors, vertex_normals)

        input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        #input_image_undst = cv2.cvtColor(input_image_undst, cv2.COLOR_BGR2RGB)
        cv2.imwrite(Path.joinpath(output_dir,mPATH.name), input_image)
        #cv2.imwrite(Path.joinpath(output_dir,'ishodnik_undist.jpg'), input_image_undst)

        

        print("ply file saved")


    def OnFolderOpen(self):
        img_path = self.file_img_path       
        mPATH = Path(img_path)
        img_name = mPATH.name
        img_name_without_ext = mPATH.stem
        img_dir = mPATH.parent
        output_dir = Path(img_dir) / Path(img_name_without_ext)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))



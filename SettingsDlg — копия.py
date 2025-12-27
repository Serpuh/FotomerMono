import sys
import torch
import os

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import numpy as np
import utils3d
import time

import math
from pathlib import Path

import time

path1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path1)

from moge.model.v2 import MoGeModel
from moge.utils.io import save_glb, save_ply
from moge.utils.vis import colorize_depth, colorize_normal

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QUrl, QRegularExpression, QTimer, QObject, Signal, Slot
from PySide6.QtGui import QDesktopServices, QDoubleValidator, QRegularExpressionValidator, QTextCursor

from ui_SettingsDlg import Ui_SettingsDlg

from ui_form import Ui_MainWindow


project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
import cv2

class CalcWorker(QObject):
    # Signals to communicate with the main (GUI) thread
    progress = Signal(str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, img_path: str, use_gpu: bool, model_quality: int, max_depth_m: float, metric_scale_mnoj: float, project_root: Path):
        super().__init__()
        self.img_path = img_path
        self.use_gpu = use_gpu
        self.model_quality = model_quality 

        self.max_depth_m = max_depth_m        
        self.metric_scale_mnoj = metric_scale_mnoj

        self.project_root = project_root
        self._is_cancelled = False

    @Slot()
    def run(self):
        """Long-running work performed in background thread."""
        try:
            self.progress.emit("Calculation start")
            start_total = time.time()

            img_path = self.img_path
            mPATH = Path(img_path)
            img_name = mPATH.name
            img_name_without_ext = mPATH.stem
            img_dir = mPATH.parent
            output_dir = Path(img_dir) / Path(img_name_without_ext)

            if not os.path.exists(output_dir):
                os.mkdir(output_dir)

            dirPath = self.project_root
            modelQuality = self.model_quality
            modelPath = dirPath / Path("Models") / Path("model_best.pt")
            if modelQuality == 1:
                modelPath = dirPath / Path("Models") / Path("model_middle.pt")
            if modelQuality == 2:
                modelPath = dirPath / Path("Models") / Path("model_small.pt")

            t0 = time.time()
            device = torch.device("cuda" if self.use_gpu and torch.cuda.is_available() else "cpu")
            self.progress.emit(f"Using device: {device}")
            model = MoGeModel.from_pretrained(modelPath).to(device)
            t1 = time.time()
            self.progress.emit(f"Model loaded: {t1 - t0:.2f} sec")

            # Read image
            input_image_bgr = cv2.imread(img_path)
            if input_image_bgr is None:
                raise RuntimeError(f"Failed to read image: {img_path}")
            input_image = cv2.cvtColor(input_image_bgr, cv2.COLOR_BGR2RGB)
            input_image_t = torch.tensor(input_image / 255.0, dtype=torch.float32, device=device).permute(2, 0, 1)

            # Run inference
            t_inf_start = time.time()
            self.progress.emit("Running inference...")
            output = model.infer(
                input_image_t,
                num_tokens=None,
                resolution_level=9,
                force_projection=True,
                apply_mask=True,
                fov_x=None,
                use_fp16=False,
                max_depth_m=self.max_depth_m,
                metric_scale_mnoj = self.metric_scale_mnoj
            )

            t_inf_end = time.time()
            self.progress.emit(f"Inference done {t_inf_end - t_inf_start:.2f} sec")

            # Extract outputs (ensure correct .cpu() usage)
            points = output['points'].cpu().numpy() if 'points' in output else None
            depth = output['depth'].cpu().numpy() if 'depth' in output else None
            mask = output['mask'].cpu().numpy() if 'mask' in output else None
            intrinsics = output['intrinsics'].cpu().numpy() if 'intrinsics' in output else None
            # Fix: use proper cpu() to retrieve focal
            focal_t = output.get('focal', None)
            if focal_t is None:
                focal_X = 0.0
            else:
                try:
                    focal_X = float(focal_t.cpu().numpy().item())
                except Exception:
                    # fallback if shape is different
                    focal_X = float(focal_t.cpu().numpy().flatten()[0])

            normal = output['normal'].cpu().numpy() if 'normal' in output else None

            # Save depth visualization and EXR
            t_save_start = time.time()
            depth_vis_path = output_dir / f"{img_name_without_ext}.png"
            depth_exr_path = output_dir / f"{img_name_without_ext}.exr"
            mask_path = output_dir / "mask.png"

            cv2.imwrite(str(depth_vis_path), cv2.cvtColor(colorize_depth(depth), cv2.COLOR_RGB2BGR))
            # write exr (depth) as float
            cv2.imwrite(str(depth_exr_path), depth, [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_FLOAT])
            cv2.imwrite(str(mask_path), (mask * 255).astype(np.uint8))

            t_save_mid = time.time()
            self.progress.emit(f"Saved depth images {t_save_mid - t_save_start:.2f} sec")

            # Clean mask and build mesh
            mask_cleaned = mask & ~utils3d.np.depth_map_edge(depth, 0.4)
            height, width = input_image.shape[:2]

            faces, vertices, vertex_colors, vertex_uvs, vertex_normals = utils3d.np.build_mesh_from_map(
                points,
                input_image.astype(np.float32) / 255.0,
                utils3d.np.uv_map(height, width),
                normal,
                mask=mask_cleaned,
                tri=True
            )

            ply_path = output_dir / f"{img_name_without_ext}.ply"
            # adjust normals sign to match original code behavior
            vertex_normals = vertex_normals * [1, -1, -1]
            save_ply(str(ply_path), vertices, np.zeros((0, 3), dtype=np.int32), vertex_colors, vertex_normals)

            # Save original image into output dir
            img_out_path = output_dir / mPATH.name
            # convert back to BGR for OpenCV saving (we have input_image in RGB)
            cv2.imwrite(str(img_out_path), cv2.cvtColor(input_image, cv2.COLOR_RGB2BGR))

            t_end = time.time()
            total_time = t_end - start_total
            self.progress.emit(f"All done: {total_time:.2f} sec")
            # Emit finished with data the UI thread can use
            result = {
                "output_dir": str(output_dir),
                "img_name_without_ext": img_name_without_ext,
                "depth_png": str(depth_vis_path),
                "depth_exr": str(depth_exr_path),
                "ply": str(ply_path),
                "focal_X": focal_X,
            }
            self.finished.emit(result)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.error.emit(f"Error in worker: {e}\n{tb}")


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

        self.ui.qualityComboBox.addItem("small")
        self.ui.qualityComboBox.addItem("middle")
        self.ui.qualityComboBox.addItem("best")
        self.ui.qualityComboBox.setCurrentIndex(1)                

        self.fov_x=None
        self.max_depth_m = 100
        self.metric_scale_mnoj = 1.0

        self.ui.max_depth_m.setText(f"{self.max_depth_m:.1f}")
        self.ui.metric_scale_mnoj.setText(f"{self.metric_scale_mnoj:.3f}")
        

        validator = QDoubleValidator()     
        #validator.setNotation(QDoubleValidator.StandardNotation)
        validator = QRegularExpressionValidator(QRegularExpression(r"^(0|[1-9]\d*)(\.\d+)?$"))          
        #validator.setRange(0.1, 120.0, 2)
        self.ui.fov_x.setValidator(validator)
        self.ui.max_depth_m.setValidator(validator)
        self.ui.metric_scale_mnoj.setValidator(validator)

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
        self.ui.calcButton.setEnabled(False)
        self.ui.text1.appendPlainText(f"Calculation start\n")
        #self.ui.text1.setPlainText(f"Calculation start\n")
        self.ui.text1.moveCursor(QTextCursor.End)
        self.ui.text1.update()

        QTimer.singleShot(1000,self.updateText)       
        time.sleep(1)

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
        
        end = time.time()
        print(f"model = MoGeModel.from_pretrained: {end - start:.2f} sec")

        self.ui.text1.setPlainText(f"model = MoGeModel.from_pretrained: {end - start:.2f} sec\n")
        self.ui.text1.moveCursor(QTextCursor.End)
                
        input_image = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB) 
        input_image_t = torch.tensor(input_image / 255, dtype=torch.float32, device=device).permute(2, 0, 1)    
        
        if(self.fov_x is not None):
            self.fov_x = float(self.ui.fov_x.text())
        self.max_depth_m = float(self.ui.max_depth_m.text())
        self.metric_scale_mnoj = float(self.ui.metric_scale_mnoj.text())
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
                fov_x=self.fov_x,                
                use_fp16=False,
                max_depth_m=self.max_depth_m,
                metric_scale_mnoj = self.metric_scale_mnoj)
        #output = model.infer(input_image_t)
        points, depth, mask, intrinsics, focal_X, fx, fy  = output['points'].cpu().numpy(), output['depth'].cpu().numpy(), output['mask'].cpu().numpy(), output['intrinsics'].cpu().numpy(),  output['focal'].cpu().numpy(),  output['fx'].cpu().numpy(),  output['fy'].cpu().numpy()
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
        cv2.imwrite(Path.joinpath(output_dir,'mask.png'), (mask * 255).astype(np.uint8))

        self.Ui_MainWindow.gView2.addImage(Path.joinpath(output_dir,img_name_without_ext+".png"))
        self.Ui_MainWindow.gView2.addEXR(Path.joinpath(output_dir,img_name_without_ext+".exr"),focal_X, fx, fy)
        self.Ui_MainWindow.gView1.addEXR(Path.joinpath(output_dir,img_name_without_ext+".exr"),focal_X, fx, fy)
        
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
        cv2.imwrite(Path.joinpath(output_dir,mPATH.name), input_image)

        print("ply file saved")
        self.ui.calcButton.setEnabled(True)


    def OnFolderOpen(self):
        if(self.file_img_path is not None):
            img_path = self.file_img_path       
            mPATH = Path(img_path)
            img_name = mPATH.name
            img_name_without_ext = mPATH.stem
            img_dir = mPATH.parent
            output_dir = Path(img_dir) / Path(img_name_without_ext)
            QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))



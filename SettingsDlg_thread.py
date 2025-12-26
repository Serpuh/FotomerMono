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

#from moge.model/v2 import MoGeModel if False else None  # placeholder to avoid import-time errors in this snippet
from moge.model.v2 import MoGeModel
from moge.utils.io import save_glb, save_ply
from moge.utils.vis import colorize_depth, colorize_normal

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QUrl, QRegularExpression, QTimer, Signal, QObject, QThread, Slot
from PySide6.QtGui import QDesktopServices, QDoubleValidator, QRegularExpressionValidator, QTextCursor

from ui_SettingsDlg import Ui_SettingsDlg

from ui_form import Ui_MainWindow

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


class CalcWorker(QObject):
    # Signals to communicate with the main (GUI) thread
    progress = Signal(str)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, img_path: str, use_gpu: bool, max_depth_m: float, model_quality: int, project_root: Path):
        super().__init__()
        self.img_path = img_path
        self.use_gpu = use_gpu
        self.max_depth_m = max_depth_m
        self.model_quality = model_quality
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
                max_depth_m=self.max_depth_m
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
            try:
                self.ui.text1.append("gpu available\n")
            except AttributeError:
                self.ui.text1.appendPlainText("gpu available\n")
        else:
           self.ui.gpuComboBox.setCurrentIndex(1)
           self.ui.gpuComboBox.setEnabled(False)
           try:
               self.ui.text1.append("gpu not available\n")
           except AttributeError:
               self.ui.text1.appendPlainText("gpu not available\n")

        self.ui.qualityComboBox.addItem("small")
        self.ui.qualityComboBox.addItem("middle")
        self.ui.qualityComboBox.addItem("best")
        self.ui.qualityComboBox.setCurrentIndex(1)


        self.fov_x=None
        self.max_depth_m = 100
        self.ui.max_depth_m.setText(f"{self.max_depth_m:.1f}")

        validator = QDoubleValidator()
        validator.setRange(0.1, 120.0, 2)
        self.ui.fov_x.setValidator(validator)
        self.ui.max_depth_m.setValidator(validator)
        hh=10

        # keep refs to worker/thread so they don't get GC'd
        self._worker = None
        self._thread = None

    def show(self):
        if(self.file_img_path == None):
            self.ui.calcButton.setEnabled(False)
        else:
            self.ui.calcButton.setEnabled(True)

        if(self.fov_x == None):
            self.ui.fov_x.setEnabled(False)
        else:
            self.ui.fov_x.setEnabled(True)

        super().show()
        self.after_show()

    def after_show(self):
        hh=10

    def updateText(self):
        self.ui.text1.update()

    def _append_text(self, text: str):
        """Append text to the text widget in a safe way (handles QTextEdit vs QPlainTextEdit)."""
        try:
            self.ui.text1.append(text)
        except Exception:
            try:
                self.ui.text1.appendPlainText(text)
            except Exception:
                # as a fallback, setPlainText (not ideal because it replaces content)
                self.ui.text1.setPlainText(text)

    def OnButtonCalc(self):
        # Prevent double clicks
        self.ui.calcButton.setEnabled(False)
        self._append_text("Starting background calculation...")

        # Read UI choices
        img_path = self.file_img_path
        if not img_path:
            self._append_text("No image selected.")
            self.ui.calcButton.setEnabled(True)
            return

        use_gpu = (self.ui.gpuComboBox.currentText() == "gpu")
        try:
            max_depth = float(self.ui.max_depth_m.text())
        except Exception:
            max_depth = self.max_depth_m

        # model quality mapping (original code used 0 default)
        model_quality = 0

        # Create worker and thread
        worker = CalcWorker(img_path=img_path, use_gpu=use_gpu, max_depth_m=max_depth, model_quality=model_quality, project_root=project_root)
        thread = QThread()
        worker.moveToThread(thread)

        # Connect signals
        worker.progress.connect(self._append_text)
        worker.finished.connect(self._on_worker_finished)
        worker.error.connect(self._on_worker_error)
        thread.started.connect(worker.run)

        # cleanup when thread finishes (worker.finished handler will stop thread)
        # Keep references so they aren't garbage-collected
        self._worker = worker
        self._thread = thread

        thread.start()

    @Slot(dict)
    def _on_worker_finished(self, result: dict):
        # Called in UI thread
        self._append_text("Worker finished.")
        focal_X = result.get("focal_X", 0.0)
        output_dir = result.get("output_dir", "")
        depth_png = result.get("depth_png", "")
        depth_exr = result.get("depth_exr", "")
        ply = result.get("ply", "")
        # update UI fields
        self.fov_x = focal_X
        try:
            self.ui.fov_x.setText(f"{self.fov_x:.1f}")
        except Exception:
            pass

        # Add images to main window views if available
        try:
            # convert to Path to match original usage
            if depth_png:
                self.Ui_MainWindow.gView2.addImage(str(depth_png))
            if depth_exr:
                # gView2 and gView1 expect (path, focal_X)
                self.Ui_MainWindow.gView2.addEXR(str(depth_exr), focal_X)
                self.Ui_MainWindow.gView1.addEXR(str(depth_exr), focal_X)
        except Exception as e:
            self._append_text(f"Error updating main window views: {e}")

        # stop and clean thread
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait(2000)
            self._thread = None
            self._worker = None

        self.ui.calcButton.setEnabled(True)

    @Slot(str)
    def _on_worker_error(self, errmsg: str):
        self._append_text(errmsg)
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait(2000)
            self._thread = None
            self._worker = None
        self.ui.calcButton.setEnabled(True)

    def OnFolderOpen(self):
        img_path = self.file_img_path
        if not img_path:
            return
        mPATH = Path(img_path)
        img_name = mPATH.name
        img_name_without_ext = mPATH.stem
        img_dir = mPATH.parent
        output_dir = Path(img_dir) / Path(img_name_without_ext)
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))
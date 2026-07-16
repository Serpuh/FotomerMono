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

start = time.time()

dirPath = r"C:\LoungeRGBDImages\image100"
output_dir = r"C:\LoungeRGBDImages\depth100my"

if not os.path.exists(output_dir):
            os.mkdir(output_dir)

png_files = sorted(Path(dirPath).glob("*.[pP][nN][gG]"), key=lambda x: x.name)

device_name = "gpu"
if(device_name=="gpu"):
    device = torch.device("cuda")
    b_use_fp16 = True
    print("use cuda")
else:
    device = torch.device("cpu")
    b_use_fp16 = False
    print("use cpu")

dirPath = r"C:\MoGe\MoGe"
modelPath = dirPath / Path("Models") / Path("model_best.pt")

model = MoGeModel.from_pretrained(modelPath).to(device)
        
end = time.time()
print(f"Model loaded: {end - start:.2f} sec")

fov_x = 62.
max_depth_m = 20.
metric_scale_mnoj=1.

for png in png_files:
    start1 = time.time()
    input_image = cv2.cvtColor(cv2.imread(png), cv2.COLOR_BGR2RGB) 
    input_image_t = torch.tensor(input_image / 255, dtype=torch.float32, device=device).permute(2, 0, 1)    
    output = model.infer(
                input_image_t,
                num_tokens=None,
                resolution_level=9,
                force_projection=True,
                apply_mask=True,
                fov_x=fov_x,                
                use_fp16=b_use_fp16, # True-Gpu, False-CPU
                max_depth_m=max_depth_m,
                metric_scale_mnoj = metric_scale_mnoj)

    points, depth, mask, intrinsics, focal_X, fx, fy  = output['points'].cpu().numpy(), output['depth'].cpu().numpy(), output['mask'].cpu().numpy(), output['intrinsics'].cpu().numpy(),  output['focal'].cpu().numpy(),  output['fx'].cpu().numpy(),  output['fy'].cpu().numpy()

    mPATH = Path(png)
    img_name = mPATH.name    
    output_png = Path(output_dir) / Path(img_name)

    # FOR REAL SENSE FORMAT
    depth_mm = (depth * 1000).astype(np.uint16)  # Convert meters to mm, uint16
    cv2.imwrite(output_png, depth_mm)  # PNG preserves uint16

    end1 = time.time()
    print(f"Infer time: {end1 - start1:.2f} sec {png}")

end = time.time()
print(f"All time: {end - start:.2f} sec")

h=0


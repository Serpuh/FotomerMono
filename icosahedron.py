import sys
import torch
import os
import re

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

from moge.utils.panorama import spherical_uv_to_directions, get_panorama_cameras, split_panorama_image, merge_panorama_depth

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
import cv2

def natural_sort_key(path):
    return [int(text) if text.isdigit() else text.lower() 
            for text in re.split('([0-9]+)', str(path))]



def find_duplicates(lst):
    seen = set()
    duplicates = set()
    for item in lst:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)

start = time.time()

dirPath = r"C:\360\5"
output_dir = r"C:\360\5\ICO"

if not os.path.exists(output_dir): os.mkdir(output_dir)
            
if not os.path.exists(output_dir+r"\0"):os.mkdir(output_dir+r"\0")
if not os.path.exists(output_dir+r"\1"):os.mkdir(output_dir+r"\1")
if not os.path.exists(output_dir+r"\2"):os.mkdir(output_dir+r"\2")        
if not os.path.exists(output_dir+r"\3"):os.mkdir(output_dir+r"\3")
if not os.path.exists(output_dir+r"\4"):os.mkdir(output_dir+r"\4")
if not os.path.exists(output_dir+r"\5"):os.mkdir(output_dir+r"\5")
if not os.path.exists(output_dir+r"\6"):os.mkdir(output_dir+r"\6")
if not os.path.exists(output_dir+r"\7"):os.mkdir(output_dir+r"\7")
if not os.path.exists(output_dir+r"\8"):os.mkdir(output_dir+r"\8")
if not os.path.exists(output_dir+r"\9"):os.mkdir(output_dir+r"\9")
if not os.path.exists(output_dir+r"\10"):os.mkdir(output_dir+r"\10")
if not os.path.exists(output_dir+r"\11"):os.mkdir(output_dir+r"\11")
#if not os.path.exists(output_dir+r"\12"):os.mkdir(output_dir+r"\12")

jpg_files = sorted(Path(dirPath).glob("*.[jJ][pP][gG]"), key=natural_sort_key)
#jpg_files = sorted(jpg_files, key=natural_sort_key)

splitted_extrinsics, splitted_intriniscs = get_panorama_cameras()
splitted_resolution = 1000
for i, jpg in enumerate(jpg_files):
    print(jpg)
    #image = cv2.cvtColor(cv2.imread(str(jpg)), cv2.COLOR_BGR2RGB)
    image = cv2.imread(str(jpg))
    splitted_images = split_panorama_image(image, splitted_extrinsics, splitted_intriniscs, splitted_resolution)

    mPATH = Path(jpg)
    img_name = mPATH.name    
    output_png = Path(output_dir) / Path(img_name)
        
    for k, split in enumerate(splitted_images):
        path_save = Path(output_dir)/ Path(str(k)) / Path(str(i)+mPATH.suffix)
        cv2.imwrite(path_save,split)   
        



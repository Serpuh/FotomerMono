import os
os.environ['XFORMERS_DISABLED'] = '1'   # Disable xformers
import numpy as np
import torch
from moge.model.v2 import MoGeModel

PRETRAINED_MODEL = r'C:\MoGe\MoGe\Models\moge-2-vits-normal\model_s.pt'
ONNX_FILE = r'C:\MoGe\MoGe\Models\moge-2-vits-normal\moge-2-vits-normal.onnx'


model = MoGeModel.from_pretrained(PRETRAINED_MODEL)
model.onnx_compatible_mode = True  # Enable ONNX compatible mode
"""
torch.onnx.export(
    model, 
    (torch.rand(1, 3, 518, 518), torch.tensor(1800)),
    ONNX_FILE,
    input_names=['image', 'num_tokens'],
    output_names=['points', 'normal', 'mask', 'metric_scale'],
    dynamic_axes={
        'image': {0: 'batch_size', 2: 'height', 3: 'width'},
    },
    opset_version=18
)

"""
class MoGeStatic(MoGeModel):
    def forward(self, image: torch.Tensor):
        return super().forward(image, NUM_TOKENS)

NUM_TOKENS = 1800
FIXED_IMAGE_INPUT = torch.rand(1, 3, 518, 518)

model = MoGeStatic.from_pretrained(PRETRAINED_MODEL)
model.onnx_compatible_mode = True  # Enable ONNX compatible mode

torch.onnx.export(
    model, 
    (FIXED_IMAGE_INPUT,),
    ONNX_FILE,
    input_names=['image'],
    output_names=['points', 'normal', 'mask', 'scale'],
    dynamic_axes=None,
    opset_version=18
)

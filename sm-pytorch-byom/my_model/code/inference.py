import numpy as np
import torch
import os
from six import BytesIO
import json


os.system('pip install --upgrade pip')
os.system('pip3 install opencv-python')
os.system('pip3 install torchvision')



NPY_CONTENT_TYPE = 'application/x-npy'

def _npy_loads(data):
    """
    Deserializes npy-formatted bytes into a numpy array
    """
    stream = BytesIO(data)
    return np.load(stream)

def input_fn(request_body, NPY_CONTENT_TYPE):
    """An input_fn that loads a pickled tensor"""
    if NPY_CONTENT_TYPE == 'application/x-npy':
        data = _npy_loads(request_body)
        img = data * 1.0 / 255
        img = torch.from_numpy(np.transpose(img[:, :, [2, 1, 0]], (2, 0, 1))).float()
        
        return img
    else:
        # Handle other content-types here or raise an Exception
        # if the content type is not supported.
        pass

def predict_fn(input_data, model):
    import torchvision
    
    example_model = torchvision.models.resnet34()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    img_LR = input_data.unsqueeze(0)
    # img_LR = img_LR.to(device)

    example_model.to(device)
    example_model.eval()
    with torch.no_grad():
        out =  example_model(img_LR.to(device))
    return out

def output_fn(prediction, content_type):
    import cv2
    output = prediction.data.squeeze().float().cpu().clamp_(0, 1).numpy()
    # output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
    output = (output * 255.0).round()

    output = cv2.medianBlur(output.astype('uint8'),11)
    res = {'result': output.tolist()}
    content_type = 'application/json'
    return json.dumps(res), content_type

def model_fn(model_dir):
    import torch
    
    print('model_dir:' + str(model_dir))
    print('files:' + str(os.listdir(model_dir)))
    print('dir:' + str(os.getcwd()))
    
    loaded_model = torch.load(model_dir +  '/RRDB_PSNR_x4.pth')
    return loaded_model


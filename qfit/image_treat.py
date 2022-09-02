"""
Image treatment 
- calling affine_transformation_parameters_editor_r.py
- trimming GUI and triming

ref opencv gui
https://rasp.hateblo.jp/entry/2016/01/22/230852
https://www.oit.ac.jp/is/nishiguchi-lab/?OpenCV-Python+%E6%BC%94%E7%BF%92/tutorial_008py

"""

__author__ = "Shinjiro Yagyu"
__license__ = "BSD-3-Clause"
__copyright__ = "National Institute for Materials Science, Japan"
__date__ = "2022/09/02"
__version__= "1.0.0"
__revised__ = "2022/09/02"

from pathlib import Path
import subprocess
from subprocess import PIPE
import time

import cv2
import numpy as np
from PIL import Image
import tifffile as tiff


from qfit import file_folder_trans as fft

editor_path = Path().resolve()
# print(Path().resolve())
# print(list(p.iterdir()))

img_edit_path = str(list(editor_path.glob('*/affine_transformation_parameters_editor_r.py'))[0])


def img_editor_process():
    """ Call affine_transformation_parameters_editor_r.py

    Returns:
        list: output folder list, subproess output string
    """

    command_list = ['python', img_edit_path]
    proc = subprocess.Popen(command_list, stdout=PIPE, stderr=PIPE)

    try:
        outs, errs = proc.communicate(timeout=20000)

    except subprocess.SubprocessError:
        proc.kill()
        outs, errs = proc.communicate()
        
    outstring = outs.decode('utf-8').split('\n')

    # print(outstring)

    output_folder_list = list(editor_path.glob('rot_*'))
    # output_folder_list=1

    return output_folder_list, outstring

def gui2trim(file_name, wh=1100, NX=2368, NY=2240, time_out=120):
    """trim gui + triming Main function
        wrapping pos_est_rect
        
    Args:
        file_name (str or pathlib): file path
        wh (int, optional): triming size. 
            2 inch: wh=1100, 4 inch: wh=2000
            Defaults to 1100.
        NX (int, optional): original size w. Defaults to 2368.
        NY (int, optional): original size h. Defaults to 2240.
        time_out (int, optional): GUI timeout [s]. Defaults to 120. -> 3 min
    
    Returns:
        pathlib : new holder name path
    """

    trim_position = pos_est_rect(file_name, wh, NX, NY, time_out)

    new_folder = folder2trim2tif(file_name, *trim_position)

    return new_folder

def gui2trim2(file_name, wh=1100, NX=2368, NY=2240, time_out=120):
    """trim gui + triming Main function
        wrapping pos_est_rect
        
        The return value is different from gui2trim.
        
    Args:
        file_name (str or pathlib): file path
        wh (int, optional): triming size. 
            2 inch: wh=1100, 4 inch: wh=2000
            Defaults to 1100.
        NX (int, optional): original size w. Defaults to 2368.
        NY (int, optional): original size h. Defaults to 2240.
        time_out (int, optional): GUI timeout [s]. Defaults to 120. -> 3 min
        
    Returns:
        pathlib : new holder name path
        trim_position :tuple
    """

    trim_position = pos_est_rect(file_name, wh, NX, NY, time_out)

    new_folder = folder2trim2tif(file_name, *trim_position)

    return new_folder, trim_position

def pos_est_rect(file_name, wh=1100, NX=2368, NY=2240, time_out=120):
    """trimming position estimation by using opencv GUI

    Args:
        file_name (str):file name or folder. Allowed file types -> .tif, .npy, (.jpeg, .png)
        wh (int, optional): triming size. Defaults to 1100.
                            1 px -> 0.05 mm  2 inch -> 1100
        NX (int, optional): Original width. Defaults to 2368.
        NY (int, optional): Original height. Defaults to 2240.
        time_out (int, optional): time out second. Defaults to 120.

    return:
        int: cord_x, cord_y, wh, wh
    """
    
    start = time.time()
    if type(file_name) == np.ndarray:
        img = file_name

    else:
        fp_name = Path(file_name).resolve()

        if '' in fp_name.suffix :
            try:
                fp_list = list(fp_name.glob('*.tif'))
                img = tiff.imread(str(fp_list[0]))

            except:
                fp_list = list(fp_name.glob('*.npy'))
                cdata = np.fromfile(str(fp_list[0]),dtype=np.float32)
                img = cdata.reshape(NX,NY) 

        elif fp_name.suffix == '.tif':
            img = tiff.imread(file_name)

        elif fp_name.suffix == '.npy':
            cdata = np.fromfile(file_name,dtype=np.float32)
            img = cdata.reshape(NX,NY) 
            
        else:
            img = cv2.imread(str(file_name))
        

    img = img.astype('uint8')
    
    cord_x = 0
    cord_y = 0
    
    def printCoor(event,x,y,flags,param):
        nonlocal img
        nonlocal cord_x, cord_y
        
        if event == cv2.EVENT_LBUTTONDOWN:
            img_tmp = img.copy()
            cv2.rectangle(img_tmp,(x,y),(x+wh,y+wh),(255,255,255), thickness=10)
            cv2.putText(img_tmp, text=f'(x,y):({x},{y})',org=(x, y-20), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=2.0, color=(255,255,255),thickness=3,lineType=cv2.LINE_4)

            print(f'start x:{x}, y:{y} --wh:{wh}-- end x:{x+wh}, y:{y+wh}')

            cv2.imshow('image',img_tmp)
            
            cord_x = x
            cord_y = y
            
        elif event == cv2.EVENT_RBUTTONDOWN:
            cv2.imshow('image',img)
            
    print(img.shape)
    print('Quit -> press "ESC" Key')

    cv2.namedWindow('image',cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('image',printCoor)
    cv2.moveWindow('image', 100,100)
    cv2.putText(img, text=f'Quit -> press "ESC" Key',org=(20,60), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=2.0, color=(255,255,255),thickness=3,lineType=cv2.LINE_4)
    cv2.imshow('image',img)
    
    while True:
        elasped_time = time.time() - start
        # cv2.imshow('image',img)
        # break ESC key
        if cv2.waitKey(20) & 0xFF == 27:
            break
        
        if elasped_time > time_out:
            print('time out')
            break
        
    cv2.destroyAllWindows()
    print(f'final x: {cord_x}, y: {cord_y}')
    
    return cord_x, cord_y, wh, wh


def trim(array, x, y, width, height):
    """
    Function specified by the upper left coordinates and the width / height of the area to be trimmed
    The return value of shap is the order of rows and columns.
    Note that the order is y and x in terms of xy coordinates. The origin is on the upper left.

    Args:
        array (2Dndarray): image data 
        x (int): start x
        y (int): start y
        width (int): width
        height (int): height

    Returns:
        [ndarray]: trim image

    Example:
    im_trim2 = trim(im, 128, 192, 256, 128)
    # (128, 256, 3)

    Ref:
    https://note.nkmk.me/python-numpy-image-processing/

    """
    array_trim = array.copy()
    array_trim = array_trim[y:y + height, x:x+width]

    print(f'Original h(Y), w(X) : {array.shape}')
    print(f'Trimmed h(Y), w(X) :  {array_trim.shape}')

    return array_trim


def folder2trim2tif(filename_or_path, x, y, width, height):
    """fd tif -> triming -> new fd tif

    Args:
        filename_or_path (str): filename_or_path 
        x (int): trim cordinate x (left top)
        y (int): trim cordinate y (left top)
        width (int): trim width
        height (int): trim height

    Returns:
        pathlib : new holder name path
    """
    npy_lists = fft.folder_file_list(filename_or_path)
    new_folder = npy_lists[0].resolve().parents[1]/f'tr_{npy_lists[0].stem[:-2]}'
    new_folder.mkdir(exist_ok=True)

    for fn in npy_lists:
        new_file_name = new_folder/f'tr_{fn.stem}.tif'
        tmp_array = tiff.imread(str(fn))

        tmp_trim= trim(array=tmp_array, x=x, y=y, width=width, height=height)
        tiff.imwrite(str(new_file_name), tmp_trim)
        # Image.fromarray(tmp_trim).save(str(new_file_name))

    return new_folder

# --- Not use ---
def tif2torim(tifname,x, y, width, height):
    """
    Read tif -> trim -> save tif
    2 inch x 2.54 = 50.8 mm
    detector 0.05mm at each size
    about w,h = 1020

    Args:
        tifname (str): tif file name  .tif
        x (int): trim cordinate x (left top)
        y (int): trim cordinate y (left top)
        width (int): width
        height (int): height

    Returns:
       2darray: trimmed 2d-ndarray
    """
    p_tif = Path(tifname)
    img = tiff.imread(str(p_tif))

    trim_array = trim(array=img, x=x, y=y, width=width, height=height)

    # new_file_name = p_tif.parent/f'{p.name[:-6]}_trm_{p.name[-5:]}'
    new_file_name = p_tif
    tiff.imsave(str(new_file_name), trim_array)

    return trim_array


if __name__ == '__main__':
    pass
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument("data", help="data file", type=str)
    # args = parser.parse_args()

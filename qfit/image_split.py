

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

def split_row_col(imagefile, rows, cols, save=False, outpath='out', ext='tif'):
    """
    行数、列数を指定して、分割する場合
    To split by specifying the number of rows and columns

    Args:
        imagefile (str or pathlib): image file path
        rows (int): number of rows
        cols (int): number of cols
        save (bool, optional): save. Defaults to False.
        outpath (str): output folder
        ext (str): output suffix 'tif', 'png', 'jpg' Defaults to 'tif'

    Ref:
        https://pystyle.info/opencv-split-and-concat-images/
        OpenCV – 画像をグリッド上に分割する、複数の画像をグリッド上に結合する方法

    """
    # img = cv2.imread(imagefile)
    img_pil = Image.open(imagefile)
    img = np.array(img_pil)

    chunks = []
    for row_img in np.array_split(img, rows, axis=0):
        for chunk in np.array_split(row_img, cols, axis=1):
            chunks.append(chunk)

    print(f'rows: {rows}, cols: {cols}')
    print(f'lenght: {len(chunks)}')

    if save:
        output_dir = Path(outpath)
        output_dir.mkdir(exist_ok=True)
        for i, chunk in enumerate(chunks):
            save_path = output_dir / f"chunk_{i:02d}.{ext}"
            # cv2.imwrite(str(save_path), chunk)
            chunk_pil = Image.fromarray(chunk)
            chunk_pil.save(str(save_path))

    return chunks, (rows,cols)


def split_size(imagefile, height, width, save=False, outpath='out', ext='tif'):
    """
    To split an image by specifying the image size after splitting
    分割後の画像サイズを指定して分割する場合

    Args:
        imagefile (stror pathlib): file path and  name
        height (int): split image height
        width (int): split image width
        save (bool, optional): save. Defaults to False.
        outpath (str): output folder
        ext (str): output suffix 'tif', 'png', 'jpg' Defaults to 'tif'


    Note:
        分割後の大きさ
        行数 = 画像の高さ / 分割後の画像の高さ
        列数 = 画像の幅 / 分割後の画像の幅

        除算の結果は、端数を切り捨てる場合は numpy.floor()、切り捨てない場合は numpy.ceil()
    """

    # img = cv2.imread(imagefile)
    img_pil = Image.open(imagefile)
    img = np.array(img_pil)

    size = (height, width)  # 分割後の大きさ
    rows = int(np.ceil(img.shape[0] / size[0]))  # 行数
    cols = int(np.ceil(img.shape[1] / size[1]))  # 列数

    chunks = []
    for row_img in np.array_split(img, rows, axis=0):
        for chunk in np.array_split(row_img, cols, axis=1):
            chunks.append(chunk)

    print(f'rows: {rows}, cols: {cols}')
    print(f'lenght: {len(chunks)}')

    if save:
        output_dir = Path(outpath)
        output_dir.mkdir(exist_ok=True)
        for i, chunk in enumerate(chunks):
            save_path = output_dir / f"chunk_{i:02d}.{ext}"
            # cv2.imwrite(str(save_path), chunk)
            chunk_pil = Image.fromarray(chunk)
            chunk_pil.save(str(save_path))


    return chunks, (rows,cols)

def split_average(split_lists, rows, cols):
    """
    Calculate the average value from the split image list.
    分割したイメージリストから平均値を計算

    Args:
        split_lists (list): split image list
        rows (int): number of rows of splits 
        cols (int): number of cols of splits

    Returns:
        ndarray: 2d-ndarray
    
    Note:
        OpenCVで画像サイズの変更をしてみた
        https://qiita.com/kenfukaya/items/dfa548309c301c7087c4
        
    """
    ave_lists = []
    for i in split_lists:
        ave_ = np.nanmean(i)
        ave_lists.append(ave_)

    ave_image = np.array(ave_lists).reshape((rows,cols))

    print(f'shape:{ave_image.shape}')
    print(f'Max:{np.nanmax(ave_image):.2f}, Min:{np.nanmin(ave_image):.2f}')
    print(f'Ave:{np.nanmean(ave_image):.2f}, Median:{np.nanmedian(ave_image):.2f}')

    return ave_image

def image_resize(image,factor): 
    """画像の拡大縮小

    Args:
        image (ndarray): 2d-ndarray image data
        factor (float): magnified factor

    Returns:
        [ndarray]: 2d-ndarray image
    """
    h,w = image.shape
    print(f'Original shape: height: {h}, width: {w}')
    tmp_image= cv2.resize(image , (int(w*factor), int(h*factor)))
    hn,wn = tmp_image.shape
    print(f'Resize shape: height: {hn}, width: {wn}')
    
    return tmp_image
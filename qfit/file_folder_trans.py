"""
file converter
npy to tif, tif to npy

All File transfer format is tif
.npy -> fd.tif
fd.tif -> .npy
fd.tif -> new fd.tif

Memo
rot (image rotation):affin transform GUI
rc : fit.py
q :q2.py
T, T2 :file converter
fd:folder

method A (rc2rot): 
RC(.tif->.npy) -> T(.npy->fd.tif) -> trimming(fd.tif->new fd.tif)
-> image rotaion(fd.tif->new fd.tif) -> T2(fd.tif->.npy) 
-> q(.npy->.npy)-> T(.npy->fd.tif)

method B (rot2rc): 
image rotation(fd.tif-> new fd.tif) -> RC(fd.tif->.npy) 
-> T(.npy->fd.tif) -> trimming(fd.tif->new fd.tif) 
-> T2(fd.tif->.npy) -> q(.npy->.npy)-> T(.npy->fd.tif)
 
"""

__author__ = "Shinjiro Yagyu"
__license__ = "BSD-3-Clause"
__copyright__ = "National Institute for Materials Science, Japan"
__date__ = "2022/09/02"
__version__= "1.0.0"
__revised__ = "2022/09/02"


from pathlib import Path
import shutil

import numpy as np
from PIL import Image
import tifffile as tiff


def npy2folder(npy_file_name, NX=2368, NY=2240, tif_save=True):
    """move npy file to new dir and make tif file

    Args:
        npy_file_name (str): npy_file_name, ex hw_21000_c.npy
        NX (int): NX
        NY (int): NY
        tif_save (bool): save tif file default True

    Returns:
        pathlib: new folder path
    """
    p_npy = Path(npy_file_name).resolve()

    # if '_c.' in p_npy.name or '_h.' in p_npy.name or '_w.' in p_npy.name :
    #     # print('rc file')
    #     remove = -2

    # elif  '_x.' in p_npy.name or '_y.' in p_npy.name or '_z.' in p_npy.name :
    #     # print('q file')  
    #     remove = -3

    # else:
    #     print('Check file')
    #     remove = -2

    remove = -2
    p_dir = p_npy.parent/p_npy.stem[:remove]
    p_dir.mkdir(exist_ok=True)
  
    p_tmp = list(p_npy.parent.glob(f"{p_npy.stem[:remove]}*.*"))

    # print(p_npy)
    # print(p_dir)
    # print(p_tmp)

    # move file
    for source in p_tmp:
        shutil.move(str(source), str(p_dir))

    if tif_save:
        f_tmp = list(p_dir.glob(f"{p_npy.stem[:remove]}*.npy"))
        for fi in f_tmp:
            tif_name = p_dir / f'{fi.stem}.tif'
            np_tmp = np.fromfile(str(fi),dtype=np.float32)
            npres_temp = np_tmp.reshape(NX,NY)
            tiff.imwrite(str(tif_name), npres_temp, compression=None)
            # Image.fromarray(npres_temp).save(str(tif_name))
      
    return p_dir


def folder_file_list(filename_or_path,look_for='tif'):
    """ file list

    Args:
        filename_or_path (str or pathlib): file name with relative path or file folder
        example: 'hw_211116_135415' or ./hw_211116_135415/hw_211116_135415_c.npy

        look_for (str, optional): look for files. 'tif' or 'npy', Defaults to 'tif'.

    Returns:
        [list]: pathlib list
    """

    
    f_path = Path(filename_or_path).resolve()
    # print(npy_path)
    
    if look_for == 'tif':

        if '' in f_path.suffix:
            f_list = list(f_path.glob(f'*.tif'))
        
        elif f_path.suffix == '.tif' or f_path.suffix == '.npy':
            f_list = list(f_path.parent.glob(f'{f_path.stem[:-2]}*.tif'))

    elif look_for == 'npy':

        if '' in f_path.suffix:
            f_list = list(f_path.glob(f'*.npy'))

        elif f_path.suffix == '.npy' or f_path.suffix == '.tif':
            f_list = list(f_path.parent.glob(f'{f_path.stem[:-2]}*.npy'))


    return f_list


def fd_tif2fd_npy(file_dir):
    """.tif  to .npy

    Args:
        file_dir (str):  folder name included tif files
    
    Exampel:

        file_dir='./hw_211116_135415'

    """
    p = Path(file_dir)
    p_list = list(p.glob('*.tif'))
    for i in p_list:
        np_name =  i.parent/f'{i.stem}.npy'
        # print(np_name)
        I = tiff.imread(str(i))
        I.tofile(np_name)
        # I = Image.open(str(i))
        # data = np.array(I)
        # data.tofile(np_name)
        
def conv_tif2npy(file_dir):
    """tif files in the file directory convert to npy files

    Args:
        file_dir (str): folder name include tif files

    Returns:
        list: npy file list
    """
    
    fd_tif2fd_npy(file_dir)
    npy_list = folder_file_list(file_dir,look_for='npy')
    
    print(f'npy list:{npy_list}')
    
    return npy_list
    
    

if __name__ == '__main__':
    pass

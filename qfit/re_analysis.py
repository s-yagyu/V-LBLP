"""
re-analsys tools
    Data load (rc,q)
    converting x,y to polar codinates(r,theta)

"""

__author__ = "Shinjiro Yagyu"
__license__ = "BSD-3-Clause"
__copyright__ = "National Institute for Materials Science, Japan"
__date__ = "2022/09/02"
__version__= "2.0.0"
__revised__ = "2023/02/02"

from pathlib import Path

import numpy as np
from PIL import Image
import tifffile as tiff

from qfit import file_folder_trans as fft


def load_rc_tif(file_path):
    """load rc  tif data
    
    Args:
        file_path (str):  Name of the folder where .npy and .tif files are stored.
        In Load, only Tif files are used.

    Returns:
        dict:  {'c':peak[arcsec], 'h':height, 'w':width[arcsec], 'ct':peak-ave[deg], 'ht':normalize, 'wt':width[deg]}
        
    Note:
    FWHM = 2 * root(2*ln(2))* sigma(gauss) ~2.35*sigma
    HWFACTOR = 2 * np.sqrt(2 * np.log(2))
    
    Method hw (width) -> FWHM / HWFACTOR (~=sigma) 
    method gauss (width) -> sigma
    """
   
    file_lists = fft.folder_file_list(file_path)

    # print(file_lists)
    # convert arcsec to deg
    arcsec2deg = (1/3600)
    # sigma to FWHM
    HWFACTOR = 2 * np.sqrt(2 * np.log(2))
    
    for fn in file_lists:

        tmp_array = tiff.imread(str(fn))
        tmp_ave = np.mean(tmp_array[~np.isnan(tmp_array)])

        if '_c.' in fn.name:
            # print(fn.name)
            c_data = tmp_array
            c_tra = (c_data - tmp_ave) * arcsec2deg 

        elif '_h.' in fn.name:
            # print(fn.name)
            h_data = tmp_array
            h_tra = (h_data - tmp_ave)/tmp_ave
            
        elif '_w.' in fn.name :
            # print(fn.name)
            w_data = tmp_array*HWFACTOR
            w_tra = np.abs(w_data * arcsec2deg)


    return {'c':c_data, 'h':h_data, 'w':w_data, 'ct':c_tra, 'ht':h_tra, 'wt':w_tra }


def load_q_tif(file_path):
    """load q tif data

    Args:
        file_path (str): folder name containg q tif data

    Returns:
        dict : {'x':qx, 'y':qy, 'z':qz, 'xy':qxy, 'ang':q_ang, 'angxy':q_angxy, 'r':q_r}
        
        q_ang:polar codinate angle between Z and r  -> theta
        q_angxy: polar codinate angle between x and y -> phi

    Note:
        np.arctan(y/x): returns(rad)-> -pi/2 to pi/2 
        np.arctan2(y, x): returns(rad)-> -pi to pi
        This angle is the angle between the vector from the origin to the coordinates (x, y) 
        and the positive direction of the x-axis in the polar coordinate plane (declination).
    
    """
       
    file_lists = fft.folder_file_list(file_path)

    for fn in file_lists:
        tmp_array = tiff.imread(str(fn))
        # print(fn.name)
    
        if '_x.' in fn.name:
            qx = tmp_array

        elif '_y.' in fn.name:
            qy = tmp_array
            
        elif '_z.' in fn.name :
            qz = tmp_array

        else:
            pass

    qxy = np.hypot(qx, qy)
    q_ang = np.rad2deg(np.arctan(qxy/qz))
    # q_ang = np.rad2deg(np.arctan2(qxy,qz))
    q_angxy = np.rad2deg(np.arctan2(qy,qx))
    q_r = np.sqrt(qx**2 + qy**2+ qz**2)

    return {'x':qx, 'y':qy, 'z':qz, 'xy':qxy, 'ang':q_ang, 'angxy':q_angxy, 'r':q_r}

def average_3q(q0p,q0m,qpm):
    """ Average of 3q

    Args:
        q0p (dict): load q data
        q0m (dict): load q data
        qpm (dict): load q data

    Returns:
        dict: {'x':qtx, 'y':qty, 'z':qtz, 'xy':qtxy, 'ang':qt_ang, 'angxy':qt_angxy, 'r':qt_r}
    """
    
    qtx = (q0p['x'] + q0m['x'] + qpm['x'])/3
    qty = (q0p['y'] + q0m['y'] + qpm['y'])/3
    qtz = (q0p['z'] + q0m['z'] + qpm['z'])/3
    
    qtxy = np.hypot(qtx, qty)
    qt_ang = np.rad2deg(np.arctan(qtxy/qtz))
    qt_angxy = np.rad2deg(np.arctan2(qty,qtx))
    qt_r = np.sqrt(qtx**2 + qty**2+ qtz**2)
    
    return {'x':qtx, 'y':qty, 'z':qtz, 'xy':qtxy, 'ang':qt_ang, 'angxy':qt_angxy, 'r':qt_r}

def difference_2q(qaf,qbf,flag='minus'):
    """ difference of q calculations

    Args:
        qbf  (dict): load q data
        qaf  (dict): load q data
        flag (str, optional):'minus'=qaf-qdf, 'div'=qbf/qaf, 'ave'=(qaf+qdf)/2.
            Defaults to 'minus'.

    Returns:
        dict: {'x':qtx, 'y':qty, 'z':qtz, 'xy':qtxy, 'ang':qt_ang, 'angxy':qt_angxy, 'r':qt_r}

    Examples:
        qd = difference_2q(qbf=q_bs,qaf=q_epi,flag='minus')
        
    """

    if flag== 'minus':
        qtx = qaf['x'] -qbf['x']
        qty = qaf['y'] -qbf['y']
        qtz = qaf['z'] -qbf['z']

        qtxy = np.hypot(qtx, qty)
        qt_ang = np.rad2deg(np.arctan(qtxy/qtz))
        qt_angxy = np.rad2deg(np.arctan2(qty,qtx))
        qt_r = np.sqrt(qtx**2 + qty**2+ qtz**2)


    elif flag== 'div':
        qtx = qbf['x'] /qaf['x']
        qty = qbf['y'] /qaf['y']
        qtz = qbf['z'] /qaf['z']

        qtxy = np.hypot(qtx, qty)
        qt_ang = np.rad2deg(np.arctan(qtxy/qtz))
        qt_angxy = np.rad2deg(np.arctan2(qty,qtx))
        qt_r = np.sqrt(qtx**2 + qty**2+ qtz**2)
    
    elif flag == 'ave':
        qtx = (qaf['x'] + qbf['x'])/2
        qty = (qaf['y'] + qbf['y'])/2
        qtz = (qaf['z'] + qbf['z'])/2

        qtxy = np.hypot(qtx, qty)
        qt_ang = np.rad2deg(np.arctan(qtxy/qtz))
        qt_angxy = np.rad2deg(np.arctan2(qty,qtx))
        qt_r = np.sqrt(qtx**2 + qty**2+ qtz**2)

    return {'x':qtx, 'y':qty, 'z':qtz, 'xy':qtxy, 'ang':qt_ang, 'angxy':qt_angxy, 'r':qt_r}

# --develop version
# corrilation

import numpy.ma as ma

def nan_corr(q1,q2):
    """ Corrlation with nan

    Args:
        q1 (ndarray): q before data
        q2 (ndarray): q after data

    Returns:
        masked_array: 

    Examples:
        q1=q_bs['qx']
        q2=q_epi['qx']  
        corrd = nan_corr(q1,q2)
        
    corrd= masked_array(
            data=[[1.0, 0.9986379453775506],
                [0.9986379453775506, 1.0]],
            mask=[[False, False],
                [False, False]],
            fill_value=1e+20)

    print(corrd.data)       
    """
    a = ma.masked_invalid(q1)
    b = ma.masked_invalid(q2)

    msk = (~a.mask & ~b.mask)
    corr = ma.corrcoef(a[msk],b[msk])
    print(corr)
    
    return corr


# --- cos and polar calculation ---

def cosxy(qx,qy):
    """qx ,qy convert cos values

    Args:
        qx (2d-ndarray): qx
        qy (2d-ndarray): qy

    Returns:
        dict[2d-ndarray]: {'qxsg':qcxsig, 'qysg':qcysig, 'qcx':qcx, 'qcy':qcy, 'qc0':qs0}
    
    Example:
        qcos=polar_conv(q_0m120['x'],q_0m120['y']) 
        
    """
    qcx = qx.copy()
    qcy = qy.copy()
    q_r, q_t = getRD(x=qcx, y=qcy, out_deg_or_rad='rad')
    q_ri, q_ti = getRD(y=qcx, x=qcy, out_deg_or_rad='rad')
    qcx=np.cos(q_t)
    qcy=np.cos(q_ti)
    qcxsig = np.sign(qcx)
    qcysig = np.sign(qcy)
    qs0=np.zeros(qcx.shape)
    
    return {'qxsg':qcxsig, 'qysg':qcysig, 'qcx':qcx, 'qcy':qcy, 'qc0':qs0}

def getRD(x, y, out_deg_or_rad='rad'):
    """Converting x,y to polar coordinates

    Args:
        x (ndarray): 2d-ndarray
        y (ndarray): 2d-ndarray
        out_deg_or_rad (str, optional): output angel unit.'rad' or 'deg' Defaults to 'rad'.

    Returns:
        radii, theta
        radii(ndarray): r
        theta(ndarray): angle. value depend on out_deg_or_rad
    
    Note:
        ref: https://qiita.com/osakasho/items/1647518c6c4b97651810
        
    """
 
    radii = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y,x)
    if out_deg_or_rad == 'deg':
        theta = np.rad2deg(theta)
            
    return radii, theta


def _inner_cos(u: np.ndarray, v: np.ndarray):
    """COS calculation

    Args:
        u (np.ndarray): unit vector. np.array([1, 0]) or np.array([0, 1])
        v (np.ndarray): data

    Returns:
        [type]: [description]
        
    Example:
        # xx, yy : 2d-ndarray data such as image data
        uu = np.array([1, 0]) # unit vector
        shape_ = xx.shape 
        cos_list = []
        for i,j in zip(xx.flatten(),yy.flatten()):
            vv = np.array([i,j])
            cos_temp =_inner_cos(uu,vv)
            cos_list.append(cos_temp)
        cos_arr=np.array(cos_list).reshape(shape_)
    
    Note:
        https://www.mathpython.com/ja/numpy-vector-angle/
        https://python.atelierkobato.com/inner/

    """
    
    # inner product
    # i = np.inner(u, v)
    i = np.vdot(u,v)
    # vector length
    s = np.linalg.norm(u)
    t = np.linalg.norm(v)
    cos_t = i/(s*t)
    # theta = np.arccos(i/(s*t))
    # if deg_or_rad == 'deg':
    #    theta = np.rad2deg(theta)
        
    return cos_t

def d2_inner_product(qx,qy,u_angd=(0,90)):
    """2D cos values
    Args:
        qx (ndarray): 2D ndarray
        qy (ndarray): 2D ndarray
        u_angd (tuple, optional): unit vector angle [deg]. Defaults to (0,90).
                (0,90)
                ux = np.array([1,0])
                ux = np.array([0,1])
                (120,-120)
                r3 = np.sqrt(3)
                ux = np.array([-0.5,r3/2])
                uy = np.array([-0.5,-r3/2])

    Returns:
        qux: 2D ndarray cos values 
        quy: 2D ndarray cos values 
        
    Note: 
        cos -> 1 same direction, -> -1 opposit direction, -> 0 no compornet
        
    """       
    ux = np.array([np.cos(np.deg2rad(u_angd[0])),np.sin(np.deg2rad(u_angd[0]))])
    uy = np.array([np.cos(np.deg2rad(u_angd[1])),np.sin(np.deg2rad(u_angd[1]))])

    shape_ = qx.shape

    ux_cos = []
    uy_cos = []
    for i,j in zip(qx.flatten(),qy.flatten()):
        v = np.array([i,j])
        ux_cos_t = _inner_cos(ux,v)
        uy_cos_t = _inner_cos(uy,v)
        
        ux_cos.append(ux_cos_t)
        uy_cos.append(uy_cos_t)
    
    qux = np.array(ux_cos).reshape(shape_)
    quy = np.array(uy_cos).reshape(shape_)
    
    return qux, quy

@np.vectorize
def curvature_ang(ang,r,printf=True):
    """calculate curvature radius
    
    curvature radius : R [m]
    tilting angle : Dq [deg]
    sample radius: r [m]

    d = r*arctan(Dq)
    
    R = (r^2+d^2)/2d

    Args:
        ang (float): tilting angle [deg]
        r (float): sample radius [m]

    Returns:
        R(float), d(float): curvature radius [m], edge distance [m]
        
    example:
        4 inch: 10.16cm --> 0.1016m, 
        4 inch radius: 0.0508m
        tilting angle 0.03 deg
        
        >>> r, d = curvature_ang(ang=0.03,r=0.0508)
        >>> r = 48 
            curveture  48m

        2inch: radius 0.0254m
        tilting angle 0.01 deg 
        
        >>> r, d = curvature_ang(ang=0.01,r=0.0254)
        >>> r = 72 
            curveture --> 72m

    """

    d = r * np.tan(np.deg2rad(ang))
    R = (r**2 + d**2)/(2*d)
    if printf:
        print(f'curvature:{R:.2f} [m], edge distance:{d:.2e} [m]')

    return R, d

@np.vectorize
def curvature_d(d,r,printf=True):
    """calculate curvature radius and angle
    
    Args:
        d (float): edge distance [m]
        r (float): sample radius [m]

    Returns:
        R(float), thi(float): curvature radius [m], tilting angle [deg]
    
    Example:
        curvature_d(0.2e-3,100e-3)
    """
    
    R = (r**2 + d**2)/(2*d)
    thi =np.rad2deg(np.arctan(d/r))
    if printf:
        print(f'curvature:{R:.2f} [m], tilting angle:{r:.3f} [deg]')
    return R, thi

# --- data statics infos ---
def static_info(qx,qy,qz):
    """ static infomation
        nan values are skipped
        
    Args:
        qx (float): ndarray
        qy (float): ndarray
        qz (float): ndarray
    
    """
    q_list = [qx,qy,qz]
    for i in q_list:
        qav = np.nanmean(i)
        qmax = np.nanmax(i)
        qmin = np.nanmin(i)
        qstd = np.nanstd(i)
        print(f'ave:{qav}, max:{qmax}, min:{qmin}, std:{qstd}')
        

# --- data rotation ---
def flipxy(data,flip='xy'):
    """image flip
       
    Args:
        data (ndarray): image data
        flip (str, optional):   x left-right
                                y up-down
                                xy both. 180 rotation
                                Defaults to 'xy'.
    Returns:
        data_flip(ndarray): fliped ndarray (new object)
    
    Note:
        ref: https://note.nkmk.me/python-numpy-flip-flipud-fliplr/
        
    """

    if flip == 'x':
        data_flip = np.fliplr(data).copy()
    elif flip == 'y':
        data_flip = np.flipud(data).copy()
    elif flip == 'xy':
        data_flip = np.flip(data).copy()

    return data_flip

def cc2pc3(x, y, z, out_deg_or_rad='rad'):
    """ 3d Cartesian coordinates (x, y, z) convert to polar coordinates

    Args:
        x (ndarray): 2d-ndarray
        y (ndarray): 2d-ndarray
        z (ndarray): 2d-ndarray
        out_deg_or_rad (str, optional): output angel unit.'rad' or 'deg' Defaults to 'rad'.

    Returns:
        
        r3d(ndarray): r. length
        theta(ndarray): angle. value depend on out_deg_or_rad. z-xy 
        fai(ndarray): angle. value depend on out_deg_or_rad. x-y
    
    Note:
        ref: https://qiita.com/osakasho/items/1647518c6c4b97651810
    """
 
    r3d = np.sqrt(x**2 + y**2 + z**2)
    fai = np.arctan2(y,x) #x-y 
    theta = np.arccos(z/r3d) #z-xy 
    if out_deg_or_rad == 'deg':
        theta = np.rad2deg(theta)
        fai = np.rad2deg(fai)
        
    return r3d, theta, fai

def pc2cc3(r3, theta3, phi3, input_deg_or_rad='rad'):
    """3d polar codinates convert to x, y, z

    Args:
        r3(ndarray): r. length
        theta3(ndarray): angle. value depend on out_deg_or_rad. z-xy 
        phi3(ndarray): angle. value depend on out_deg_or_rad. x-y
        input_deg_or_rad (str, optional): input angel unit.'rad' or 'deg' Defaults to 'rad'.

    Returns:
        x (ndarray): 2d-ndarray
        y (ndarray): 2d-ndarray
        z (ndarray): 2d-ndarray
    Note:
        ref: https://qiita.com/osakasho/items/1647518c6c4b97651810
    """
    if input_deg_or_rad == 'deg':
        theta3 = np.deg2rad(theta3)
        phi3 = np.deg2rad(phi3)
    xx = r3*np.sin(theta3)*np.cos(phi3)
    yy = r3*np.sin(theta3)*np.sin(phi3)
    zz = r3*np.cos(theta3)

    return xx, yy, zz
    
# def get3RD(x, y, z, out_deg_or_rad='rad'):
#     """ x, y, z convert to polar codinates

#     Args:
#         x (ndarray): 2d-ndarray
#         y (ndarray): 2d-ndarray
#         z (ndarray): 2d-ndarray
#         out_deg_or_rad (str, optional): output angel unit.'rad' or 'deg' Defaults to 'rad'.

#     Returns:
        
#         r3d(ndarray): r. length
#         theta(ndarray): angle. value depend on out_deg_or_rad. z-xy 
#         fai(ndarray): angle. value depend on out_deg_or_rad. x-y
    
#     Note:
#         ref: https://qiita.com/osakasho/items/1647518c6c4b97651810
#     """
 
#     r3d = np.sqrt(x**2 + y**2 + z**2)
#     fai = np.arctan2(y,x) #x-y 
#     theta = np.arccos(z/r3d) #z-xy 
#     if out_deg_or_rad == 'deg':
#         theta = np.rad2deg(theta)
#         fai = np.rad2deg(fai)
        
#     return r3d, theta, fai

 
def getXY(r, angle, deg_or_rad='deg'):
    """
    polar to Euclid codinates
    """   
    if deg_or_rad == 'deg':
        # deg to rad
        angle = np.deg2rad(angle)
        
    x = r * np.cos(angle)
    y = r * np.sin(angle)
    # print(x, y)
    return x, y


def d3_inner_product(qx,qy,qz):
    """
    3D cos values
    Args:
        qx (ndarray): 2D ndarray
        qy (ndarray): 2D ndarray
        qz (ndarray): 2D ndarray
    Returns:
        qux: 2D ndarray cos values 
        quy: 2D ndarray cos values 
        quz: 2D ndarray cos values
    Note: 
        cos -> 1 same direction, -> -1 opposit direction, -> 0 no compornet
    
    """

    ux = np.array([1,0,0])
    uy = np.array([0,1,0])
    uz = np.array([0,0,1])

    shape_ = qx.shape

    ux_cos = []
    uy_cos = []
    uz_cos = []
    for i,j,k in zip(qx.flatten(),qy.flatten(),qz.flatten()):
        v = np.array([i,j,k])
        ux_cos_t = _inner_cos(ux,v)
        uy_cos_t = _inner_cos(uy,v)
        uz_cos_t = _inner_cos(uz,v)
        
        ux_cos.append(ux_cos_t)
        uy_cos.append(uy_cos_t)
        uz_cos.append(uz_cos_t)
    
    qux = np.array(ux_cos).reshape(shape_)
    quy = np.array(uy_cos).reshape(shape_)
    quz = np.array(uz_cos).reshape(shape_)
    
    return qux, quy, quz
  
if __name__ == '__main__':
    pass

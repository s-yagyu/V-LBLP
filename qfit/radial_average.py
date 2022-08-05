"""
Module for determining radial direction average 

"""

from pathlib import Path
from matplotlib import markers

import matplotlib.pyplot as plt

import cv2
import numpy as np
# import pandas as pd
from PIL import Image

from qfit import re_analysis as rean
from qfit import multiplot as mlplt

plt.rcParams["font.size"] = 14
plt.rcParams['font.family']= 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

width_u = 4.8
height_u = 4.5

# save figure parameter
DPI = 300
EXT = 'pdf'
PIX_SIZE = 0.05

# CMAP = "gist_rainbow_r"
# CMAP = "rainbow"
# CMAP ='PRGn'
CMAP="RdBu"

def image2uint8(img_array):
    """ 
    2d-ndarray(2d image) convert to a binary image of type uint8.

    Args:
        img_array (ndarray): data name

    Returns:
        ndarray: binary image of uint8, 
    """

    # print(type(img_array),img_array.dtype)
    img_u8 = img_array.astype(np.uint8) 
    img_b = np.where(img_u8 > 0, 255, 0)
    img_b_u8 = img_b.astype(np.uint8)
    

    return img_b_u8

def read_tif2uint8(file_name):
    """ 
    Reads a tif file and 
    returns a grayscale image of type float and a binary image of type uint8.

    Args:
        file_name (str): file name

    Returns:
        ndarray: binary image of uint8, grayscale image of float
    """
    img_pil = Image.open(file_name)
    img_array = np.array(img_pil)

    # print(type(img_array),img_array.dtype)
    img_u8 = img_array.astype(np.uint8) 
    img_b = np.where(img_u8 > 0, 255, 0)
    img_b_u8 = img_b.astype(np.uint8)

    return img_b_u8, img_array

def find_circle(b_image, area_size=50000):
    """find wafer center and radius

    Args:
        b_image (ndarray): binary ndarray dtype uint8
        area_size (int, optional): select circle filter . Defaults to 50000.
            If it is smaller than this value, it will not be detected.

    Returns:
        (list) : center_lists, radius_lists, area_lists

    """

    # make copy
    imgc = np.copy(b_image)

    th, img_gray = cv2.threshold(imgc, 128, 255, cv2.THRESH_TOZERO)
    contours, hierarchy = cv2.findContours(img_gray,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    # Ignore objects with small area
    contours = list(filter(lambda x: cv2.contourArea(x) > area_size, contours))

    center_lists = []
    radius_lists = []
    area_lists = []
    for i in range(len(contours)):
        contour = contours[i]
        c_area = cv2.contourArea(contour)

        # Draw the minimum circumscribed circle of the contour
        (x, y), radius = cv2.minEnclosingCircle(contour)
        center = (int(x), int(y))
        radius = int(radius)
        print(f'Circle center: {center}, Radius: {radius}, Area: {c_area}')
        cv2.circle(imgc, center, radius, (255, 255, 255), 3, lineType=cv2.LINE_AA)
        cv2.circle(imgc, center, 20, (0, 0, 0), -1 )
        # cv2.drawMarker(imgc,  center, color=(0, 0, 0), markerType=cv2.MARKER_TILTED_CROSS, thickness=20)

        center_lists.append(center)
        radius_lists.append(radius)
        area_lists.append(c_area) 

    # Displays an image with enclosed lines.
    plt.imshow(imgc,cmap =CMAP)

    return center_lists, radius_lists, area_lists

def _make_circle_mask(org_image, center, radius):
    """make circle mask

    Args:
        org_image (ndarray): original image at float
        center (tuple int): (x,y)
        radius (int): [description]

    Returns:
        ndarray: dst, mask_float
        dst: masked image  at dtype float
        mask_float : mask image at dtype float
    """
    
    mask = np.zeros_like(org_image)
    # cv2.circle(img, center, radius, color, thickness=1, lineType=cv2.LINE_8, shift=0)
    # 線の太さは引数thicknessで指定する。単位はピクセル。
    # 長方形や円の場合、-1などの負の値を指定すると内部が塗りつぶされる。
    # この場合円の中が白(255)となりそのほかは0となる
    # cv2.circle(mask, (200, 100), 50, (255, 255, 255), thickness=-1)
    cv2.circle(mask, center, radius, (255, 255, 255), thickness=-1)
    # print(mask.shape, mask.dtype, mask.min(), mask.max())
    # uint8 0,255 
    mask_float = (mask / 255)
    # print(mask_float.shape, mask_float.dtype, mask_float.min(), mask_float.max())
    # float 0.0, 1.0 

    dst = org_image * (mask / 255)
    # print(dst.shape, dst.dtype)
    # print(dst.shape, dst.dtype, np.nanmin(dst),np.nanmax(dst),np.nanmedian(dst),np.nanmean(dst))
    
    return dst, mask_float


def _circle_plots(original_img, dimg_lists, rad_lists, ave_lists, title='Select Imgae', nrows=None, ncols=4, pixel_size=0.05,save=False):
    
    # def zscore(x):
    #     # z-score normalization 
    #     x_mean = np.nanmean(x)
    #     x_std  = np.nanstd(x)
    #     z_score = (x-x_mean)/x_std
    #     return z_score

    def z_predict(orig,target_img):
        orig_mean = np.nanmean(orig)
        orig_std  = np.nanstd(orig)
        z_scale = (target_img-orig_mean)/orig_std
        return z_scale

    if nrows == None:
        nrows = (len(rad_lists) + ncols -1)//ncols

    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*4.8,nrows*3.6), squeeze=False, tight_layout=True)
    

    ax_list=[]    
    for i in range(nrows):
        for j in range(ncols):
            ax_list.append(ax[i,j])

    for  ii, (i_img, i_rad, i_mean) in enumerate(zip(dimg_lists,rad_lists,ave_lists)): 

        if np.nanmax(i_img) < 1:
            i_img = (z_predict(original_img,i_img)*128)+128
            # i_img = (zscore(i_img)*128)+128
        
        ax_list[ii].imshow(i_img.astype(np.uint8),cmap=CMAP)
        
        ax_list[ii].set_title(f'r:{i_rad*pixel_size}, Ave:{i_mean:.1e}' + '$^{\circ}$')
        ax_list[ii].set_ylabel("y (mm)")
        ax_list[ii].set_xlabel("x (mm)")
        x_ticks = ax_list[ii].get_xticks()[1:-1]
        y_ticks = ax_list[ii].get_yticks()[1:-1]
        x_labels = [f'{int(i*pixel_size)}' for i in x_ticks]
        y_labels = [f'{int(i*pixel_size)}' for i in y_ticks]
        
        ax_list[ii].set_xticks(x_ticks)
        ax_list[ii].set_xticklabels(x_labels)
        ax_list[ii].set_yticks(y_ticks)
        ax_list[ii].set_yticklabels(y_labels)

    if len(ax_list) != len(ave_lists):
        for ij in range(len(ax_list)-len(ave_lists)):
            newi= ij + len(ave_lists)
            ax_list[newi].axis("off")


    fig.suptitle(title)
    plt.tight_layout()
    
    if save:
        filename=mlplt.re_replace(title)
        plt.savefig(f'{filename}.{EXT}', dpi=DPI)
        
    plt.show()


def calc_circle_radius_ave(org_image, center, max_radius, dr=100, pixel_size=0.05, 
                           fig_show=True, ylim=(0,0), ylabel='$FWHM_g$ ($^{\circ}$)',
                           title='r $\cdot$ $\Delta r$',save=False):
    """Average in radial direction and in donut-shaped radial direction

    Args:
        org_image (2d-ndarray): Original image FWHM image [deg]
        center (tuple): center cordinate
        max_radius (int): wafer radius
        dr (int, optional): target area pixel. Defaults to 100.
        pixel_size (float, optional): detector pixel size. Defaults to 0.05.
        fig_show (bool, optional): graph and figure. Defaults to True.
        ylim (tuple, optional): y axis limit. The default is (0,0), which means autoscale.
        In case of fwhm, ylim=(0.0035,0.006)

    Returns:
        dict: dsi-> radial average, dri-> donut-shaped radial average
            dsi = {'img': dst_lists, 'r': radius_lists, 'ave': mean_lists, 'sum': sum_lists}
            dri = {'img': dr_lists, 'r': radius_lists, 'ave':  mean_r_lists, 'sum': sum_r_lists}
    """
    
    num = 1 + (max_radius//dr)
    radius_lists =[i*100 for i in range(1,num+1)]

    dst_lists = []
    sum_lists = []
    mean_lists = []
    
    dr_lists = []
    sum_r_lists = []
    mean_r_lists = []
    real_radius_lists = [] #radius_list x pixel size
   
    tmp_maskf = np.zeros_like(org_image)
    
    for ri in radius_lists:

        tmp_dst,tmp_mask = _make_circle_mask(org_image=org_image, center=center ,radius=ri)
        dst_lists.append(tmp_dst)
       
        tmp_maskf = tmp_mask - tmp_maskf
        
        tmp_drc = tmp_dst.copy()
        tmp_dr = tmp_drc*tmp_maskf
        dr_lists.append(tmp_dr)
        
        tmp_maskf = tmp_mask
        
        # tmp_sum = np.nansum(np.abs(tmp_dst*arcsec2deg))
        # tmp_mean =np.nanmean(np.abs(tmp_dst*arcsec2deg))
        dst_nan = np.where(tmp_dst<=0.00001, np.nan, tmp_dst)
        tmp_sum = np.nansum(dst_nan)
        tmp_mean =np.nanmean(dst_nan)
        sum_lists.append(tmp_sum)
        mean_lists.append(tmp_mean)
        
        dr_nan = np.where(tmp_dr<=0.00001, np.nan, tmp_dr)
        tmp_r_sum = np.nansum(dr_nan)
        tmp_r_mean =np.nanmean(dr_nan)
        sum_r_lists.append(tmp_r_sum)
        mean_r_lists.append(tmp_r_mean)
        real_radius_lists.append(ri*pixel_size)
        # print(f'radius:{ri}, SUM:{tmp_sum:.2f}, MEAN:{tmp_mean:.2f}')
        # print(f'radius:{ri}, SUM:{tmp_r_sum:.2f}, MEAN:{tmp_r_mean:.2f}')
        
    if fig_show:
        mean_arr = np.array(mean_lists)
        diff_mean = np.diff(mean_arr, prepend=0)
        fig, (ax1,ax2) =plt.subplots(1, 2, figsize=(2*width_u,1*height_u), tight_layout=True)
        ax1.plot(real_radius_lists, mean_lists,'ro-')
        ax1.set_title('r')
        ax1.set_xlabel('Radius (mm)')
        ax1.set_ylabel(ylabel)
        if ylim != (0,0):
            ax1.set_ylim(ylim)
            ax2.set_ylim(ylim)
        ax1.grid()

        ax2.plot(real_radius_lists, mean_r_lists,'ro-')
        ax2.set_title('$\Delta$r')
        ax2.set_xlabel('Radius (mm)')
        ax2.set_ylabel(ylabel)  
        ax2.grid()
        
        fig.suptitle(title)
        # plt.gray()
        if save:
            filename=mlplt.re_replace(title)
            plt.savefig(f'{filename}.{EXT}', dpi=DPI)
            
        # plt.tight_layout()
        plt.show()

        _circle_plots(org_image, dimg_lists=dst_lists,rad_lists=radius_lists,ave_lists=mean_lists, title='Select r Imgae', nrows=None, ncols=4)
        _circle_plots(org_image, dimg_lists=dr_lists,rad_lists=radius_lists,ave_lists=mean_r_lists, title='Select Δr Imgae', nrows=None, ncols=4)

    dsi = {'img': dst_lists, 'r': real_radius_lists, 'ave': mean_lists, 'sum': sum_lists}
    dri = {'img': dr_lists, 'r': real_radius_lists, 'ave':  mean_r_lists, 'sum': sum_r_lists}

    return dsi, dri

def curvature_plot(dsi,dri,ylim=(0,0),title=''):
    """curvature_plot
        q tilte data

    Args:
        dsi (dict): radial average; calc_circle_radius_ave output 
        dri (dict): donut-shaped radial average; calc_circle_radius_ave output
        ylim (tuple, optional): y axis limit. The default is (0,0), which means autoscale.
        title(str,optinal): figure title.

    Returns:
        tuple: dsi_c_radius, dri_c_radius
    """
    
    dsi_c_radius = rean.curvature_ang(np.array(dsi['ave']),np.array(dsi['r'])/1000,printf=False) # /1000 means 'mm' to 'm'
    dri_c_radius = rean.curvature_ang(np.array(dri['ave']),np.array(dri['r'])/1000,printf=False)
    
    fig, (ax1,ax2) = plt.subplots(1,2,figsize=(8.0, 4.0))
    ax1.plot(dsi['r'], dsi_c_radius[0],'ro-')
    ax1.set_title('r Curvature')
    ax1.set_xlabel('Radius [mm]')
    ax1.set_ylabel('Curvature [m]')

    if ylim != (0,0):
        ax1.set_ylim(ylim)
        ax2.set_ylim(ylim)

    ax1.grid()

    ax2.plot(dri['r'], dri_c_radius[0],'ro-')
    ax2.set_title('Δr Curvature ')
    ax2.set_xlabel('Radius [mm]')
    ax2.set_ylabel('Curvature [m]')
    ax2.grid()
    fig.suptitle(title)
    plt.tight_layout()
    plt.show()
    
    return dsi_c_radius, dri_c_radius

def r_dr_3data_plot(r0_dsi,r0_dri,rp120_dsi,rp120_dri,rm120_dsi,rm120_dri,
                    ylim=(0,0), ylabel='$FWHM_g$ ($^{\circ}$)',
                    title='r $\cdot$ $\Delta r$', pix_size=PIX_SIZE,
                    save=False):
   
    # r and dr plots of 3 directions
    nrow=1
    ncol=2
    fig, (ax1,ax2) =plt.subplots(nrow, ncol, figsize=(ncol*width_u,nrow*height_u), tight_layout=True)
    ax1.plot(np.array(r0_dsi['r']),r0_dsi['ave'],'o-',label='$\psi=0^{\circ}$')
    ax1.plot(np.array(rp120_dsi['r']),rp120_dsi['ave'],'s-',label='$\psi=120^{\circ}$')
    ax1.plot(np.array(rm120_dsi['r']),rm120_dsi['ave'],'^-',label='$\psi=-120^{\circ}$')
    ax1.set_title('r')
    ax1.set_xlabel('Radius (mm)')
    ax1.set_ylabel(ylabel)
    ax1.grid()
    ax1.legend(loc='upper left')
    # ax2.plot(radius_lists,diff_mean)
    # ax2.set_title('Differance Average')
    # ax2.set_xlabel('Radious [pixel]')
    # ax2.set_ylabel('Difference Average')
    ax2.plot(np.array(r0_dri['r']),r0_dri['ave'],'o-',label='$\psi=0^{\circ}$')
    ax2.plot(np.array(rp120_dri['r']),rp120_dri['ave'],'s-',label='$\psi=120^{\circ}$')
    ax2.plot(np.array(rm120_dri['r']),rm120_dri['ave'],'^-',label='$\psi=-120^{\circ}$')
    ax2.set_title('$\Delta r$')
    ax2.set_xlabel('Radius (mm)')
    ax2.set_ylabel(ylabel)
    ax2.grid()
    ax2.legend(loc='upper left',fontsize=14)
    
    if ylim != (0,0):
        ax1.set_ylim(ylim)
        ax2.set_ylim(ylim)

    fig.suptitle(title)
    
    if save:
        filename=mlplt.re_replace(title)
        plt.savefig(f'{filename}.{EXT}', dpi=DPI)
        
    plt.show()
  
if __name__ == '__main__':
    pass

    # example 
    # from qfit import re_analysis as rean

    # file_path ='rot_hw_220111_151046'
    # rc0 = rean.load_rc_tif(file_path)
    # b_h_img = image2uint8(rc0['h'])
    # hc_lists, hr_lists, ha_lists = find_circle(b_image=b_h_img, area_size=4000)
    # dsi, dri = calc_circle_radius_ave(org_image=rc0['wt'], center=hc_lists[0], max_radius=hr_lists[0], 
    #                                     dr=100, pixel_size=0.05, fig_show=True)

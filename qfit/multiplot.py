"""
multiplot module

"""
__author__ = "Shinjiro Yagyu"
__license__ = "BSD-3-Clause"
__copyright__ = "National Institute for Materials Science, Japan"
__date__ = "2022/09/02"
__version__= "2.0.0"
__revised__ = "2023/03/27"

from pathlib import Path
from PIL import Image
import re

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker

import mpl_toolkits.axes_grid1
from mpl_toolkits.mplot3d import Axes3D

from qfit import re_analysis as rean
from qfit import re_plot as replt

# memo figsize=(width,height) wdth:height= 4:3 
# (row,col)->figsize(col*4,row*3): (3,4)->figsize(16,9)

width_u = 5.2
height_u = 4

# Detector pixcel size
PIX_SIZE = 0.05

# save figure parameter
DPI = 300
EXT = 'png' # png, jpg, pdf

# plt.rcParams["font.size"] = 14
plt.rcParams['font.family']= 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

def re_replace(text):
    """Remove special symbols with regular expressions 

    Args:
        text (str): text
    Returns:
        str: Text with special symbols removed
    Examples:
        text = '4 inch $\phi$=0'
        re_replace(text)
        >>> '4_inch_phi0
    Ref:
        https://qiita.com/ganyariya/items/42fc0ed3dcebecb6b117 
    """
    # code_regex = re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％]')

    code_regex = re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~]')
    cleaned_text = code_regex.sub('', text).replace(' ', '_')
    # print(cleaned_text)

    return cleaned_text


# --- RC plot -----

def rc_12plots(read_rc_data, data_range=None, peak_range =(0,0),width_range =(0,0),height_range =(0,0),
               row_num=None, title='RC12plot', save=False, dpi=DPI, ext=EXT, pixel_size=PIX_SIZE):
    """12 plots for RC

        plots
        (1)c (2)ct, (3)line-ct, (4) hist-ct
        (5)w, (6)wt, (7)line-wt, (8) hist-wt
        (9)h,(10)hist-h, (11)ht, (12) hist-ht
  
    Args:
        read_rc_data (dict): rc load data name
            {'c': peak (arecsec), 'h':height, 'w':width (arcsec), 'ct':peak-ave (deg), 'ht':(height-ave)/ave, 'wt':width (deg) }
        data_range (tuple, optional): (str_x,end_x,str_y,end_y) Defaults to None.
        row_num (int, optional):Cross section position of height. 
                                If None, then position is half size of image height.
                                Defaults to None.
        peak_range(tuple, optional): ct range,(0,0) means autoscale
        width_range(tuple, optional): wt range, (0,0) means autoscale
        height_range(tuple, optional): h range, (0,0) means autoscale
        title (str, optional): figure title name. Defaults to 'RC12plot'.
        save (bool, optional): save image. save name is 'title' name.
        ext (str,optional): save image type suffix. Default to EXT.
        dpi (int, optional): dpi. Default to DPI.
        pixel_size(float, optional): detctor pixel size [mm]. Default to 0.05.
        
    Returns:
        void

    """
    nrow=3
    ncol=4
    fig, ax = plt.subplots(nrow, ncol, figsize=(ncol*width_u,nrow*height_u), squeeze=False, tight_layout=True)
    # fig, ax = plt.subplots(nrow, ncol, figsize=(16,10), squeeze=False, tight_layout=True)

    h, w  = read_rc_data['c'].shape
  
    if row_num == None:
        row_num = h//2
    

    ax_list=[]    
    for i in range(nrow):
        for j in range(ncol):
            ax_list.append(ax[i,j])
    
    ax0, im0, cax0 = replt.plot_imshow_ax(plot_data=read_rc_data['c'], axi=ax_list[0], 
                                        data_range=data_range, v_range=(0,0), title='Peak position (arcsec)',pixel_size=pixel_size)

    ax1, ax2, im1, cax1 = replt.plot_line_ax(plot_data=read_rc_data['ct'], axi=[ax_list[1], ax_list[2]],
                                        data_range=data_range, v_range=peak_range,row_num=row_num, 
                                        title='Peak angle difference (deg)',pixel_size=pixel_size)

    ax3 = replt.plot_hist_ax(plot_data=read_rc_data['ct'], axi=ax_list[3], data_range=data_range, 
                             x_range=peak_range,bins_=100,density=False, xlabel='Peak difference(deg)', quantail=0.9999) 

    ax4, im4, cax4 = replt.plot_imshow_ax(plot_data=read_rc_data['w'], axi=ax_list[4], 
                                    data_range=data_range, v_range=(0,0),title='FWHM (arcsec)', pixel_size=pixel_size)

    ax5, ax6, im5, cax5 = replt.plot_line_ax(plot_data=read_rc_data['wt'], axi=[ax_list[5],ax_list[6]], 
                                    data_range=data_range, v_range=width_range, 
                                    row_num=row_num, title='FWHM (deg)') 

    ax7 = replt.plot_hist_ax(plot_data=read_rc_data['wt'], axi=ax_list[7], data_range=data_range, 
                            x_range=width_range, bins_=100,density=False, xlabel='FWHM (deg)',quantail=1)
                        
    ax8, im8, cax8 = replt.plot_imshow_ax(plot_data=read_rc_data['h'], axi=ax_list[8], 
                                    data_range=data_range, v_range=height_range, 
                                    title='Height',pixel_size=pixel_size) 

    ax9 = replt.plot_hist_ax(plot_data=read_rc_data['h'], axi=ax_list[9], data_range=data_range, 
                            x_range=height_range,bins_=100,density=False,xlabel='Height', quantail=0.99) 

    ax10, im10, cax10 = replt.plot_imshow_ax(plot_data=read_rc_data['ht'], axi=ax_list[10], 
                                        data_range=data_range, v_range=(0,0),
                                        title='Nomalized Height difference',pixel_size=pixel_size) 

    ax11 = replt.plot_hist_ax(plot_data=read_rc_data['ht'], axi=ax_list[11], data_range=data_range, 
                            x_range=(0,0), bins_=100, density=False,
                            xlabel='Nomalized Height difference', quantail=0.99) 
    
    fig.colorbar(im0,ax=ax0,cax=cax0)
    fig.colorbar(im1,ax=ax1,cax=cax1)
    fig.colorbar(im4,ax=ax4,cax=cax4)
    fig.colorbar(im5,ax=ax5,cax=cax5)
    fig.colorbar(im8,ax=ax8,cax=cax8)
    fig.colorbar(im10,ax=ax10,cax=cax10)
  
    # plt.tight_layout()
    fig.suptitle(title)

    if save:
        filename=re_replace(title)
        plt.savefig(f'{filename}.{ext}', dpi=dpi)
       
    plt.show()


def rc_2plots(read_rc_data, data_range=None, peak_range=(0,0),width_range=(0,0),title='RC2plot', save=False, dpi=DPI, ext=EXT, pixel_size=PIX_SIZE):
    """average peak and histgram, fwhm and histgram
    
      (1)ct,(2) ct hist, 
      (3)wt, (4)wt hist

    Args:
        read_rc_data (dict): rc load data name
            {'c': peak (arecsec), 'h':height, 'w':width (arcsec), 'ct':peak-ave (deg), 'ht':(height-ave)/ave, 'wt':width (deg) }
        rc data:{'c': peak (arecsec), 'h':height, 'w':width (arcsec), 'ct':peak-ave (deg), 'ht':height-ave, 'wt':width (deg) }
        data_range (tuple, optional): (str_x,end_x,str_y,end_y) Defaults to None.
        peak_range(tuple, optional): (0,0) means autoscale
        width_range(tuple, optional): (0,0) means autoscale
        title (str, optional): figure title name. Defaults to 'RC2plot'.
        save (bool, optional): save image save name is 'title' name
        ext (str,optional): save image type suffix. Default to EXT.
        dpi (int, optional): dpi. Default to DPI.
        pixel_size(float, optional): detctor pixel size [mm]. Default to 0.05.
        
    Returns:
        void

    """
    nrow=2
    ncol=2
    fig, ax = plt.subplots(nrow, ncol, figsize=(ncol*width_u,nrow*height_u), squeeze=False, tight_layout=True)
    # fig, ax = plt.subplots(nrow, ncol, figsize=(10,8), squeeze=False, tight_layout=True)

    h,w  = read_rc_data['c'].shape

    ax_list=[]    
    for i in range(nrow):
        for j in range(ncol):
            ax_list.append(ax[i,j])
    
    ax0, im0, cax0 = replt.plot_imshow_ax(plot_data=read_rc_data['ct'], axi=ax_list[0], 
                                        data_range=data_range, v_range=peak_range, 
                                        title='$\Delta\\theta$ ($^{\circ}$)',pixel_size=pixel_size)
    
    ax1 = replt.plot_hist_ax(plot_data=read_rc_data['ct'], axi=ax_list[1], data_range=data_range, x_range=peak_range,
                            bins_=100,density=False, xlabel='$\Delta\\theta$ ($^{\circ}$)',
                            title='$\Delta\\theta$ histgram', quantail=0.9999)
    
    ax2, im2, cax2 = replt.plot_imshow_ax(plot_data=read_rc_data['wt'], axi=ax_list[2], 
                                    data_range=data_range, v_range=width_range,
                                    title='FWHM ($^{\circ}$)',pixel_size=pixel_size)
  
    
    ax3 = replt.plot_hist_ax(plot_data=read_rc_data['wt'], axi=ax_list[3], data_range=data_range, 
                             x_range=width_range,
                             bins_=100,density=False,xlabel='FWHM ($^{\circ}$)',
                             title='FWHM histgram', quantail=0.999)
    
     
    fig.colorbar(im0,ax=ax0,cax=cax0)
    fig.colorbar(im2,ax=ax2,cax=cax2)

    # plt.tight_layout()
    fig.suptitle(title)

    if save:
        filename=re_replace(title)
        plt.savefig(f'{filename}.{ext}', dpi=dpi)
        
    plt.show()


def rc_3plots(read_rc_data, data_range=None, peak_range =(0,0),width_range =(0,0),height_range =(0,0),
              title='RC3plot', save=False, dpi=DPI, ext=EXT, pixel_size=PIX_SIZE):
    """3 plots for RC
        
        (1)ct (2)wt, (3)h
  
    Args:
        read_rc_data (dict): rc load data name
            {'c': peak (arecsec), 'h':height, 'w':width (arcsec), 'ct':peak-ave (deg), 'ht':height-ave, 'wt':width (deg) }
        data_range (tuple, optional): (str_x,end_x,str_y,end_y) Defaults to None.
        peak_range(tuple, optional): ct range,(0,0) means autoscale
        width_range(tuple, optional): wt range, (0,0) means autoscale
        height_range(tuple, optional): h range, (0,0) means autoscale
        title (str, optional): figure title name. Defaults to 'RC3plot'.
        save (bool, optional): save image save name is 'title' name
        ext (str,optional): save image type suffix. Default to EXT.
        dpi (int, optional): dpi. Default to DPI.
        pixel_size(float, optional): detctor pixel size [mm]. Default to 0.05.
        
    Returns:
        void

    """
    nrow=1
    ncol=3
    fig, ax = plt.subplots(nrow, ncol, figsize=(ncol*width_u,nrow*(height_u+0.5)), squeeze=False, tight_layout=True)
    # fig, ax = plt.subplots(nrow, ncol, figsize=(16,6), squeeze=False, tight_layout=True)

    h,w  = read_rc_data['c'].shape
  
    ax_list=[]    
    for i in range(nrow):
        for j in range(ncol):
            ax_list.append(ax[i,j])
    
    ax0, im0, cax0 = replt.plot_imshow_ax(plot_data=read_rc_data['ct'], axi=ax_list[0], 
                                    data_range=data_range, v_range=peak_range, 
                                    title='$\Delta\\theta$ ($^{\circ}$)',pixel_size=pixel_size)

    ax1, im1, cax1 = replt.plot_imshow_ax(plot_data=read_rc_data['wt'], axi=ax_list[1], 
                                    data_range=data_range, v_range=width_range,
                                    title='FWHM ($^{\circ}$)',pixel_size=pixel_size)
     
    ax2, im2, cax2 = replt.plot_imshow_ax(plot_data=read_rc_data['h'], axi=ax_list[2], 
                                    data_range=data_range, v_range=height_range, 
                                    title='Height',pixel_size=pixel_size) 
    
    
    fig.colorbar(im0,ax=ax0,cax=cax0)
    fig.colorbar(im1,ax=ax1,cax=cax1)
    fig.colorbar(im2,ax=ax2,cax=cax2)

    # plt.tight_layout()
    fig.suptitle(title)

    if save:
        filename=re_replace(title)
        plt.savefig(f'{filename}.{ext}', dpi=dpi)
    plt.show()


# ----------- q plot ------------

def qcp_12plots(q_dict, title='qxyz qr$\\theta$$\phi$', step=200, save=False, dpi=DPI, ext=EXT, pixel_size=PIX_SIZE):
    """q xyz(cartesian) and polar plot
    
    (1)qx, (2)qx hist, (3)qy, (4)qy hist
    (5)qz, (6)qr, (7)q_theta, (8)q_theta hist
    (9)q_phi, (10)q_phi hist, (11)q_xy, (12)q_phi quiver

    Args:
        q_dict (dict):  {'x':qx, 'y':qy, 'z':qz, 'xy':qxy, 'ang':q_ang, 'angxy':q_angxy, 'r':q_r}
        title (str, optional): title. Defaults to 'qxyz qr$\theta$$\phi$'.
        step (int, optional): quiver step. Default to 200.
        save (bool, optional): save. Defaults to False.
        ext (str,optional): save image type suffix. Default to EXT.
        dpi (int, optional): dpi. Default to DPI.
        pixel_size(float, optional): detctor pixel size [mm]. Default to 0.05.
        
    Returns:
        void
        
    Examples:
        folder = '2R_0p120'
        q_0p = rean.load_q_tif(folder)
        
    """
    
    
    nrow=3
    ncol=4
    fig, ax = plt.subplots(nrow, ncol, figsize=(ncol*width_u,nrow*height_u), squeeze=False, tight_layout=True)
    # fig, ax = plt.subplots(nrow, ncol, figsize=(16,10), squeeze=False, tight_layout=True)

    ax_list=[]    
    for i in range(nrow):
        for j in range(ncol):
            ax_list.append(ax[i,j])
    
    ax0, im0, cax0 = replt.plot_imshow_ax(plot_data=q_dict['x'],axi=ax_list[0], v_range=(0,0), 
                                        title='$q_x$',pixel_size=pixel_size)

    ax1 = replt.plot_hist_ax(plot_data=q_dict['x'],axi=ax_list[1], x_range=(0,0), 
                            bins_=100, density=False, xlabel='$q_x$',title='$q_x$ histgram')
    
    ax2, im2, cax2 = replt.plot_imshow_ax(plot_data=q_dict['y'],axi=ax_list[2], v_range=(0,0), 
                                        title='qy',pixel_size=pixel_size)

    ax3 = replt.plot_hist_ax(plot_data=q_dict['y'],axi=ax_list[3], x_range=(0,0), 
                        bins_=100, density=False, xlabel='$q_y$',title='$q_y$ histgram')
    
    ax4, im4, cax4 = replt.plot_imshow_ax(plot_data=q_dict['z'],axi=ax_list[4], v_range=(0,0), 
                                        title='$q_z$',pixel_size=pixel_size)

    ax5, im5, cax5 = replt.plot_imshow_ax(plot_data=q_dict['r'],axi=ax_list[5], v_range=(0,0), 
                                        title='$q_r$',pixel_size=pixel_size)
    
    ax6, im6, cax6 = replt.plot_imshow_ax(plot_data=q_dict['ang'], axi=ax_list[6],v_range=(0,0), 
                                        title='$q_{\\theta}$ ($^{\circ}$)',pixel_size=pixel_size)

    ax7 = replt.plot_hist_ax(plot_data=q_dict['ang'],axi=ax_list[7], x_range=(0,0.3), bins_=100, 
                            density=False, xlabel='$q_{\\theta}$ ($^{\circ}$)',title='$q_{\\theta}$ histgram')
    
    xr,yr = rean.getXY(1, q_dict['angxy'], deg_or_rad='deg')
    ax8, im8, cax8 = replt.plot_quiver2d_ax(xr,yr,q_dict['angxy'], axi=ax_list[8], step=step, 
                                                title='$q_{\phi}$ with arrow ($^{\circ}$)',pixel_size=pixel_size)

    ax9 = replt.plot_hist_ax(plot_data=q_dict['angxy'],axi=ax_list[9], x_range=(-180,180), 
                            bins_=100, density=False, xlabel='$q_{\phi}$ ($^{\circ}$)',title='$q_{\phi}$ histgram')
    
    ax10, im10, cax10 = replt.plot_imshow_ax(plot_data=q_dict['xy'],axi=ax_list[10], v_range=(0,0), 
                                            title='$q_{xy}$',pixel_size=pixel_size)
    
    ax11 = replt.plot_hist_ax(plot_data=q_dict['xy'],axi=ax_list[11], x_range=(0,0), 
                              bins_=100, density=False, xlabel='$q_{xy}$',title='$q_{xy}$ histgram')
    

    
    fig.colorbar(im0,ax=ax0,cax=cax0)
    fig.colorbar(im2,ax=ax2,cax=cax2)
    fig.colorbar(im4,ax=ax4,cax=cax4,format='%.5f')
    fig.colorbar(im5,ax=ax5,cax=cax5,format='%.5f')
    fig.colorbar(im6,ax=ax6,cax=cax6)
    fig.colorbar(im8,ax=ax8,cax=cax8)
    fig.colorbar(im10,ax=ax10,cax=cax10)
   
    
    fig.suptitle(title)
    plt.tight_layout()

    if save:
        filename=re_replace(title)
        plt.savefig(f'{filename}.{ext}', dpi=dpi)
    plt.show()

def qc_4plots(q_dict, title='q$_x$, q$_y$', step=200, qx_range=(0,0), qy_range=(0,0), save=False, dpi=DPI, ext=EXT, pixel_size=PIX_SIZE):
    """q cartesian plot
    
    (1)qx, (2)qx hist, (3)qy, (4)qy hist

    Args:
        q_dict (dict):  {'x':qx, 'y':qy, 'z':qz, 'xy':qxy, 'ang':q_ang, 'angxy':q_angxy, 'r':q_r}
        title (str, optional): title. Defaults to 'qxyz qr$\theta$$\phi$'.
        step (int, optional): quiver step. Default to 200.
        qx_range (tuple, optional): Default to (0,0) means  autoscale
        qy_range (tuple, optional): Default to (0,0) means  autoscale
        save (bool, optional): save. Defaults to False.
        ext (str,optional): save image type suffix. Default to EXT.
        dpi (int, optional): dpi. Default to DPI.
        pixel_size(float, optional): detctor pixel size [mm]. Default to 0.05.
    """
    
    
    nrow=2
    ncol=2
    fig, ax = plt.subplots(nrow, ncol, figsize=(ncol*width_u,nrow*height_u), squeeze=False, tight_layout=True)


    ax_list=[]    
    for i in range(nrow):
        for j in range(ncol):
            ax_list.append(ax[i,j])
    
    ax0, im0, cax0 = replt.plot_imshow_ax(plot_data=q_dict['x'],axi=ax_list[0], v_range=qx_range, 
                                        title='$q_x$',pixel_size=pixel_size)

    ax1 = replt.plot_hist_ax(plot_data=q_dict['x'],axi=ax_list[1], x_range=qx_range, 
                            bins_=100, density=False, xlabel='$q_x$',title='$q_x$ histgram')
    
    ax2, im2, cax2 = replt.plot_imshow_ax(plot_data=q_dict['y'],axi=ax_list[2], v_range=qy_range, 
                                        title='$q_y$',pixel_size=pixel_size)

    ax3 = replt.plot_hist_ax(plot_data=q_dict['y'],axi=ax_list[3], x_range=qy_range, 
                        bins_=100, density=False, xlabel='$q_y$',title='$q_y$ histgram')
    
    # ax4, im4, cax4 = replt.plot_imshow_ax(plot_data=q_dict['z'],axi=ax_list[4], v_range=(0,0), 
    #                                     title='qz',pixel_size=pixel_size)
    
    # ax5 = replt.plot_hist_ax(plot_data=q_dict['z'],axi=ax_list[5], x_range=(0,0), 
    #                     bins_=100, density=False, xlabel='qz',title='qz histgram')
    # ax_list[5].axis("off")
    
    fig.colorbar(im0,ax=ax0,cax=cax0)
    fig.colorbar(im2,ax=ax2,cax=cax2)
    # fig.colorbar(im4,ax=ax4,cax=cax4,format='%.5f')

    fig.suptitle(title)
    plt.tight_layout()
    
    if save:
        filename=re_replace(title)
        plt.savefig(f'{filename}.{ext}', dpi=dpi)
        
    plt.show()
    
def qp_4plots(q_dict, title='q polar', ang_range=(0,0.25),save=False, dpi=DPI, ext=EXT, pixel_size=PIX_SIZE):
    """q polar plot
    theta: between z and r
    phi: between x, y
    (1) q phi, (2) q phi hist
    (3) q theta (4) q theta hist

    Args:
        q_dict (dict): q load data {'x':qx, 'y':qy, 'z':qz, 'xy':qxy, 'ang':q_ang, 'angxy':q_angxy, 'r':q_r}
        title (str, optional): figure title. Defaults to 'q polar'.
        ang_range (tuple, optional): q_theta range. Default to (0,0.25)
        save (bool, optional): figure save. Defaults to False.
        ext (str,optional): save image type suffix. Default to EXT.
        dpi (int, optional): dpi. Default to DPI.
        pixel_size(float, optional): detctor pixel size [mm]. Default to 0.05.
    """
    
    nrow=2
    ncol=2

    fig, ax = plt.subplots(nrow, ncol, figsize=(ncol*width_u,nrow*height_u), squeeze=False, tight_layout=True)

    ax_list=[]    
    for i in range(nrow):
        for j in range(ncol):
            ax_list.append(ax[i,j])
    

    ax0, im0, cax0 = replt.plot_imshow_ax(plot_data=q_dict['angxy'],axi=ax_list[0], v_range=(-180,180), 
                                        title='$q_{\phi}$ ($^{\circ}$)',pixel_size=pixel_size)

    ax1 = replt.plot_hist_ax(plot_data=q_dict['angxy'],axi=ax_list[1], x_range=(-180,180), 
                            bins_=100, density=False, xlabel='$q_{\phi}$ ($^{\circ}$)',title='$q_{\phi}$ histgram')

    ax2, im2, cax2 = replt.plot_imshow_ax(plot_data=q_dict['ang'],axi=ax_list[2], v_range=ang_range, 
                                        title='$q_{\\theta}$ ($^{\circ}$)',pixel_size=pixel_size)

    ax3 = replt.plot_hist_ax(plot_data=q_dict['ang'],axi=ax_list[3], x_range=ang_range, 
                            bins_=100, density=False, xlabel='$q_{\\theta}$ ($^{\circ}$)',title='$q_{\\theta}$ histgram')
    
    fig.colorbar(im0,ax=ax0,cax=cax0)
    fig.colorbar(im2,ax=ax2,cax=cax2)
    
    plt.tight_layout()
    fig.suptitle(title)

    if save:
        filename=re_replace(title)
        plt.savefig(f'{filename}.{ext}', dpi=dpi)
    plt.show()

def qp3_4plots(q_dict, title='$q_r$$q_{\theta}$$q_{\phi}$',ang_range=(0,0.25), step=200, 
               save=False, dpi=DPI, ext=EXT, pixel_size=PIX_SIZE,magnify=800):
    """q  polar + 3d plot
    
    (1)q_theta, (2)q_theta hist
    (3)q_phi quiver (4)3d-image

    Args:
        q_dict (dict):  {'x':qx, 'y':qy, 'z':qz, 'xy':qxy, 'ang':q_ang, 'angxy':q_angxy, 'r':q_r}
        title (str, optional): title. Defaults to 'qxyz qr$\theta$$\phi$'.
        ang_range (tuple, optional): q_theta range. Default to (0,0.25)
        step (int, optional): quiver step. Default to 200.
        save (bool, optional): save. Defaults to False.
        ext (str,optional): save image type suffix. Default to EXT.
        dpi (int, optional): dpi. Default to DPI.
        pixel_size(float, optional): detctor pixel size [mm]. Default to 0.05.
    """
    
    
    nrow=2
    ncol=2
    fig, ax = plt.subplots(nrow, ncol, figsize=(ncol*width_u,nrow*height_u), squeeze=False, tight_layout=True)

    ax_list=[]    
    for i in range(nrow):
        for j in range(ncol):
            ax_list.append(ax[i,j])
    
    
    ax0, im0, cax0 = replt.plot_imshow_ax(plot_data=q_dict['ang'], axi=ax_list[0],v_range=ang_range, 
                                        title='$q_{\\theta}$ ($^{\circ}$)',pixel_size=pixel_size)

    ax1 = replt.plot_hist_ax(plot_data=q_dict['ang'],axi=ax_list[1], x_range=ang_range, bins_=100, 
                            density=False, xlabel='$q_{\\theta}$ ($^{\circ}$)',title='$q_{\\theta}$ histgram')
    
    
    xr,yr = rean.getXY(1, q_dict['angxy'], deg_or_rad='deg')
    ax2, im2, cax2 = replt.plot_quiver2d_ax(xr,yr,q_dict['angxy'], axi=ax_list[2], step=step, 
                                                title='$q_{\phi}$ with arrow ($^{\circ}$)',pixel_size=pixel_size)


    
    fig.colorbar(im0,ax=ax0,cax=cax0)
    
    # cax2.set_ticklabels(['-180','-90','0','90','180']) 
    # cax2.set_ticks([-180,-90,0,90,180]) 
    fig.colorbar(im2,ax=ax2,cax=cax2,ticks=[-180,-90,0,90,180])

    fig.suptitle(title)
    plt.tight_layout()

    ax_list[3].axis("off")
    ax_list[3] = fig.add_subplot(nrow,ncol,4,projection='3d') 
    ax3 = replt.plot_quiver3d_ax(qx_data=q_dict['x'], qy_data=q_dict['y'], qz_data=q_dict['z'], qxy_data=q_dict['xy'], 
                                 axi=ax_list[3], step=step, title='$q_{\phi}$ + $q_{\\theta}$ with arrow',pixel_size=pixel_size,magnify=magnify)

    
    # plt.gray()
    if save:
        filename=re_replace(title)
        plt.savefig(f'{filename}.{ext}', dpi=dpi)
     
    plt.show()
    
    
def qp3_3plots(q_dict, title='q polar', xy_range=(0,0.01),step=200, save=False, dpi=DPI, ext=EXT, pixel_size=PIX_SIZE,magnify=800):
    """q polar plot
    
    (1) q_phi quiver
    (2) qxy image
    (3) qx,qy,qz 3d-image

    Args:
        q_dict (dict): q load data {'x':qx, 'y':qy, 'z':qz, 'xy':qxy, 'ang':q_ang, 'angxy':q_angxy, 'r':q_r}
        title (str, optional): figure title. Defaults to 'q polar'.
        xy_range (tuple,optional): image plot v_range. if (0,0), autoscale. Default to (0,0.01).
        step (int, optional): quiver step. Default to 200.
        save (bool, optional): save. Defaults to False.
        ext (str,optional): save image type suffix. Default to EXT.
        dpi (int, optional): dpi. Default to DPI.
        pixel_size(float, optional): detctor pixel size [mm]. Default to 0.05.
        
    """
    
    nrow=1
    ncol=3
    fig, ax = plt.subplots(nrow, ncol, figsize=(ncol*width_u,nrow*height_u), squeeze=False, )

    ax_list=[]    
    for i in range(nrow):
        for j in range(ncol):
            ax_list.append(ax[i,j])
    

    xr,yr = rean.getXY(1, q_dict['angxy'], deg_or_rad='deg')
    ax0, im0, cax0 = replt.plot_quiver2d_ax(xr,yr,q_dict['angxy'], axi=ax_list[0], step=step, 
                                            title='$q_{\phi}$ with arrow ($^{\circ}$)',pixel_size=pixel_size)

    ax1, im1, cax1 = replt.plot_imshow_ax(plot_data=q_dict['xy'], axi=ax_list[1], v_range=xy_range, 
                                            title='$q_{xy}$',pixel_size=pixel_size)

    
    fig.colorbar(im0,ax=ax0,cax=cax0)
    fig.colorbar(im1,ax=ax1,cax=cax1)
    
    plt.tight_layout()

    ax_list[2].axis("off")
    ax_list[2] = fig.add_subplot(1,3,3,projection='3d') 
    ax2 = replt.plot_quiver3d_ax(qx_data=q_dict['x'], qy_data=q_dict['y'], qz_data=q_dict['z'], qxy_data=q_dict['xy'], 
                            axi=ax_list[2], step=step, title='$q_{\phi}$ + $q_{\\theta}$ with arrow',pixel_size=pixel_size,magnify=magnify)

    fig.suptitle(title)

    if save:
        filename=re_replace(title)
        plt.savefig(f'{filename}.{ext}', dpi=dpi)
        
    plt.show()   

def qp3_1plots(q_dict, title='q polar', xy_range=(0,0.01),step=200, save=False, dpi=DPI, ext=EXT, pixel_size=PIX_SIZE,magnify=800):
    """3d-image plot
    
        Args:   
            q_dict (dict): q load data {'x':qx, 'y':qy, 'z':qz, 'xy':qxy, 'ang':q_ang, 'angxy':q_angxy, 'r':q_r}
            title (str, optional): figure title. Defaults to 'q polar'.
            xy_range (tuple,optional): image plot v_range. if (0,0), autoscale. Default to (0,0.01).
            step (int, optional): quiver step. Default to 200.
            save (bool, optional): save. Defaults to False.
            ext (str,optional): save image type suffix. Default to EXT.
            dpi (int, optional): dpi. Default to DPI.
            pixel_size(float, optional): detctor pixel size [mm]. Default to 0.05.
        
    """
    
    nrow=1
    ncol=1
    fig, ax = plt.subplots(nrow, ncol, figsize=(ncol*width_u,nrow*height_u), squeeze=False)

    ax_list=[]    
    for i in range(nrow):
        for j in range(ncol):
            ax_list.append(ax[i,j])
    
    ax_list[0].axis("off")
    ax_list[0] = fig.add_subplot(1,1,1,projection='3d') 
    ax0 = replt.plot_quiver3d_ax(qx_data=q_dict['x'], qy_data=q_dict['y'], qz_data=q_dict['z'], qxy_data=q_dict['xy'], 
                            axi=ax_list[0], step=step,title='',pixel_size=pixel_size,magnify=magnify)

    fig.suptitle(title)

    if save:
        filename=re_replace(title)
        plt.savefig(f'{filename}.{ext}', dpi=dpi)
        
    plt.show()   

# ------ 
   
def image_hist_fig(plt_data, data_range=None, img_range=(0,0), imgtitle='', h_range=(0,0.15), h_xlabel='value'):
    """image and histgram plot

    Args:
        plt_data (2D ndarray): image plot data
        data_range (tuple, optional): (str_x,end_x,str_y,end_y) Defaults to None.
        img_range (tuple, optional): vmin vmax range. 
                                    if (0,0) is auto scale. Defaults to (0,0).
        imgtitle (str, optional): image title. Defaults to ''.
        h_range (tuple, optional): histgram range. Defaults to (0,0.15).
        h_xlabel (str, optional): histgram x label. Defaults to 'cos value'.
    
    example:
        image_hist_fig(plt_data=q2['qx'],data_range=None,img_range=(0,0),
                        imgtitle='qx',h_range=(0,0.15),h_xlabel='cos value') 
    """
    fig = plt.figure(figsize=(10,5)) 
    ax1 = fig.add_subplot(121) 
    ax2 = fig.add_subplot(122) 

    _, im, cax = replt.plot_imshow_ax(plot_data=plt_data, axi=ax1, data_range=data_range,v_range=img_range, title=imgtitle)
    _ = replt.plot_hist_ax(plot_data=plt_data, axi=ax2, data_range=data_range, x_range=h_range,bins_=100,
                           density=False,xlabel=h_xlabel)
    
    fig.colorbar(im, cax=cax)
    plt.tight_layout()
    plt.show() 
    

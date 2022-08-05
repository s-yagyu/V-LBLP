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


# memo figsize=(width,height) wdth:height= 4:3 unit
# (row,col)->figsize(col*4,row*3): (3,4)->figsize(16,9)

# width_u = 4
# height_u = 3
# width_u = 4.8
# height_u = 3.6

width_u = 5.2
height_u = 4

# Detector pixcel size
PIX_SIZE = 0.05

# save figure parameter
DPI = 300
EXT = 'pdf' # png, jpg

plt.rcParams["font.size"] = 14
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
                             x_range=peak_range,bins_=100,density=True, xlabel='Peak difference(deg)', quantail=0.9999) 

    ax4, im4, cax4 = replt.plot_imshow_ax(plot_data=read_rc_data['w'], axi=ax_list[4], 
                                    data_range=data_range, v_range=(0,0),title='FWHM (arcsec)', pixel_size=pixel_size)

    ax5, ax6, im5, cax5 = replt.plot_line_ax(plot_data=read_rc_data['wt'], axi=[ax_list[5],ax_list[6]], 
                                    data_range=data_range, v_range=width_range, 
                                    row_num=row_num, title='FWHM (deg)') 

    ax7 = replt.plot_hist_ax(plot_data=read_rc_data['wt'], axi=ax_list[7], data_range=data_range, 
                            x_range=width_range, bins_=100,density=True, xlabel='FWHM (deg)',quantail=1)
                        
    ax8, im8, cax8 = replt.plot_imshow_ax(plot_data=read_rc_data['h'], axi=ax_list[8], 
                                    data_range=data_range, v_range=height_range, 
                                    title='Height',pixel_size=pixel_size) 

    ax9 = replt.plot_hist_ax(plot_data=read_rc_data['h'], axi=ax_list[9], data_range=data_range, 
                            x_range=height_range,bins_=100,density=True,xlabel='Height', quantail=0.99) 

    ax10, im10, cax10 = replt.plot_imshow_ax(plot_data=read_rc_data['ht'], axi=ax_list[10], 
                                        data_range=data_range, v_range=(0,0),
                                        title='Nomalized Height difference',pixel_size=pixel_size) 

    ax11 = replt.plot_hist_ax(plot_data=read_rc_data['ht'], axi=ax_list[11], data_range=data_range, 
                            x_range=(0,0), bins_=100, density=True,
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
                            bins_=100,density=True, xlabel='$\Delta\\theta$ ($^{\circ}$)',
                            title='$\Delta\\theta$ histgram', quantail=0.9999)
    
    ax2, im2, cax2 = replt.plot_imshow_ax(plot_data=read_rc_data['wt'], axi=ax_list[2], 
                                    data_range=data_range, v_range=width_range,
                                    title='FWHM ($^{\circ}$)',pixel_size=pixel_size)
  
    
    ax3 = replt.plot_hist_ax(plot_data=read_rc_data['wt'], axi=ax_list[3], data_range=data_range, 
                             x_range=width_range,
                             bins_=100,density=True,xlabel='FWHM ($^{\circ}$)',
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

    rc data:{'c': peak (arecsec), 'h':height, 'w':width (arcsec), 'ct':peak-ave (deg), 'ht':height-ave, 'wt':width (deg)}
    plots
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
                            bins_=100, density=True, xlabel='$q_x$',title='$q_x$ histgram')
    
    ax2, im2, cax2 = replt.plot_imshow_ax(plot_data=q_dict['y'],axi=ax_list[2], v_range=(0,0), 
                                        title='qy',pixel_size=pixel_size)

    ax3 = replt.plot_hist_ax(plot_data=q_dict['y'],axi=ax_list[3], x_range=(0,0), 
                        bins_=100, density=True, xlabel='$q_y$',title='$q_y$ histgram')
    
    ax4, im4, cax4 = replt.plot_imshow_ax(plot_data=q_dict['z'],axi=ax_list[4], v_range=(0,0), 
                                        title='$q_z$',pixel_size=pixel_size)

    ax5, im5, cax5 = replt.plot_imshow_ax(plot_data=q_dict['r'],axi=ax_list[5], v_range=(0,0), 
                                        title='$q_r$',pixel_size=pixel_size)
    
    ax6, im6, cax6 = replt.plot_imshow_ax(plot_data=q_dict['ang'], axi=ax_list[6],v_range=(0,0), 
                                        title='$q_{\\theta}$ ($^{\circ}$)',pixel_size=pixel_size)

    ax7 = replt.plot_hist_ax(plot_data=q_dict['ang'],axi=ax_list[7], x_range=(0,0.3), bins_=100, 
                            density=True, xlabel='$q_{\\theta}$ ($^{\circ}$)',title='$q_{\\theta}$ histgram')
    
    xr,yr = rean.getXY(1, q_dict['angxy'], deg_or_rad='deg')
    ax8, im8, cax8 = replt.plot_quiver2d_ax(xr,yr,q_dict['angxy'], axi=ax_list[8], step=step, 
                                                title='$q_{\phi}$ with arrow ($^{\circ}$)',pixel_size=pixel_size)

    ax9 = replt.plot_hist_ax(plot_data=q_dict['angxy'],axi=ax_list[9], x_range=(-180,180), 
                            bins_=100, density=True, xlabel='$q_{\phi}$ ($^{\circ}$)',title='$q_{\phi}$ histgram')
    
    ax10, im10, cax10 = replt.plot_imshow_ax(plot_data=q_dict['xy'],axi=ax_list[10], v_range=(0,0), 
                                            title='$q_{xy}$',pixel_size=pixel_size)
    
    ax11 = replt.plot_hist_ax(plot_data=q_dict['xy'],axi=ax_list[11], x_range=(0,0), 
                              bins_=100, density=True, xlabel='$q_{xy}$',title='$q_{xy}$ histgram')
    

    
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
    
    ax0, im0, cax0 = replt.plot_imshow_ax(plot_data=q_dict['x'],axi=ax_list[0], v_range=(0,0), 
                                        title='$q_x$',pixel_size=pixel_size)

    ax1 = replt.plot_hist_ax(plot_data=q_dict['x'],axi=ax_list[1], x_range=qx_range, 
                            bins_=100, density=True, xlabel='$q_x$',title='$q_x$ histgram')
    
    ax2, im2, cax2 = replt.plot_imshow_ax(plot_data=q_dict['y'],axi=ax_list[2], v_range=(0,0), 
                                        title='$q_y$',pixel_size=pixel_size)

    ax3 = replt.plot_hist_ax(plot_data=q_dict['y'],axi=ax_list[3], x_range=qy_range, 
                        bins_=100, density=True, xlabel='$q_y$',title='$q_y$ histgram')
    
    # ax4, im4, cax4 = replt.plot_imshow_ax(plot_data=q_dict['z'],axi=ax_list[4], v_range=(0,0), 
    #                                     title='qz',pixel_size=pixel_size)
    
    # ax5 = replt.plot_hist_ax(plot_data=q_dict['z'],axi=ax_list[5], x_range=(0,0), 
    #                     bins_=100, density=True, xlabel='qz',title='qz histgram')
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
                            bins_=100, density=True, xlabel='$q_{\phi}$ ($^{\circ}$)',title='$q_{\phi}$ histgram')

    ax2, im2, cax2 = replt.plot_imshow_ax(plot_data=q_dict['ang'],axi=ax_list[2], v_range=ang_range, 
                                        title='$q_{\\theta}$ ($^{\circ}$)',pixel_size=pixel_size)

    ax3 = replt.plot_hist_ax(plot_data=q_dict['ang'],axi=ax_list[3], x_range=ang_range, 
                            bins_=100, density=True, xlabel='$q_{\\theta}$ ($^{\circ}$)',title='$q_{\\theta}$ histgram')
    
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
                            density=True, xlabel='$q_{\\theta}$ ($^{\circ}$)',title='$q_{\\theta}$ histgram')
    
    
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
    _ = replt.plot_hist_ax(plot_data=plt_data, axi=ax2, data_range=data_range, x_range=h_range,bins_=100,density=True,xlabel=h_xlabel)
    
    fig.colorbar(im, cax=cax)
    plt.tight_layout()
    plt.show() 
    
           


# --- old----
def q_12plots(q_dict, title='', data_range=None, step=50, hist_x_range=(0,0.2), save=False, dpi=DPI, sig_select=False):
    """12 plots for q  vector
    
    (1)qx, (2)qy, (3)qz, (4) qxy
    (5)polar cos x, (6)cos x sign, (7) polar cos x hist,(8)qxy vector
    (9)polar cos y, (10) cos y sign (11)polar cos y hist, (12) qxy tilting angle hist
    origin ='upper' or 'lower'
    
    Args:
        q_dict (dict): q load data {'x':qx, 'y':qy, 'z':qz, 'xy':qxy, 'ang':q_ang, 'angxy':q_angxy, 'r':q_r}
        title (str, optional): figure title name. Defaults to ''.
        origin (str, optional): origin position. Defaults to 'upper'.
        step (int, optional): quiver step. Default to 50.
        save (bool, optional): save. Defaults to False.
        dpi (int, optional): dpi. Default to DPI.

    Returns:
        void
    """
    nrow=3
    ncol=4
    fig, ax = plt.subplots(nrow, ncol, figsize=(ncol*width_u,nrow*height_u), squeeze=False, tight_layout=True)
    # fig, ax = plt.subplots(nrow, ncol, figsize=(16,10), squeeze=False, tight_layout=True)

    # Polar codinates
    qcx = q_dict['x'].copy()
    qcy = q_dict['y'].copy()
    q_r, q_t = rean.getRD(x=qcx, y=qcy, out_deg_or_rad='rad')
    q_ri, q_ti = rean.getRD(y=qcx, x=qcy, out_deg_or_rad='rad')
    qcx=np.cos(q_t)
    qcy=np.cos(q_ti)
    
    def select_array(ndata):
        x = ndata
        # condlist = [x<=-0.5, (x > -0.5) & (x < 0), x==0, (x > 0) & (x < 0.5), x>=0.5]
        # choicelist = [-1,-0.5,0,0.5,1]
        condlist = [x<=-0.5, (x > -0.5) & (x < 0.5), x>=0.5]
        choicelist = [-1,0,1]
        y =np.select(condlist, choicelist, np.nan)

        return y
    
    if sig_select == True:

        qcxsig = select_array(qcx)
        qcysig = select_array(qcy)
    else:
        qcxsig = np.sign(qcx)
        qcysig = np.sign(qcy)

    qxy = q_dict['xy']
    qxyz_ang = q_dict['ang']

    ax_list=[]    
    for i in range(nrow):
        for j in range(ncol):
            ax_list.append(ax[i,j])
    
    ax0, im0, cax0 = replt.plot_imshow_ax(plot_data=q_dict['x'], axi=ax_list[0], 
                                         data_range=data_range, v_range=(0,0), title='qx')

    ax1, im1, cax1 = replt.plot_imshow_ax(plot_data=q_dict['y'], axi=ax_list[1], 
                                         data_range=data_range, v_range=(0,0), title='qy')

    ax2, im2, cax2 = replt.plot_imshow_ax(plot_data=q_dict['z'], axi=ax_list[2], 
                                         data_range=data_range, v_range=(0,0), title='qz')

    ax3, im3, cax3 = replt.plot_imshow_ax(plot_data=qxy, axi=ax_list[3], 
                                         data_range=data_range, v_range=(0,0), title='$\|qxy\|=\sqrt{qx^{2}+qy^{2}}$') 
    # 'qxy=$\sqrt{q^{2}_{x}+q^{2}_{y}}$'
    # cax3.yaxis.get_major_formatter().set_useOffset(False)
    
    # cax3.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
    ax4, im4, cax4 = replt.plot_imshow_ax(plot_data=qcx, axi=ax_list[4], 
                                         data_range=data_range, v_range=(-1.1,1.1), 
                                         title='x cos value')

    # title=r'$cos\theta = \left(\frac{\vec{qxy}\cdot\vec{ux}}{\|qxy\|\|ux\|}\right)$'
    ax5 = replt.plot_hist_ax(plot_data=qcx, axi=ax_list[5], data_range=data_range, x_range=(-1.1,1.1),
                        bins_=100,density=True,title='x cos value histgram', xlabel='x cos value')

    ax6, im6, cax6 = replt.plot_imshow_ax(plot_data=qcxsig, axi=ax_list[6], 
                                         data_range=data_range, v_range=(-1.1,1.1), title='x sign',)                                

    ax7 = replt.plot_quiver_ax(qx_data=q_dict['x'], qy_data=q_dict['y'], axi=ax_list[7], step=step, 
                                title='Distortion direction')
    
    ax8, im8, cax8 = replt.plot_imshow_ax(plot_data=qcy, axi=ax_list[8], 
                                         data_range=data_range, v_range=(-1.1,1.1), 
                                         title='y cos value', )

    ax9 = replt.plot_hist_ax(plot_data=qcy, axi=ax_list[9], data_range=data_range, x_range=(-1.1,1.1),
                           bins_=100, density=True, title='y cos value histgram', xlabel='y cos value')

    ax10, im10, cax10 = replt.plot_imshow_ax(plot_data=qcysig, axi=ax_list[10], 
                                         data_range=data_range, v_range=(-1.1,1.1), title='y sign')                                       

    ax11 = replt.plot_hist_ax(plot_data=qxyz_ang, axi=ax_list[11], data_range=data_range, x_range=hist_x_range,
                           bins_=100, density=True, title='Tilting angle histgram',xlabel='Relative tilting angle [deg]')
    
    
    fig.colorbar(im0,ax=ax0,cax=cax0)
    fig.colorbar(im1,ax=ax1,cax=cax1)
    fig.colorbar(im2,ax=ax2,cax=cax2,format='%.5f')
    fig.colorbar(im3,ax=ax3,cax=cax3)
    fig.colorbar(im4,ax=ax4,cax=cax4)
    fig.colorbar(im6,ax=ax6,cax=cax6)
    fig.colorbar(im8,ax=ax8,cax=cax8)
    fig.colorbar(im10,ax=ax10,cax=cax10)

    plt.tight_layout()
    fig.suptitle(title)
    # plt.gray()

    if save:
        filename=re_replace(title)
        plt.savefig(f'{filename}.png"', dpi=dpi)
        # plt.savefig(f"{title.replace(' ', '_')}.png", dpi=dpi)
    plt.show()


def q_12xyplots(q_dict, title='',data_range=None, row_num=None, col_num=None, save=False, dpi=DPI):
    """12 plots for q  vector
    
    (1)qx, (2)x-line, (3)y-line, (4)hist
    (5)qy, (6)x-line, (7)y-line, (8)hist
    (9)qxy, (10)x-line, (11)y-line, (12)hist
    
    origin ='upper' or 'lower'
    
    Args:
        q_dict (dict): q load data {'x':qx, 'y':qy, 'z':qz, 'xy':qxy, 'ang':q_ang, 'angxy':q_angxy, 'r':q_r}
        title (str, optional): figure title name. Defaults to ''.
        origin (str, optional): origin position. Defaults to 'upper'.
        save (bool, optional): save image save name is 'title' name
        dpi (int, optional): dpi. Default to DPI.
    Returns:
        void
    """
    nrow=3
    ncol=4
    fig, ax = plt.subplots(nrow, ncol, figsize=(ncol*width_u,nrow*height_u), squeeze=False, tight_layout=True)
    # fig, ax = plt.subplots(nrow, ncol, figsize=(16,10), squeeze=False, tight_layout=True)

    h,w  = q_dict['x'].shape
    qxy = q_dict['xy']
    qxyz_ang = q_dict['ang']

    if row_num == None:
        row_num = h/2

    if col_num == None:
        col_num =w/2

    ax_list=[]    
    for i in range(nrow):
        for j in range(ncol):
            ax_list.append(ax[i,j])
    
    ax0, ax1, ax2, im0, cax0 = replt.plot_xyline_ax(plot_data=q_dict['x'], axi=ax_list[0:3], 
                                            data_range=data_range, v_range=(0,0), title='qx', 
                                            row_num=row_num, col_num=col_num)
    ax3 = replt.plot_hist_ax(plot_data=q_dict['x'], axi=ax_list[3], data_range=data_range, x_range=(0,0),
                        bins_=100,density=True,xlabel='qx')
    
    ax4, ax5, ax6, im4, cax4 = replt.plot_xyline_ax(plot_data=q_dict['y'], axi=ax_list[4:7], 
                                            data_range=data_range, v_range=(0,0), title='qy', 
                                            row_num=row_num, col_num=col_num)
    ax7 = replt.plot_hist_ax(plot_data=q_dict['y'], axi=ax_list[7], data_range=data_range, x_range=(0,0),
                        bins_=100,density=True,xlabel='qy')
    
    ax8, ax9, ax10, im8, cax8 = replt.plot_xyline_ax(plot_data=qxy, axi=ax_list[8:11], 
                                            data_range=data_range, v_range=(0,0), title='|qxy|', 
                                            row_num=row_num, col_num=col_num)
    
    ax11 = replt.plot_hist_ax(plot_data=qxy, axi=ax_list[11], data_range=data_range, x_range=(0,0),
                        bins_=100,density=True,xlabel='|qxy|')
    
    
    fig.colorbar(im0,ax=ax0,cax=cax0)
    fig.colorbar(im4,ax=ax4,cax=cax4)
    fig.colorbar(im8,ax=ax8,cax=cax8)

    # plt.tight_layout()
    fig.suptitle(title)
    # plt.gray()
    if save:
        filename=re_replace(title)
        plt.savefig(f'{filename}.png"', dpi=dpi)
        # plt.savefig(f"{title.replace(' ', '_')}.png", dpi=dpi)
    plt.show()


def q_3plots(q_dict, title='', data_range=None, step=50, hist_x_range=(0,0.2), save=False, dpi=DPI):
    """3 plots for q  vector

    (1) qxy
    (2) qxy vector
    (3) qxy tilting angle hist
    
    origin ='upper' or 'lower'
    
    Args:
        q_dict (dict): q load data {'x':qx, 'y':qy, 'z':qz, 'xy':qxy, 'ang':q_ang, 'angxy':q_angxy, 'r':q_r}
        title (str, optional): figure title name. Defaults to ''.
        origin (str, optional): origin position. Defaults to 'upper'.
        save (bool, optional): save image save name is 'title' name
        dpi (int, optional): dpi. Default to DPI.

    Returns:
        void
    """
    nrow=1
    ncol=3
    fig, ax = plt.subplots(nrow, ncol, figsize=(ncol*width_u,nrow*height_u), squeeze=False, tight_layout=True)
    # fig, ax = plt.subplots(nrow, ncol, figsize=(16,6), squeeze=False, tight_layout=True)

    qxy = q_dict['xy']
    qxyz_ang = q_dict['ang']

    ax_list=[]    
    for i in range(nrow):
        for j in range(ncol):
            ax_list.append(ax[i,j])
    
    ax0, im0, cax0 = replt.plot_imshow_ax(plot_data=qxy, axi=ax_list[0], 
                                         data_range=data_range, v_range=(0,0), title='$\|qxy\|=\sqrt{qx^{2}+qy^{2}}$') 
                                   
    ax1 = replt.plot_quiver_ax(qx_data=q_dict['x'], qy_data=q_dict['y'], axi=ax_list[1], step=step, title='Distortion direction')
    
    ax2 = replt.plot_hist_ax(plot_data=qxyz_ang, axi=ax_list[2], data_range=data_range, x_range=hist_x_range,
                           bins_=100, density=True, title='Tilting angle histgram', xlabel='Relative tilting angle [deg]')
    
    
    fig.colorbar(im0,ax=ax0,cax=cax0)
   
    plt.tight_layout()
    fig.suptitle(title)
    # plt.gray()

    if save:
        filename=re_replace(title)
        plt.savefig(f'{filename}.png"', dpi=dpi)
        # plt.savefig(f"{title.replace(' ', '_')}.png", dpi=dpi)
    plt.show()
    

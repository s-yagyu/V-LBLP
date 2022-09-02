"""
plot module
"""
__author__ = "Shinjiro Yagyu"
__license__ = "BSD-3-Clause"
__copyright__ = "National Institute for Materials Science, Japan"
__date__ = "2022/09/02"
__version__= "1.0.0"
__revised__ = "2022/09/02"

from pathlib import Path
from turtle import color
from PIL import Image

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker

import mpl_toolkits.axes_grid1
from mpl_toolkits.mplot3d import Axes3D

from qfit import re_analysis as rean

CMAP = "gist_rainbow_r"
# CMAP = "gist_rainbow"
# CMAP = "gist_ncar_r"
# cmap_=plt.cm.gist_earth

PIX_SIZE = 0.05 # Detector pixel size

plt.rcParams["font.size"] = 14
plt.rcParams['font.family']= 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']


def plot_imshow_ax(plot_data, axi=None, data_range=None, v_range=(0,0), title='',origin='upper',pixel_size=PIX_SIZE, arrow=False):
    """plot image

    Args:
        plot_data (2D ndarray): image plot data
        axi (optional): one ax object. Defaults to None.
        data_range (tuple, optional): (str_x,end_x,str_y,end_y) Defaults to None.
        v_range (tuple, optional): vmin vmax range. 
                                if (0,0) is auto scale. Defaults to (0,0).
                                example :vmin=-0.2, vmax=0.2
        title (str, optional): title description. Defaults to ''.
        origin (str, optional): y axsis direction. Defaults to 'upper'.
                                'upper' or 'lower'
                                upper -> (0,0) left top : default
                                loer ->  (0,0) left bottom
        pixel_size(float, optional):Detector pixel size [mm]. Defaults to 0.05,(50 micron).
        arrow(bool, optional):xy arrow drowing . Defaults to False.
        
    Returns:
        if  axi != None:  -> ax
        axi  = None: -> None 

    Example:
        _ = plot_imshow_ax(plot_data=q2['qx'], axi=None, data_range=None,v_range=(0,0), title='',origin='upper')
    """
    
    if data_range == None:
        # sty, edy = 0, h 
        # stx, edx = 0, w
        select_data = plot_data
    else:
        stx, edx = data_range[0], data_range[1]
        sty, edy = data_range[2], data_range[3] 
        select_data = plot_data[sty:edy,stx:edx]

    if axi == None:
        fig_ = plt.figure()
        ax_ = fig_.add_subplot(111)
    else:
        ax_ = axi   
    divider = mpl_toolkits.axes_grid1.make_axes_locatable(ax_)
    cax = divider.append_axes('right', '5%', pad='3%')

    if v_range == (0,0):
        im = ax_.imshow(select_data, cmap=CMAP, interpolation='none', origin=origin)
    else:
        im = ax_.imshow(select_data, cmap=CMAP, interpolation='none',
                       vmin=v_range[0], vmax=v_range[1], origin=origin)

    ax_.set_title(title)
    ax_.set_ylabel("y (mm)")
    ax_.set_xlabel("x (mm)")
    x_ticks = ax_.get_xticks()[1:-1]
    y_ticks = ax_.get_yticks()[1:-1]
    x_labels = [f'{int(i*pixel_size)}' for i in x_ticks]
    y_labels = [f'{int(i*pixel_size)}' for i in y_ticks]
    # x_labels = [f'{i*pixel_size}' for i in x_ticks]
    # y_labels = [f'{i*pixel_size}' for i in y_ticks]
    
    ax_.set_xticks(x_ticks)
    ax_.set_xticklabels(x_labels)
    ax_.set_yticks(y_ticks)
    ax_.set_yticklabels(y_labels)

    if arrow:
        startpoint=(200,200)
        incr = 300
        endx=(startpoint[0]+incr,startpoint[1])
        endy=(startpoint[0],startpoint[1]+incr)

        #x
        ax_.annotate('', xy=endx, xytext=startpoint,
                arrowprops=dict(shrink=0, width=0.5, headwidth=4, 
                                headlength=4, connectionstyle='arc3'))
        #y
        ax_.annotate('', xy=endy, xytext=startpoint,
                arrowprops=dict(shrink=0, width=0.5, headwidth=4, 
                                headlength=4, connectionstyle='arc3'))
        ax_.text(300,150,'x')
        ax_.text(80,400,'y')

    if axi == None:
        fig_.colorbar(im, cax=cax)
        plt.show()
        return  None
    else:
        return ax_, im, cax


def plot_line_ax(plot_data, axi=None, data_range=None, v_range=(0,0), row_num=1250, title='',origin='upper',pixel_size=PIX_SIZE):
    """plot image

    Args:
        plot_data (2D ndarray): image plot data
        axi (list, optional): ax object. Defaults to None.
                            example:[ax0,ax1]
        data_range (tuple, optional): (str_x,end_x,str_y,end_y) Defaults to None.
        v_range (tuple, optional): vmin vmax range. 
                                if (0,0) is auto scale. Defaults to (0,0).
                                example :vmin=-0.2, vmax=0.2
        row_num (int, optional):cross section line. Defaults to 1250.
        title (str, optional): title description. Defaults to ''.
        origin (str, optional): y axsis direction. Defaults to 'upper'.
                                'upper' or 'lower'
                                upper -> (0,0) left top : default
                                loer ->  (0,0) left bottom
        pixel_size(float, optional):Detector pixel size [mm]. Defaults to 0.05,(50 micron).
        
    Returns:
        if  axi  = None 
        -> None 
        
        else
        -> ax0, ax1, im, cax
    """
    
    if data_range == None:
        # sty, edy = 0, h 
        # stx, edx = 0, w
        select_data = plot_data
    else:
        stx, edx = data_range[0], data_range[1]
        sty, edy = data_range[2], data_range[3] 
        select_data = plot_data[sty:edy,stx:edx]
        
    h, w= select_data.shape   
    # print(f'Row(NX):{h}, Column(NY):{w}')

    start = (0,row_num)
    end = (w,row_num)
 
    if axi == None:
        fig, (ax0,ax1) = plt.subplots(ncols=2,figsize=(8,4))
    else:
        ax0 = axi[0]
        ax1 = axi[1]
        
    divider = mpl_toolkits.axes_grid1.make_axes_locatable(ax0)
    cax = divider.append_axes('right', '5%', pad='3%')
    
    if v_range == (0,0):
        im = ax0.imshow(select_data, cmap=CMAP, interpolation='none',origin=origin)
        ax1.plot(select_data[row_num,:],'ro-')
    else:
        im = ax0.imshow(select_data, cmap=CMAP, interpolation='none',
                       vmin=v_range[0], vmax=v_range[1], origin=origin)
        ax1.set_ylim(v_range)
        
    ax1.plot(select_data[row_num,:],'ro-')
    ax0.plot([start[0],end[0]],[start[1],end[1]],'r-',lw=2)

    ax0.set_title(title)
    ax0.set_ylabel("y (mm)")
    ax0.set_xlabel("x (mm)")
    x_ticks = ax0.get_xticks()[1:-1]
    y_ticks = ax0.get_yticks()[1:-1]
    x_labels = [f'{i*pixel_size}' for i in x_ticks]
    y_labels = [f'{i*pixel_size}' for i in y_ticks]
    ax0.set_xticks(x_ticks)
    ax0.set_xticklabels(x_labels)
    ax0.set_yticks(y_ticks)
    ax0.set_yticklabels(y_labels)

    ax1.set_title(f'x line profile: {row_num*pixel_size}')
    ax1.set_xticks(x_ticks)
    ax1.set_xticklabels(x_labels)
 

    if axi == None:
        fig.colorbar(im, cax=cax)
        plt.tight_layout()
        plt.show()
        return  None
    else:
        return ax0, ax1, im, cax


def plot_quiver_ax(qx_data, qy_data, axi=None, step=100, title='Vector', origin='upper', pixel_size=PIX_SIZE):
    """quiver plot image

    Args:
        Args:
        qx_data (ndarray): 
        qy_data (ndarray): 
        axi (optional): one ax object. Defaults to None. 
        step (int, optional): Defaults to 50
        title (str, optional): title description. Defaults to 'Vector'.
        origin (str, optional): y axsis direction. Defaults to 'upper'.
                                'upper' or 'lower'
                                upper -> (0,0) left top : default
                                loer ->  (0,0) left bottom
        pixel_size(float, optional):Detector pixel size [mm]. Defaults to 0.05,(50 micron).
                               
    Returns:
        if  axi != None -> ax
        axi  = None -> None 

    Example:
        _ = plot_quiver_ax(qx_data, qy_data, axi=None, step=50, origin='upper')
    Ref:
        https://www.sairablog.com/article/matplotlib-quiver-vector-visualization.html
        
    """

    if axi == None:
        fig_ = plt.figure()
        ax_ = fig_.add_subplot(111)
    else:
        ax_ = axi   
        
    xdata = qx_data[::step,::step]
    ydata = qy_data[::step,::step]
    
    
    if origin == 'upper': # Note: https://www.fixes.pub/program/243536.html
        ax_.invert_yaxis()
        ydata =-ydata
       
    ax_.quiver(xdata, ydata, color='blue',width=0.003, headwidth=7,
               headlength=9,)
    
    ax_.set_title(title)
    
    ax_.set_ylabel("y (mm)")
    ax_.set_xlabel("x (mm)")
    x_ticks = ax_.get_xticks()[1:-1]
    y_ticks = ax_.get_yticks()[1:-1]
    x_labels = [f'{i*pixel_size*step}' for i in x_ticks]
    y_labels = [f'{i*pixel_size*step}' for i in y_ticks]
    
    ax_.set_xticks(x_ticks)
    ax_.set_xticklabels(x_labels)
    ax_.set_yticks(y_ticks)
    ax_.set_yticklabels(y_labels)    

    ax_.set_aspect('equal')

    if axi == None:
        plt.show()
        return  None
    else:
        return ax_


def plot_quiver2d_ax(qx_data, qy_data, qxy_data, axi=None, step=250, title='Vector',pixel_size=PIX_SIZE):
    """quiver 2d plot image

    Args:
        qx_data (ndarray): qx data
        qy_data (ndarray): qy data
        qxy_data (ndarray): sqrt(qy**2,qz**2)
        axi (ax object, optional): ax object. Defaults to None.
        step (int, optional): quiver step. Defaults to 250.
        title (str, optional): Graph title. Defaults to 'Vector'.
        pixel_size (float, optional): detector pixel size. Defaults to 0.05.

    Returns:
        if  axi == None -> None
        else -> ax, im, cax
    Example:
        xr,yr=rean.getXY(1, q_0m120['angxy'], deg_or_rad='deg')
        plot_quiver2d_ax(xr,yr,q_0m120['angxy'], step=200)       
    """
    
    if axi == None:
        fig_ = plt.figure()
        ax_ = fig_.add_subplot(111)
    else:
        ax_ = axi   
        
    xdata = qx_data[::step,::step]
    ydata = qy_data[::step,::step]
    
    hs, ws = xdata.shape
    ho, wo = qxy_data.shape

    xo = np.linspace(0, (wo-1)*pixel_size, wo)
    yo = np.linspace(0, (ho-1)*pixel_size, ho)
  
    xs = np.linspace(0, (wo-1)*pixel_size, ws, endpoint=False)
    ys = np.linspace(0, (ho-1)*pixel_size, hs, endpoint=False)
    
    xx, yy = np.meshgrid(xo, yo)
    xxs, yys = np.meshgrid(xs, ys)
    
    
    ax_.invert_yaxis()
    ydata =-ydata
    
    divider = mpl_toolkits.axes_grid1.make_axes_locatable(ax_)
    cax = divider.append_axes('right', '5%', pad='3%')
    
    
    im = ax_.contourf(xx, yy, qxy_data, alpha=1, cmap=CMAP)  # offset=0, 
    # ax_.quiver(xxs, yys, xdata, ydata, color='white', width=0.008, headwidth=7,
    #            headlength=9,)
    ax_.quiver(xxs, yys, xdata, ydata, color='black')
   
    
    ax_.set_title(title)
    
    ax_.set_ylabel("y (mm)")
    ax_.set_xlabel("x (mm)")
    x_ticks = ax_.get_xticks()[0:-1]
    y_ticks = ax_.get_yticks()[0:-1]
    
    x_labels = [f'{int(i)}' for i in x_ticks]
    y_labels = [f'{int(i)}' for i in y_ticks]
    
    ax_.set_xticks(x_ticks)
    ax_.set_xticklabels(x_labels)
    ax_.set_yticks(y_ticks)
    ax_.set_yticklabels(y_labels)    

    ax_.set_aspect('equal')

    if axi == None:
        fig_.colorbar(im, cax=cax)
        plt.show()
        return  None

    else:
        return ax_, im, cax


def plot_quiver3d_ax(qx_data, qy_data, qz_data, qxy_data, axi=None, step=250, title='Vector', 
                     pixel_size=PIX_SIZE, elev=45, azim=0, zlim=(0,8), magnify=800):
    """quiver 3d plot image

    Args:
        qx_data (ndarray): qx data
        qy_data (ndarray): qy data
        qz_data (ndarray): qz data
        qxy_data (ndarray): sqrt(qy**2,qz**2)
        axi (ax object, optional): ax object. Defaults to None.
        step (int, optional): quiver step. Defaults to 250.
        title (str, optional): Graph title. Defaults to 'Vector'.
        pixel_size (float, optional): detector pixel size. Defaults to 0.05.
        elev (int, optional): 3D view. Defaults to 45.
        azim (int, optional):3D view. Defaults to 0.
        zlim (tuple, optional): z-axis limit. Defaults to (0,8).
        magnify (int, optional): x,y tilte value. Defaults to 800.

    Returns:
        if  axi == None -> None
        else -> ax
    """
    
    if axi == None:
        fig_ = plt.figure(figsize=(6.0, 6.0))
        ax_ = fig_.add_subplot(projection='3d')
    else:
        ax_ = axi   
    
    xdata = qx_data[::step,::step]
    ydata = qy_data[::step,::step]
    zdata = qz_data[::step,::step]
    
    ho, wo = qxy_data.shape
    hs, ws = xdata.shape
    
    xo = np.linspace(0, (wo-1)*pixel_size, wo)
    yo = np.linspace(0, (ho-1)*pixel_size, ho)
  
    xs = np.linspace(0, (wo-1)*pixel_size, ws, endpoint=False)
    ys = np.linspace(0, (ho-1)*pixel_size, hs, endpoint=False)
    
    xx, yy = np.meshgrid(xo, yo)
    xxs, yys = np.meshgrid(xs, ys)
    
    
    ax_.quiver(yys, xxs, 0, ydata*magnify, xdata*magnify, zdata, color='red', 
               arrow_length_ratio=0.3,) #normalize=True

    ax_.contourf(yy, xx, qxy_data, alpha=0.5, offset=0, cmap=CMAP)  
    
    ax_.set_title(title)
    
    ax_.set_ylabel("x (mm)")
    ax_.set_xlabel("y (mm)")
    x_ticks = ax_.get_yticks()[1:-1]
    y_ticks = ax_.get_xticks()[1:-1]
    
    # x_labels = [f'{i*pixel_size*step}' for i in x_ticks]
    # y_labels = [f'{i*pixel_size*step}' for i in y_ticks]
    

    x_labels = [f'{int(i)}' for i in x_ticks]
    y_labels = [f'{int(i)}' for i in y_ticks]
    
    ax_.set_xticks(x_ticks)
    ax_.set_xticklabels(x_labels)
    ax_.set_yticks(y_ticks)
    ax_.set_yticklabels(y_labels)
    
    ax_.set_zlim(*zlim)
    ax_.set_zticks([])
    ax_.view_init(elev=elev, azim=azim)

    # ax_.set_aspect('equal')

    if axi == None:
        plt.show()
        return  None
    
    else:
        return ax_
    

def plot_3d_ax(qxy_data, axi=None, title='3d', pixel_size=PIX_SIZE, elev=45, azim=45, ):
    """ 3d plot image plot

    Args:
        qxy_data (ndarray): 2d-arraydata
        axi (ax object, optional): ax object. Defaults to None.
        title (str, optional): Graph title. Defaults to 'Vector'.
        pixel_size (float, optional): detector pixel size. Defaults to 0.05.
        elev (int, optional): 3D view. Defaults to 45.
        azim (int, optional):3D view. Defaults to 45.   
                               
    Returns:
        if  axi != None -> ax
        axi  = None -> None 
        
    """
  
    if axi == None:
        fig_ = plt.figure()
        ax_ = fig_.add_subplot(111, projection='3d')
    else:
        ax_ = axi   
        

    ho, wo = qxy_data.shape
    
    img_copy = qxy_data.copy()
    img_copy[np.isnan(qxy_data)] = 0

    xo = np.linspace(0, (wo-1)*pixel_size, wo)
    yo = np.linspace(0, (ho-1)*pixel_size, ho)
  
    xx, yy = np.meshgrid(xo, yo)
  
    # ax_.contourf(yy, xx, qxy_data, alpha=0.5, offset=0, cmap=cmap_)  
    # ax_.plot_wireframe(yy, xx, qxy_data,cmap=cmap_)
    # ax_.scatter3D(np.ravel(yy), np.ravel(xx),  qxy_data)
    # ax.set_title("Scatter Plot")
    
    #Nanがあるとダメ
    ax_.plot_surface(xx,yy, img_copy, cmap=CMAP, linewidth=0, antialiased=False)

    print(xx.shape,yy.shape,qxy_data.shape)

    ax_.set_title(title)
    
    ax_.set_ylabel("x (mm)")
    ax_.set_xlabel("y (mm)")
    x_ticks = ax_.get_yticks()[1:-1]
    y_ticks = ax_.get_xticks()[1:-1]
    
    # x_labels = [f'{i*pixel_size*step}' for i in x_ticks]
    # y_labels = [f'{i*pixel_size*step}' for i in y_ticks]
    
    x_labels = [f'{int(i)}' for i in x_ticks]
    y_labels = [f'{int(i)}' for i in y_ticks]
    
    ax_.set_xticks(x_ticks)
    ax_.set_xticklabels(x_labels)
    ax_.set_yticks(y_ticks)
    ax_.set_yticklabels(y_labels)   
    # ax_.set_zticks([])
    
    # ax_.set_zlim(0,0.1) 
    ax_.view_init(elev=elev, azim=azim)
    # ax_.set_aspect('equal')

    if axi == None:
        plt.show()
        return  None

    else:
        return ax_
 
def plot_hist_ax(plot_data, axi=None, data_range=None, x_range=(0,0.15), bins_=100, density=False,
                title='Histgram', xlabel="Relative tilting angle [deg]", ylabel="Probability", 
                color='Red', quantail=1.0):
    """histgram plot

    Args:
        plot_data (2D ndarray): image plot data
        axi (optional): one ax object. Defaults to None.
        data_range (tuple, optional): 
                        (str_x,end_x,str_y,end_y) Defaults to None.
        x_range (tuple, optional): histgram range if (0,0) then auto-scale. Defaults to (0,0.15).
        bins_ (int, optional): bins. Defaults to 100.
        density (bool, optional): Normalize. all count is 1. Defaults to False.
        title (str, optional): title. Defaults to 'Histgram'.
        xlabel (str, optional): x label. Defaults to "Relative tilting angle [deg]".
        ylabel (str, optional): y label. Defaults to "Probability".
        color (str, optional): color. Defaults to 'Red'.
        quantail (float, opttional): remove high value.  range 0.5 (median) to 1.0 Defaults to 1.0
        
    Returns:
        if  axi != None -> ax
        axi  = None -> None 

    Ref:
        matplotlib:histgram normedの挙動
        https://qiita.com/ponnhide/items/571e896915306f42c0c1
        
    """
    
    def data_quantail(data,val=0.85):
        wt_temp = data
        wt_temp =np.where(wt_temp < np.nanquantile(data,val), wt_temp, np.nan)
        return wt_temp 
     
    # h, w = plot_data.shape
    
    if data_range == None:
        # sty, edy = 0, h 
        # stx, edx = 0, w
        select_data = plot_data
    else:
        stx, edx = data_range[0], data_range[1]
        sty, edy = data_range[2], data_range[3] 
        select_data = plot_data[sty:edy,stx:edx]
    
    xyzdata = select_data.reshape(-1)
    
    xyzdata = data_quantail(xyzdata,val=quantail)
    
    xyzdata = xyzdata[~np.isnan(xyzdata)]
    
    if axi == None:
        fig_ = plt.figure()
        ax_ = fig_.add_subplot(111)

    else:
        ax_ = axi
    
    if x_range == (0,0):
        if density:
            weights = np.ones_like(xyzdata) / len(xyzdata)
            ax_.hist(xyzdata, bins=bins_, density=False, weights=weights,color=color)
        else:
            ax_.hist(xyzdata, bins=bins_, density=density, color=color)
    else:
        if density:
            weights = np.ones_like(xyzdata) / len(xyzdata)
            ax_.hist(xyzdata, range=x_range, bins=bins_, density=False, weights=weights,color=color)
            ax_.set_xlim(*x_range)
        else:
            ax_.hist(xyzdata, range=x_range, bins=bins_, density=density, color=color)
            ax_.set_xlim(*x_range)

    
    ax_.set_ylabel(ylabel)
    ax_.set_xlabel(xlabel) 
    ax_.set_title(title)
    
    if axi == None:
        plt.show()
        return  None

    else:
        return ax_    

        
def plot_xyline_ax(plot_data, axi=None, data_range=None, v_range=(0,0), title='Cross section', 
                    row_num=500, col_num=500, origin='upper', pixel_size=PIX_SIZE):
    """xy lineprofile

    Args:
        plot_data (2D ndarray): image plot data
        data_range (tuple, optional): select data range
                         (str_x,end_x,str_y,end_y) Defaults to None.
        v_range (tuple, optional): 
                            vmin vmax range. 
                             if (0,0) is auto scale. Defaults to (0,0).
                            example :vmin=-0.2, vmax=0.2 -> (-0.2,0.2)
        title (str, optional): title. Defaults to 'Cross section'.
        row_num (int, optional): row position. Defaults to 500. Y
        col_num (int, optional): col position. Defaults to 500. X
        origin (str, optional): y axsis direction. Defaults to 'upper'.
                            'upper' or 'lower'
                            upper -> (0,0) left top : default
                            loer ->  (0,0) left bottom
        pixel_size(float, optional):Detector pixel size [mm]. Defaults to 0.05,(50 micron).
                            
    Returns:
        if set axi ->
        axi  = None -> None 
        
    example:
        plot_xylineplofile(plot_data=q2['qx'], data_range=(450,1550,400,1500),
                            v_range=(0,0), title='', row_num=500, col_num=500, origin='upper')
    """
    
    if data_range == None:
        # sty, edy = 0, h 
        # stx, edx = 0, w
        select_data = plot_data
    else:
        stx, edx = data_range[0], data_range[1]
        sty, edy = data_range[2], data_range[3] 
        select_data = plot_data[sty:edy,stx:edx]
        
    h, w= select_data.shape
   
    # print(f'Row(NX):{h}, Column(NY):{w}')
    starty = (0,row_num)
    endy = (w,row_num)
    startx = (col_num,0)
    endx = (col_num,h)
  

    if axi == None:
        fig, (ax0,ax1,ax2) = plt.subplots(ncols=3,figsize=(15,5))
        
    else:
        ax0 = axi[0]
        ax1 = axi[1]
        ax2 = axi[2]

    divider = mpl_toolkits.axes_grid1.make_axes_locatable(ax0)
    cax = divider.append_axes('right', '5%', pad='3%')
    
    if v_range == (0,0):
        im = ax0.imshow(select_data, cmap=CMAP, interpolation='none',origin=origin)
        ax1.plot(select_data[row_num,:],'ro-')
        ax2.plot(select_data[:,col_num],'bo-')
        ax1.set_xlim(0,w)
        ax2.set_xlim(0,h)
    else:
        im = ax0.imshow(select_data, cmap=CMAP, interpolation='none',
                       vmin=v_range[0], vmax=v_range[1], origin=origin)
        ax1.plot(select_data[row_num,:],'ro-')
        ax2.plot(select_data[:,col_num],'bo-')
        ax1.set_ylim(v_range)
        ax2.set_ylim(v_range)
        ax1.set_xlim(0,w)
        ax2.set_xlim(0,h)
        
    ax0.set_title(title)
    ax0.set_ylabel("y [mm]")
    ax0.set_xlabel("x [mm]")
    ax0.plot([starty[0],endy[0]],[starty[1],endy[1]],'r-',lw=3)
    ax0.plot([startx[0],endx[0]],[startx[1],endx[1]],'b-',lw=3)

    x_ticks = ax0.get_xticks()[1:-1]
    y_ticks = ax0.get_yticks()[1:-1]
    x_labels = [f'{i*pixel_size}' for i in x_ticks]
    y_labels = [f'{i*pixel_size}' for i in y_ticks]
    
    ax0.set_xticks(x_ticks)
    ax0.set_xticklabels(x_labels)
    ax0.set_yticks(y_ticks)
    ax0.set_yticklabels(y_labels)

    ax1.set_title(f'x line : {col_num*pixel_size}')
    ax2.set_title(f'y line : {row_num*pixel_size}')
    
    if axi == None:
        fig.colorbar(im, cax=cax)
        plt.tight_layout()
        plt.show()
        return  None

    else:
        return ax0, ax1, ax2, im, cax


def plot_text_ax(text_list, axi):
    """text write

    Args:
        text_list (list): text list
        axi (ax object): 

    Returns:
       ax object: 
       
    """

    axi.set_ylim(0, 10)
    axi.set_xlim(0, 10)
    plt.setp(axi, frame_on=False, xticks=(), yticks=())
    for i ,ml in enumerate(text_list):
        axi.text(0,10-i,ml)

    return axi

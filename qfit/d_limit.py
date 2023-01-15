"""
Estimate d and psi limit

|Δd/d| < (∆λ/λ) -  (Δpcot(θB)/(2Lsin(2θB)))

example condtions
- ∆λ/λ= 2.8 x 10-4
- Δp = 0.05 mm
- L = 500 mm 
- λ = 1.284 Å
- GaN (112¯4) d = 1.006 Å
- Bragg angle(θB) : 39.66°
- 2θB: 79.3°
- incident angle: 0.58°
- Another limitation about the local lattice-plane curvature |∆ψ| 
  arises from the geometrical consideration on a plane perpendicular to the diffraction plane.
- |∆ψ| < ∆p/L.
- tan(θ)= ∆p/L
- |∆ψ| is smaller than 1.0x 10-4rad (=0.0057◦) at L=0.5 m.

"""

__author__ = "Shinjiro Yagyu"
__license__ = "BSD-3-Clause"
__copyright__ = "National Institute for Materials Science, Japan"
__date__ = "2022/09/02"
__version__= "1.0.0"
__revised__ = "2023/01/15"

from pathlib import Path
import re

import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np

from qfit import re_analysis as rean
from qfit import re_plot as replt
from qfit import multiplot as mlplt

# plt.rcParams["font.size"] = 14
plt.rcParams['font.family']= 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']



def limit_estimate(ramda=1.284, d=1.006, dp=0.05, L=500, drr=2.8e-04):
    """
    Estimation of experimental condition limits

    |Δd/d| < (∆λ/λ) -  (Δpcot(θB)/(2Lsin(2θB)))

    Args:
        ramda (float, optional): inciden wavelength (lambda). Defaults to 1.284.
        d (float, optional): lattice constant. Defaults to 1.006.
        dp (float, optional): pixcl size[mm]. Defaults to 0.05.
        L (int, optional): Camera distance[mm]. Defaults to 500.
        drr ([type], optional): dispersion of incident wavelength (lambda). Defaults to 2.8e-04.

    Returns:
        float: limit value
    
    Examples:
        >>> gan_param = {"ramda":1.284, 'd':1.006, 'dp':0.05, 'drr':2.8e-04, 'L':500}
            '**' means dict unpack
        >>> lim_res = dlim.limit_estimate(**gan_param)

    """

    #Bragg angle:thB-> d = ramda/(sin(tha+th2B))
    thB = np.rad2deg(np.arcsin(ramda/(2*d)))
    limt_res = drr - (0.05*(1/np.tan(np.deg2rad(thB)))/(2*L*np.sin(np.deg2rad(2*thB))))
    print(f'Limit: {limt_res:e}, thB: {thB}, th2B: {thB*2}')
    
    return limt_res


def dd_calc_4plot(data, title='$\Delta$ d/d at $\psi=0$', dd_xange=(0,2.5e-4), 
                    ramda=1.284, d=1.004, dp=0.05, L=500, drr=2.8e-04, pixel_size=0.05,
                    save=False, dpi=300, ext='pdf'):

    """Calculation and display  of dd/d limit
    (1) RC analysis result, (2) result of assign the angular component to the d component
    (3) Difference between neighboring pixels, (4) (3)'s histgram

    Args:
        data (dict): load RC data
        title (str, optional): Figure title. Defaults to '4 inch 0'.
        dd_xange (tuple, optional): dd/d range. Defaults to (0,2.5e-4).

        ramda (float, optional): inciden wavelength (lambda). Defaults to 1.284.
        d (float, optional): lattice constant. Defaults to 1.006.
        dp (float, optional): pixcl size[mm]. Defaults to 0.05.
        L (int, optional): Camera distance[mm]. Defaults to 500.
        drr ([type], optional): dispersion of incident wavelength (lambda). Defaults to 2.8e-04.
        pixel_size (float,optional): detector pixel size. Defaults to 0.05.

        save (bool, optional): save figure. Defaults to False.
        dpi (int, optional): dpi. Defaults to 300.
        ext (str, optional): save type. png, jpg, pdf. Defaults to 'pdf'.

    Returnes:
        void
    """
    

    #Bragg angle:thB-> d = ramda/(sin(tha+th2B))
    thB = np.rad2deg(np.arcsin(ramda/(2*d)))
    limt_res = limit_estimate(ramda, d, dp, L, drr)
    # Assume the average angle is the Bragg reflection angle.
    # Assign the angular component to the d component
    d_side = ramda/(2*np.sin(np.deg2rad(data['ct']+thB)))

    # pixel difference
    dd_d = np.abs(np.diff(d_side, prepend=0)/d)

    message_list=[f'|Δd/d| < (∆λ/λ) -  (Δpcot(θB)/(2Lsin(2θB))) = 2.18e-4',
                    'L = 500mm','∆λ/λ = {drr}','∆p = {dp}mm',f'{d} Å for GaN (112¯4)',
                    'λ = {ramda} Å',
                    'Bragg angle(θB) = {thB:.2f}°','2θB = {thB*2:.2f}°',
                    'limit= {limt_res:.2e}'
                    ]
                    #'Result','|Δd/d| = 2e-4/1.006 = 1.988e-04<2.18e-04','97.5% in 2.18e-4'
    # width_u = 4.8
    # height_u = 3.6
    width_u = 5.2
    height_u = 4
    nrows=2
    ncols=2

    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*width_u,nrows*height_u), squeeze=False, tight_layout=True)
    # fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12,12), squeeze=False, tight_layout=True) 
    ax0, im0, cax0 = replt.plot_imshow_ax(plot_data=data['ct'], axi=ax[0,0], v_range=(0,0), 
                                          title='$\Delta\\theta$ ($^{\circ}$)',pixel_size=pixel_size)
    ax1, im1, cax1 = replt.plot_imshow_ax(plot_data=d_side, axi=ax[0,1],  v_range=(0,0), 
                                          title='d ($\AA$)',pixel_size=pixel_size)
                                         # title=f'd ($\AA$) GaN(112¯4) {d}[$\AA$]'
    ax2, im2, cax2 = replt.plot_imshow_ax(plot_data=dd_d, axi=ax[1,0],v_range=dd_xange, 
                                          title=f'$\Delta$d/d',pixel_size=pixel_size)
    ax3 = replt.plot_hist_ax(dd_d, axi=ax[1,1], x_range=dd_xange, bins_=100, density=False, 
                             title='$\Delta$d/d histgram', xlabel="$\Delta$d/d",quantail=1)
    ax3.axvline(x=limt_res, color='blue')
    ax3_y_ticks = ax3.get_yticks()
    ax3.text(limt_res+limt_res*0.01,ax3_y_ticks[1],f'limit\n {limt_res:.2e}')
    
    # ax3.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax3.ticklabel_format(style="sci", axis="x",scilimits=(0,0))
    
    # ax3.set_ylim(0,100000)
    # ax[0,1].axis("off")
    # _ = replt.plot_text_ax(text_list=message_list, axi=ax[2,1])
    fig.colorbar(im0,ax=ax0,cax=cax0)
    fig.colorbar(im1,ax=ax1,cax=cax1)
    fig.colorbar(im2,ax=ax2,cax=cax2,format='%.2e')
    fig.suptitle(title)
    plt.tight_layout()

    if save:
        filename=mlplt.re_replace(title)
        plt.savefig(f'{filename}.{ext}', dpi=dpi)

    plt.show()

def dpsi_calc_4plot(data, title='$\Delta \Psi$', dp_xange=(0,2.5e-4), 
                    ramda=1.284, d=1.004, dp=0.05, L=500, drr=2.8e-04, pixel_size=0.05,
                    save=False, dpi=300, ext='pdf'):

    """Calculation and display of |∆ψ| limit
    |∆ψ| < ∆p/L = 1.0x 10-4rad (=0.0057◦)
    (1) RC analysis result, (2) result of limitation values
    (3) Difference between neighboring pixels toword vertical , (4) (3)'s histgram
    (5) Difference between neighboring pixels toword holizontal , (6) (4)'s histgram

    Args:
        data (dict): load RC data
        title (str, optional): Figure title. Defaults to '4 inch 0'.
        dd_xange (tuple, optional): dd/d range. Defaults to (0,2.5e-4).

        ramda (float, optional): inciden wavelength (lambda). Defaults to 1.284.
        d (float, optional): lattice constant. Defaults to 1.006.
        dp (float, optional): pixcl size[mm]. Defaults to 0.05.
        L (int, optional): Camera distance[mm]. Defaults to 500.
        drr ([type], optional): dispersion of incident wavelength (lambda). Defaults to 2.8e-04.
        pixel_size (float,optional): detector pixel size. Defaults to 0.05.

        save (bool, optional): save figure. Defaults to False.
        dpi (int, optional): dpi. Defaults to 300.
        ext (str, optional): save type. png, jpg, pdf. Defaults to 'pdf'.

    Returnes:
        void
        
    Note:
        angel difference -0.2 to 0.2 on 4 inch (101.6mm)
        4 inch /50 micron = 2032 point
        0.4 / 2032 = 1.96e-4
       
    """
    

    #Bragg angle:thB-> d = ramda/(sin(tha+th2B))
    thB = np.rad2deg(np.arcsin(ramda/(2*d)))
    limt_res = limit_estimate(ramda, d, dp, L, drr)
    
    limt_psi = 0.0057
    # Assume the average angle is the Bragg reflection angle.
    # Assign the angular component to the d component
    d_side = ramda/(2*np.sin(np.deg2rad(data['ct']+thB)))

    # pixel difference
    dpsi_hv = np.abs(np.diff(data['ct'], axis=-1, prepend=0))
    dpsi_h = np.abs(np.diff(data['ct'], axis=1, prepend=0))
    dpsi_v = np.abs(np.diff(data['ct'], axis=0, prepend=0))

    message_list=[f'|Δd/d| < (∆λ/λ) -  (Δpcot(θB)/(2Lsin(2θB))) = 2.18e-4',
                    f'L = 500mm','∆λ/λ = {drr}',f'∆p = {dp}mm',f'{d} $\AA$ for GaN (112¯4)',
                    f'λ = {ramda} $\AA$',
                    f'Bragg angle(θB) = {thB:.2f}°',f'2θB = {thB*2:.2f}°',
                    f'limit= {limt_res:.2e}',
                    f'|∆ψ| < ∆p/L = 1.0 x 10-4 rad (=0.0057◦)'
                    ]
                    #'Result','|Δd/d| = 2e-4/1.006 = 1.988e-04<2.18e-04','97.5% in 2.18e-4'

    width_u = 5.2
    height_u = 4
    nrows=2
    ncols=2

    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*width_u,nrows*height_u), squeeze=False, tight_layout=True)
    # fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12,12), squeeze=False, tight_layout=True) 
    ax0, im0, cax0 = replt.plot_imshow_ax(plot_data=data['ct'], axi=ax[0,0], v_range=(0,0), 
                                          title='$\Delta\\theta$ ($^{\circ}$)',pixel_size=pixel_size)
    
    # ax1, im1, cax1 = replt.plot_imshow_ax(plot_data=dpsi_hv, axi=ax[0,1],  v_range=dd_xange, title=f'ΔA/A',pixel_size=pixel_size)
    # ax[0,1].axis("off")
    ax1 = replt.plot_hist_ax(plot_data=data['ct'], axi=ax[0,1], x_range=(0,0), bins_=100, density=False, 
                             title='$\Delta\\theta$ histgram', xlabel='$\Delta\\theta$ ($^{\circ}$)', quantail=0.9999) 
    
    # Vertical ΔAngle 
    ax2, im2, cax2 = replt.plot_imshow_ax(plot_data=dpsi_v, axi=ax[1,0],v_range=dp_xange, 
                                          title='$\Delta\Psi$ ($^{\circ}$)',pixel_size=pixel_size)
    ax3 = replt.plot_hist_ax(dpsi_v, axi=ax[1,1], x_range=dp_xange, bins_=100, density=False, 
                             title='$\Delta\Psi$ histgram', xlabel="$\Delta\psi$ ($^{\circ}$)",quantail=1)
    
    # ax4, im4, cax4 = replt.plot_imshow_ax(plot_data=dpsi_h, axi=ax[2,0],v_range=dd_xange, title=f'Horizontal ΔAngle',pixel_size=pixel_size)
    # ax5 = replt.plot_hist_ax(dpsi_h, axi=ax[2,1], x_range=dd_xange, bins_=100, density=False, title='Horizontal ΔAngle Histgram', xlabel="Horizontal ΔA/A [deg]",quantail=1)
    
     # ax3.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax3.ticklabel_format(style="sci", axis="x",scilimits=(0,0))
    ax3.axvline(x=limt_psi, color='blue')
    ax3_y_ticks = ax3.get_yticks()
    ax3.text(limt_psi+limt_psi*0.01,ax3_y_ticks[1],f'limit\n{limt_psi:.1e}')

    # ax[0,1].axis("off")
    # _ = replt.plot_text_ax(text_list=message_list, axi=ax[0,1])
    
    fig.colorbar(im0,ax=ax0,cax=cax0)
    # fig.colorbar(im1,ax=ax1,cax=cax1)
    fig.colorbar(im2,ax=ax2,cax=cax2,format='%.2e')

    # fig.colorbar(im4,ax=ax4,cax=cax4,format='%.2e')
    fig.suptitle(title)
    plt.tight_layout()

    if save:
        filename=mlplt.re_replace(title)
        plt.savefig(f'{filename}.{ext}', dpi=dpi)

    plt.show()


def limt_calc_4plot(data, title='Limit $\Delta$d/d $\cdot$ $\Delta\Psi$', 
                    dd_xange=(0,2.5e-4), dp_xange=(0,6e-3),
                    ramda=1.284, d=1.004, dp=0.05, L=500, drr=2.8e-04, pixel_size=0.05,
                    save=False, dpi=300, ext='pdf'):

    """Calculation and display  of dd/d  and|∆ψ| limit
    |∆ψ| < ∆p/L = 1.0x 10-4rad (=0.0057◦)
    (1) RC analysis result, (2) result of assign the angular component to the d component
    (3) Difference between neighboring pixels, (4) (3)'s histgram

    Args:
        data (dict): load RC data
        title (str, optional): Figure title. Defaults to '4 inch 0'.
        dd_xange (tuple, optional): dd/d range. Defaults to (0,2.5e-4).
        dp_xange (tuple, optional): dpsi range. Defaults to (0,6e-3).

        ramda (float, optional): inciden wavelength (lambda). Defaults to 1.284.
        d (float, optional): lattice constant. Defaults to 1.004.
        dp (float, optional): pixcl size[mm]. Defaults to 0.05.
        L (int, optional): Camera distance[mm]. Defaults to 500.
        drr ([type], optional): dispersion of incident wavelength (lambda). Defaults to 2.8e-04.
        pixel_size (float,optional): detector pixel size. Defaults to 0.05.

        save (bool, optional): save figure. Defaults to False.
        dpi (int, optional): dpi. Defaults to 300.
        ext (str, optional): save type. png, jpg, pdf. Defaults to 'pdf'.

    Returnes:
        void
    """
    

    #Bragg angle:thB-> d = ramda/(sin(tha+th2B))
    thB = np.rad2deg(np.arcsin(ramda/(2*d)))
    limt_res = limit_estimate(ramda, d, dp, L, drr)
    limt_psi = 0.0057
    # Assume the average angle is the Bragg reflection angle.
    # Assign the angular component to the d component
    d_side = ramda/(2*np.sin(np.deg2rad(data['ct']+thB)))

    # pixel difference
    dd_d = np.abs(np.diff(d_side, prepend=0)/d)
    dpsi_v = np.abs(np.diff(data['ct'], axis=0, prepend=0))
     
    message_list=[f'|Δd/d| < (∆λ/λ) -  (Δpcot(θB)/(2Lsin(2θB))) = 2.18e-4',
                    f'L = 500mm','∆λ/λ = {drr}',f'∆p = {dp}mm',f'{d} Å for GaN (112¯4)',
                    f'λ = {ramda} Å',
                    f'Bragg angle(θB) = {thB:.2f}°',f'2θB = {thB*2:.2f}°',
                    f'limit= {limt_res:.2e}',
                    f'|∆ψ| < ∆p/L = 1.0 x 10-4 rad (=0.0057◦)'
                    ]
                    #'Result','|Δd/d| = 2e-4/1.006 = 1.988e-04<2.18e-04','97.5% in 2.18e-4'
    # width_u = 4.8
    # height_u = 3.6
    width_u = 5.2
    height_u = 4
    nrows=2
    ncols=2

    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*width_u,nrows*height_u), squeeze=False, tight_layout=True)
    # fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12,12), squeeze=False, tight_layout=True) 
    
    ax0, im0, cax0 = replt.plot_imshow_ax(plot_data=dd_d, axi=ax[0,0],v_range=dd_xange, 
                                          title=f'$\Delta$d/d',pixel_size=pixel_size)
    ax1 = replt.plot_hist_ax(dd_d, axi=ax[0,1], x_range=dd_xange, bins_=100, density=False, 
                             title='$\Delta$d/d histgram', xlabel="$\Delta$d/d",quantail=1)
    ax1.axvline(x=limt_res, color='blue')
    ax1_y_ticks = ax1.get_yticks()
    ax1.text(limt_res+limt_res*0.01,ax1_y_ticks[1],f'limit\n {limt_res:.2e}')
    # ax3.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax1.ticklabel_format(style="sci", axis="x",scilimits=(0,0))
    
     # Vertical ΔAngle 
    ax2, im2, cax2 = replt.plot_imshow_ax(plot_data=dpsi_v, axi=ax[1,0],v_range=dp_xange, 
                                          title='$\Delta\Psi$ ($^{\circ}$)',pixel_size=pixel_size)
    ax3 = replt.plot_hist_ax(dpsi_v, axi=ax[1,1], x_range=dp_xange, bins_=100, density=False, 
                             title='$\Delta\Psi$ histgram', xlabel="$\Delta\psi$ ($^{\circ}$)",quantail=1)
    # ax3.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax3.ticklabel_format(style="sci", axis="x",scilimits=(0,0))
    ax3.axvline(x=limt_psi, color='blue')
    ax3_y_ticks = ax3.get_yticks()
    ax3.text(limt_psi+limt_psi*0.01,ax3_y_ticks[1],f'limit\n{limt_psi:.1e}')
    
    
    # ax3.set_ylim(0,100000)
    # ax[0,1].axis("off")
    # _ = replt.plot_text_ax(text_list=message_list, axi=ax[2,1])
    fig.colorbar(im0,ax=ax0,cax=cax0,format='%.2e')
    fig.colorbar(im2,ax=ax2,cax=cax2,format='%.2e')
    fig.suptitle(title)
    plt.tight_layout()

    if save:
        filename=mlplt.re_replace(title)
        plt.savefig(f'{filename}.{ext}', dpi=dpi)

    plt.show()
# if __name__ == '__main__':
#     print(limit_estimate(ramda=1.284, d=1.004, dp=0.05, L=500, drr=2.8e-04))
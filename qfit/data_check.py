#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# This module is for creating RC and displays.

__author__ = "Shinjiro Yagyu"
__license__ = "BSD-3-Clause"
__copyright__ = "National Institute for Materials Science, Japan"
__date__ = "2022/09/02"
__version__= "1.0.0"
__revised__ = "2022/09/02"

from pathlib import Path
import sys
import csv

import numpy as np

from PIL import Image
from matplotlib import pyplot as plt

def error(msg):
    "print message 'msg' and exit program"
    print(msg)
    sys.exit(1)


def statistics_info(xs, printf=True):
    
    max_ = np.nanmax(xs)
    min_ = np.nanmin(xs)
    mean_ = np.nanmean(xs)
    median_ = np.nanmedian(xs)
    d_max_min_ = max_-min_
    if printf:
        print(f'max: {max_:.4f}')
        print(f'min: {min_:.4f}')
        print(f'mean: {mean_:.4f}')
        print(f'median: {median_:.4f}')
        # print(f'50 %: {np.percentile(xs,50):.4f}')
        
    return {'max': max_, 'min': min_, 'mean': mean_, 'median': median_, 
            'd_max_min':d_max_min_}


class CheckData:
    # image shape 2240(h) x 2368(w)
    NX = 2368
    NY = 2240

    def __init__(self, dirpath, fmt='.tif'):
        self.data = None
        self.fmt = fmt
        self.dirpath = Path(dirpath)
        self.dark = False 
        self.bg = self.loadfile(self.dirpath.joinpath(f"dark{fmt}")).astype(np.int32)
        self.dark = True
        self.angf()
        self.loaddir()

    def angf(self):
            # angles
        angle_path = self.dirpath / "angle.txt"
        with open(angle_path) as f:
            self.ang2f = {int(x["angle"]): x["filename"] for x in csv.DictReader(f)}

        # key:angle value, value: filename
        # check if assumptions are satisfied
        assert self.ang2f

        for p in self.ang2f.values():
            assert p.endswith(self.fmt)
            q = self.dirpath / p
            assert q.exists()
            assert q.is_file()
        self.xs = sorted(self.ang2f.keys())
        
    def loadfile(self, filepath):
        "loads datafile 'filepath', adjusts to file format based on extension"
        if not filepath.exists():
            error(f"file does not exist: {filepath}")
        if not filepath.is_file():
            error(f"not a file: {filepath}")

        if filepath.suffix == ".tif":
            I = Image.open(filepath)
            data = np.array(I)
            
        elif filepath.suffix == ".img":
            a = np.fromfile(filepath, dtype=np.uint16)
            data = a[5120:].reshape(self.NX, self.NY)
        else:
            raise ValueError(filepath)
        assert data.shape == (self.NX, self.NY)
        data = data.astype(np.int32)
        
        if self.dark:
            data -= self.bg
        return data

    def findmax(self, fmt=None):
        "display information about value distribution"
        npq = np.quantile
        for ang, path in self.ang2f.items():
            data = self.loadfile(self.dirpath / path).reshape(-1)
            print("PATH", path)
            print("  MIN", min(data), "1%", npq(data, 0.01), "10%", npq(data, 0.1))
            print("  25%", npq(data, 0.25), "50%", npq(data, 0.5), "75%", npq(data, 0.75))
            print("  90%", npq(data, 0.9), "99%", npq(data, 0.99), "MAX", max(data))

    def loaddir(self, fmt=None):
        # Dict内包表記（各測定角度に2次元データが入っている）
        alldata = {
            ang: self.loadfile(self.dirpath / path) for ang, path in self.ang2f.items()
            }
        self.data = np.zeros((len(alldata), self.NX, self.NY), dtype=np.int16)
        for i, x in enumerate(self.xs):
            self.data[i, :, :] = alldata[x]
            
    def check_data(self,ix,iy,plot=False):
        if not 0 <= ix < self.NX:
            print(f"illegal x position, (does not satisfy)")
            return 0, 0
        if not 0 <= iy < self.NY:
            print(f"illegal y position, (does not satisfy)")
            return 0, 0
        else:   
            show_data = self.data[:,ix,iy].reshape(-1)
            static_info = statistics_info(show_data, printf=False)
    
            print('-'*5)
            print(f'x: {ix}, y: {iy}')
            print(f'min: {static_info["min"]:.3f}, max: {static_info["max"]:.3f}')
            print(f'mean: {static_info["mean"]:.3f}, median: {static_info["median"]:.3f}')
            print(f'max - min: {static_info["d_max_min"]:.3f}')
            print('')
            
            if plot:
                plt.title(f'x: {ix}, y: {iy}')
                plt.plot(self.xs,show_data,'ro-',label='data')
                plt.xlabel('Angle [arcsec]')
                plt.ylabel('Intensity')
                title_ = f'max-min: {static_info["d_max_min"]:.2f}\nmax :{static_info["max"]}\nmean :{static_info["mean"]:.2f} \nmedian: {static_info["median"]:.2f}'
                plt.legend(title=title_)
                plt.grid(True)
                plt.show()
                
            return self.xs, show_data
                
    def check_data_hist(self,step=100,plot=False):
        data_mean = []
        data_median = []
        data_max = []
        data_min = []
        data_pos = []
        for ix in range(0,self.NX,step):
            for iy in range(0,self.NY,step):
                pos_ = (ix,iy)
                show_data = self.data[:,ix,iy].reshape(-1)
                max_ = np.nanmax(show_data)
                min_ = np.nanmin(show_data)
                median_ = np.nanmedian(show_data)
                mean_ = np.nanmean(show_data)
                data_max.append(max_)
                data_min.append(min_)
                data_median.append(median_)
                data_mean.append(mean_)
                data_pos.append(pos_)
        
        if plot:
            bins = np.linspace(0,100,50)
            # bins=300
            dif_max_min = np.array(data_max) - np.array(data_min)
            dif_max_med = np.array(data_max) - np.array(data_median)
            mm, mmbins = np.histogram(dif_max_min, bins=bins)
            md, mdbins = np.histogram(dif_max_med, bins=bins)

            # print(len(mmdata))
            # print(np.sum(mm),np.sum(mm[5:]),np.sum(mm[:5]))

            fig, (ax1,ax2) = plt.subplots(1,2,figsize=(8.0, 4.0))
            ax1.plot(mmbins[:-1],mm,'bo-',label='Max-Min')
            ax1.plot(mdbins[:-1],md,'r^-',label='Max-Median')
            ax1.set_title('Histgram')
            # ax1.set_ylim(0,100)
            ax1.set_xlim(0,100)
            ax1.set_xlabel("Difference")
            ax1.set_ylabel("number of position")
            ax1.legend()
            ax1.grid()

            # ax2.plot(mdbins[:-1],md,'r^-')
            ax2.plot(dif_max_min,'bo-',label='Max-Min')
            ax2.plot(dif_max_med,'r^-',label='Max-Median')
            ax2.set_title(f'{len(data_max)} Data')
            ax2.set_xlabel("Data Position")
            ax2.set_ylabel("Difference")
            ax2.set_xlim(0,len(data_max))
            ax2.grid()
            fig.tight_layout()
            plt.show()  
                
        return {'max': np.array(data_max), 'min': np.array(data_min), 
                'mean': np.array(data_mean), 'median': np.array(data_median),
                'max_min':np.array(data_max)-np.array(data_min),
                'max_median':np.array(data_max)-np.array(data_median),
                'position':data_pos}

if __name__ == "__main__":
    pass
    # # file_path=r"D:\XrayDataset_for_paper\GaN_n1_4_0"

    # file_path=r""
    # cdata = CheckData(file_path)
    # print(cdata.data.shape)
    
    # # show the RC plot at any positon(x,y)
    # print('Intensity statistic at selected location')
    # for i in [(a,a) for a in range(0, 2100, 100)]:
    #     cdata.check_data(*i,True)
    # cdata_dict= cdata.check_data_hist(plot=True)
    
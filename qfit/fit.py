#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
import argparse
import logging
import csv

from multiprocessing import Pool
from datetime import datetime as dt

import numpy as np
from scipy.optimize import leastsq
from scipy.interpolate import interp1d

from PIL import Image
from matplotlib import pyplot as plt
from matplotlib.colors import Colormap

#import pybeads as be

from pathlib import Path

logger = logging.getLogger(__name__)
VERSION = "1.0.0"
ROOT2 = np.sqrt(2)
HWFACTOR = 2 * np.sqrt(2 * np.log(2))
# HWFACTOR = 2.354820
# sigma : standard deviation 
# FWHM = 2 * root(2*ln(2))* sigma(gauss) ~2.35*sigma
# gauss fit -> sigma, FWHM/HWFactor -> neary sigma
# HWFACTOR = 1
DATAFILE = ".rc_merge.npy"
CHECKED_SAMPLE = False


def error(msg):
    "print message 'msg' and exit program"
    print(msg)
    sys.exit(1)


class Data:
    # image shape 2240(h) x 2368(w)
    NX = 2368
    NY = 2240
    PMAX = 30 # for using gaussian fitting

    def __init__(self, dirpath, fmt, cut, dark, ang2f):
        self.data = None
        self.count = 0
        self.dirpath = dirpath
        self.fmt = fmt
        self.cut = cut
        self.ang2f = ang2f
        self.dark = False
        self.bg = self.loadfile(dirpath.joinpath(f"dark{fmt}")).astype(np.int32)
        self.dark = dark
        self.xs = sorted(ang2f.keys())

    def loadfile(self, filepath):
        "loads datafile 'filepath', adjusts to file format based on extension"
        if not filepath.exists():
            error(f"file does not exist: {filepath}")
        if not filepath.is_file():
            error(f"not a file: {filepath}")
        logger.info(f"open file {filepath}")
        if filepath.suffix == ".tif":
            logger.info("dataformat: tif")
            I = Image.open(filepath)
            data = np.array(I)
        elif filepath.suffix == ".img":
            logger.info("dataformat: img")
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
        "loads all files in angle.txt"
        p = self.dirpath.joinpath(DATAFILE)
        if p.exists():
            self.data = np.fromfile(p, dtype=np.int16).reshape(
                len(self.xs), self.NX, self.NY
            )
            return

        alldata = {
            ang: self.loadfile(self.dirpath / path) for ang, path in self.ang2f.items()
        }
        self.data = np.zeros((len(alldata), self.NX, self.NY), dtype=np.int16)
        for i, x in enumerate(self.xs):
            self.data[i, :, :] = alldata[x]
            
        # save file
        # self.data.tofile(p)

    #@staticmethod
    #def cog(xs, ys):
    #    "calculate peak, stddev using center of gravity"
    #    cg = np.sum(xs * ys) / np.sum(ys)
    #    vpd = ys * (xs - cg) * (xs - cg)
    #    vp2 = np.sqrt(np.sum(vpd) / np.sum(ys)) / (2 * np.pi)
    #    return cg, vp2

    #  Original
    # @staticmethod
    # def hw(xs, ys):
    #     "calculate peak, stddev using max and width at halfmax "

    #     center = xs[np.argmax(ys)]  # uses first max value as center
    #     # print(np.max(yys))
    #     # print(ys.shape,yys.shape)
        
    #     big = np.where(ys > np.max(ys) / 2) #if value is noise level, no index list.
    #     # if len(big) == 0:
    #     #     return 0, 0
    #     # yhalf_ind = big[0]
    #     # if len(yhalf_ind) == 0:
    #     #     return 0, 0
    #     # fwhm = np.abs(xs[yhalf_ind.max()] - xs[yhalf_ind.min()])
        
    #     if len(big) == 0:
    #         return 0, 0
    #     yhalf_ind = big[0]
    #     if len(yhalf_ind) == 0:
    #         return 0, 0
    #     fwhm = xs[max(yhalf_ind)] - xs[min(yhalf_ind)]
        
        
    #     # print(f'c:{int(center)},fwhm:{fwhm:.2f}')
        
    #     return center, fwhm / HWFACTOR
    
    # New version of crosspoint search
    # It uses linear interpolation.
    # Reason why FWHM can only take discrete values by HW method:
    # The value to be obtained is larger than half of the maximum value and the closest value because the measurement interval is every 5 arcsec.
    
    @staticmethod
    def hw(xs,ys):
        
        center = xs[np.argmax(ys)]  # uses first max value as center
        big = np.where(ys > ys.max() / 2) #if value is noise level, no index list.
        if len(big) == 0:
            return 0, 0
        yhalf_ind = big[0]
        if len(yhalf_ind) == 0:
            return 0, 0
        try:
            fx = interp1d(xs, ys, fill_value="extrapolate")
            low_ind = yhalf_ind.min() - 2
            high_ind = yhalf_ind.max() + 2
            xr = np.linspace(xs[low_ind], xs[high_ind], (len(yhalf_ind)+4)*10)
            yr = fx(xr)
            center_x = xr[np.argmax(yr)]  # uses first max value as center
            big_x = np.where(yr >= yr.max() / 2)[0] #if value is noise level, no index list.
            if len(big_x) == 0:
                return 0, 0
            fwhm_x = xr[big_x.max()] - xr[big_x.min()]
            
        except:
            # return np.nan, np.nan
            return 0, 0
        
        # print(center_x, fwhm_x )
   
        return center_x, fwhm_x / HWFACTOR

    #@staticmethod
    #def nbeads(ys, n):
    #    "calls pybeads library to determine base signal, constants are taken from tutorial"
    #    fc = 0.006
    #    d = 1
    #    r = 6
    #    amp = 0.8
    #    lam0 = 0.5 * amp
    #    lam1 = 5 * amp
    #    lam2 = 4 * amp
    #    Nit = 15
    #    pen = "L1_v1"
    #
    #    ny = len(ys)
    #    nys = np.array((2 * n + 1) * list(ys))
    #    nsignal_est, nbg_est, cost = be.beads(
    #        nys, d, fc, r, Nit, lam0, lam1, lam2, pen, conv=None
    #    )
    #    signal_est = nsignal_est[n * ny : (n + 1) * ny]
    #    bg_est = nbg_est[n * ny : (n + 1) * ny]
    #    return signal_est, bg_est

    def fits(self, args):
        "wrapper function for multiple fittings"
        self.loaddir()
        ret = [self.fit(arg) for arg in args]
        print(f"finishing {os.getpid()}\n")
        return ret

    def fit(self, args):
        "wrapper function for all fitting methods"
        x, y, method, options, show = args
        if self.count == 0:
            msg = f"starting {os.getpid()}\n"
        elif self.count % 100 == 0:
            msg = "."
        else:
            msg = ""
        if msg:
            print(msg, end="", flush=True)
        self.count += 1
        ret, ret2, ret3, ret4, ret5 = None, None, None, None, None
        ys = self.data[:, x, y]
        # print(ys.dtype)
        if self.cut is not None:
            ys = np.where(ys > self.cut, np.nan, ys)
        xs = np.array(self.xs)
        if options["filter"] > 0 and max(ys) - min(ys) < options["filter"]:
            return x, y, [0, 0, 0, 0], -1, ys
            # return x, y, [np.nan, np.nan, np.nan, np.nan], -1, ys

        def model(xs, coeffs):
            return coeffs[0] + coeffs[1] * np.exp(
                -(((xs - coeffs[2]) / (ROOT2 * coeffs[3])) ** 2)
            )

        def residuals(coeffs, y, xs):
            y0 = np.where(np.isnan(y), 0, y)
            return y0 - model(xs, coeffs)

        if method == "gaussian" or method == "all":
            t = np.arange(len(xs))
            ymax = np.max(ys)
            yavg = np.median(ys)

            if ymax > yavg + self.PMAX:
                a = np.array(
                    [i for (i, x) in zip(xs, ys) if x > yavg + (ymax - yavg) * 0.9]
                )
                center = np.mean(a)
                wid = 10
                x0 = np.array([yavg, ymax, center, wid], dtype=float)
                x1, flag = leastsq(residuals, x0, args=(ys, xs), maxfev=5000)
                logger.info(f"{x} {y} {flag}")
                ret = x, y, x1, flag, ys
                logger.info(f"GAUSS {x1[2]} {x1[3]} OS {x1[0]} {x1[1]}")
                yy = ys - x1[0]
                y0 = np.abs(np.sum(yy * (xs - x1[2]) ** 2))
                y1 = np.sum(yy)
                logger.info(f"NAIVE_WIDTH {np.sqrt(y0 / y1)}")
            else:
                ret = x, y, [0, 0, 0, 0], 0, ys
                # ret = x, y, [np.nan, np.nan, np.nan, np.nan], 0, ys
                
            if ret[3] == 0 and ymax > yavg + self.PMAX:
                print(
                    "MIN",
                    min(ys),
                    "1%",
                    np.quantile(ys, 0.01),
                    "10%",
                    np.quantile(ys, 0.1),
                    "25%",
                    np.quantile(ys, 0.25),
                    "50%",
                    np.quantile(ys, 0.5),
                    "75%",
                    np.quantile(ys, 0.75),
                    "90%",
                    np.quantile(ys, 0.9),
                    "99%",
                    np.quantile(ys, 0.99),
                    "MAX",
                    max(ys),
                )
                plt.plot(ys)
                plt.show()
        #if method == "bcog" or method == "all":
        #    signal_est, bg_est = self.nbeads(ys, options.get("margin", 3))
        #    offset = np.mean(bg_est)
        #    scale = max(signal_est)
        #    center, width = self.cog(xs, signal_est)
        #    logger.info(f"BCOG {center} {width} OFF {offset} {scale}")
        #    ret2 = x, y, [offset, scale, center, width], 1, ys

        #if method == "cog" or method == "all":
        #    offset = min(ys)
        #    signal_est = ys - offset
        #    scale = max(signal_est)
        #    center, width = self.cog(xs, signal_est)
        #    logger.info(f"COG {center} {width} OFF {offset} {scale}")
        #    ret3 = x, y, [offset, scale, center, width], 1, ys

        #if method == "bhw" or method == "all":
        #    signal_est, bg_est = self.nbeads(ys, options.get("margin", 3))
        #    offset = np.mean(bg_est)
        #    scale = max(signal_est)
        #    center, width = self.hw(xs, signal_est)
        #    logger.info(f"BHW {center} {width} OFF {offset} {scale}")
        #    if width == 0:
        #        ret4 = x, y, [offset, scale, center, width], -1, ys
        #    else:
        #        ret4 = x, y, [offset, scale, center, width], 1, ys

        # revise
        # if method == "hw" or method == "all":
        #     ys=np.array(ys)
        #     select = np.where(ys<3000)
        #     xxs = xs[select[0]]
        #     yys = ys[select[0]]
        #     offset = yys.min()
        #     signal_est = yys - offset
        #     scale = max(signal_est)
        #     center, width = self.hw(xxs, signal_est)
        #     logger.info(f"HW {center} {width} OFF {offset} {scale}")
        #     if width == 0:
        #         ret5 = x, y, [offset, scale, center, width], -1, ys
        #     else:
        #         ret5 = x, y, [offset, scale, center, width], 1, ys
                
        if method == "hw" or method == "all":
            offset = min(ys)
            signal_est = ys - offset
            scale = max(signal_est)
            center, width = self.hw(xs, signal_est)
            logger.info(f"HW {center} {width} OFF {offset} {scale}")
            if width == 0:
                ret5 = x, y, [offset, scale, center, width], -1, ys
            else:
                ret5 = x, y, [offset, scale, center, width], 1, ys


        if show:
            plt.plot(xs, ys, "b-", label="original")
            if ret:
                m = model(xs, ret[2])
                plt.plot(xs, m, "g-", label="gaussian")
            #if ret2:
            #    m = model(xs, ret2[2])
            #    plt.plot(xs, m, "y-", label="bcog")
            #if ret3:
            #    m = model(xs, ret3[2])
            #    plt.plot(xs, m, "yo", label="cog")
            #if ret4:
            #    m = model(xs, ret4[2])
            #    plt.plot(xs, m, "r-", label="bhw")
            if ret5:
                m = model(xs, ret5[2])
                plt.plot(xs, m, "ro", label="hw")

            plt.legend()

            plt.show()
        #ret = [r for r in [ret, ret2, ret3, ret4, ret5] if r is not None][0]
        ret = [r for r in [ret, ret5] if r is not None][0]        
        # print("RET",ret[:-1], ret[-1][:5])
        return ret


def main():
    # commandline options
    parser = argparse.ArgumentParser()
    parser.add_argument("data", help="path to data directory", type=Path)
    parser.add_argument("method", help="fitting method",
        #choices=("gaussian", "cog", "bcog", "hw", "bhw", "all"),
        choices=("gaussian", "hw", "all") )
    parser.add_argument("--fmt", "-f", help="image data format", choices=("img", "tif"),
        default="img")
    #parser.add_argument(
    #    "--margin", "-m", help="add [margin] copies as margin on each side", type=int)
    parser.add_argument("--xpos", "-x", help="x position", type=int)
    parser.add_argument("--ypos", "-y", help="y position", type=int)
    parser.add_argument("--nx", help="number of x pixels (width=NX)", type=int)
    # If peak hight< + peak hight average +pmax then  fitting values nan 
    parser.add_argument("--ny", help="number of y pixels (Height=NY)", type=int)
    parser.add_argument("--pmax", help="PMAX for only use gaussian fitting", type=int)
    parser.add_argument(
        "--background", "-b", help="subtract background", action="store_true")
    parser.add_argument("--show", "-s", help="show graph", action="store_true")
    parser.add_argument("--showonly", help="only show graph", action="store_true")
    parser.add_argument(
        "--pool", "-n", help="number of cpus to use", default=1, type=int)
    parser.add_argument("--logpath", "-l", help="reroute output to logfile", type=Path)
    parser.add_argument("--outpath", "-o", help="npy data path basename")
    parser.add_argument("--findmax", help="max for each data file", action="store_true")
    parser.add_argument("--cut", help="replace values > threshold by nan", type=float)
    parser.add_argument(
        "--debug", "-d", help="output debug information", action="store_true")
    parser.add_argument(
        "--verbose", "-v", help="more verbose output", action="store_true")
    # If the difference of the intensity of (max-min) is less than options["filter"], then the fitting value is nan.
    parser.add_argument(
        "--filter", help="filter signals by minmax difference", type=float, default=0.0)
    args = parser.parse_args()

    args.fmt = "." + args.fmt

    # angles
    with open(args.data / "angle.txt") as f:
        ang2f = {int(x["angle"]): x["filename"] for x in csv.DictReader(f)}

    # check if assumptions are satisfied
    assert ang2f

    for p in ang2f.values():
        assert p.endswith(args.fmt)
        q = args.data / p
        assert q.exists()
        assert q.is_file()
    s = sorted(ang2f.keys())

    diffs = [x - y for (x, y) in zip(s[1:], s[:-1])]
    for d, val in zip(diffs, s):
        if diffs.count(d) < len(diffs) // 2:
            print("uncommon gap at", val)


    # logging
    loglevel = logging.WARNING
    if args.verbose:
        loglevel = logging.INFO
    if args.debug:
        loglevel = logging.DEBUG
    if args.logpath is None:
        logging.basicConfig(format="%(levelname)s:%(message)s", level=loglevel)
    else:
        logging.basicConfig(
            format="%(levelname)s:%(message)s", filename=args.logpath, level=loglevel
        )
    logging.getLogger().setLevel(loglevel)

    p = args.data.joinpath(DATAFILE)
    if p.exists():
        p.unlink()

    # output
    base = (
        f"{args.method}_{dt.now().strftime('%y%m%d_%H%M%S')}"
        if args.outpath is None
        else args.outpath
    )
    cpath = Path(f"{base}_c.npy")
    hpath = Path(f"{base}_h.npy")
    wpath = Path(f"{base}_w.npy")

    
    # nx,ny
    if args.nx is not None:
        Data.NX = args.nx
    if args.ny is not None:
        Data.NY = args.ny
    if args.pmax is not None:
        Data.PMAX = args.pmax
        
    # data object
    D = Data(args.data, args.fmt, args.cut, args.background, ang2f)



    if args.findmax:
        D.findmax()
        return

    # check args
    if args.xpos is not None:
        assert args.ypos is not None
        if not 0 <= args.xpos < D.NX:
            error(f"illegal x position, (does not satisfy 0 <= {args.xpos} < {D.NX})")

    if args.ypos is not None:
        assert args.xpos is not None
        if not 0 <= args.ypos < D.NY:
            error(f"illegal y position, (does not satisfy 0 <= {args.ypos} < {D.NY})")

    if not args.showonly:
        D.loaddir()

    options = {"filter": args.filter}
    #if args.margin:
    #    options["margin"] = args.margin

    if args.xpos:
        xymos = args.xpos, args.ypos, args.method, options, args.show
        D.fit(xymos)

    elif not args.showonly:
        # make (D.NX,D.NY) np.nan array
        D.data = None
        H = np.zeros((D.NX, D.NY), dtype=np.float32) + np.nan
        C = np.zeros((D.NX, D.NY), dtype=np.float32) + np.nan
        W = np.zeros((D.NX, D.NY), dtype=np.float32) + np.nan

        now = dt.now()
        vs = []
        for n in range(args.pool):
            vs.append([])

        idx = 0
        for xx in range(D.NX):
            for y in range(D.NY):
                vs[idx].append((xx, y, args.method, options, False))
                idx = (idx + 1) % args.pool
        with Pool(args.pool) as pool:
            fits = pool.map(D.fits, vs)

        ns = 0
        ng = 0
        for rets in fits:
            for ret in rets:
                # print(ret)
                x, y, x1, flag, _ = ret
                if flag == 1:
                    # print(x1,"H",x1[1],"C",x1[2]/100,"W",x1[3])
                    H[x, y] = x1[1]
                    C[x, y] = x1[2]
                    W[x, y] = x1[3]
                    ng += 1
                if flag == -1:
                    ns += 1
        print(f"skipped: {ns} good: {ng}")
        print(str(cpath))

        C.tofile(cpath)
        H.tofile(hpath)
        W.tofile(wpath)

    if not args.xpos and args.show:
        import matplotlib.pyplot as plt
        from mpl_toolkits.axes_grid1 import make_axes_locatable

        dpath = f"c_{args.method}.npy"
        dtype = np.float32

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
        fig.suptitle(base)
        axs = [ax1, ax2, ax3, ax4]

        for c, path, ax in zip("chwx", (cpath, hpath, wpath, wpath), axs):
            cmap = "gist_rainbow_r"
            vmin, vmax = {
                "w": [0, 5000],
                "h": [0, 2500],
                "c": [-5500, -1750],
                "x": [1200, 2400],
            }[c]

            data = np.fromfile(path, dtype=dtype).reshape(2368, 2240)
            # im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
            im = ax.imshow(data, cmap=cmap)

            divider = make_axes_locatable(ax)
            title = {"w": "WIDTH", "h": "HEIGHT", "c": "CENTER", "x": "WIDTH"}[c]
            cax = divider.append_axes("right", size="3%", pad=0.12, title=title)
            fig.colorbar(im, cax=cax, orientation="vertical")

        plt.savefig(f"{base}_summary.png", dpi=300)
        plt.show()


if __name__ == "__main__":
    main()

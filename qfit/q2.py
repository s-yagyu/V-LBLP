# -*- coding: utf-8 -*-
# "left-handed coordinate system"

import argparse
import logging

import numpy as np
from scipy.ndimage import rotate

def R(x,y,z,a):
    SA = np.sin(a)
    CA = np.cos(a)
    CCA = 1-np.cos(a)
    rot = np.zeros((len(a),3,3),dtype=np.float32)
    rot[:,0,0] = CA + x * x * CCA
    rot[:,1,0] = y * x * CCA + z * SA
    rot[:,2,0] = z * x * CCA - y * SA
    rot[:,0,1] = x * y * CCA - z * SA
    rot[:,1,1] = CA + y * y * CCA
    rot[:,2,1] = z * y * CCA + x * SA
    rot[:,0,2] = x * z * CCA + y * SA
    rot[:,1,2] = y * z * CCA - x * SA
    rot[:,2,2] = CA + z * z * CCA
    return rot


class Data:
    # image.shape: h,w = 2240(NY) x 2368(NX)
    NX = 2368
    NY = 2240
    ANGLE_t = 0
    ANGLE_c = 120

    def __init__(self, theta, chi, show=False, prefix="", q=1, old=False):
    # def __init__(self, theta, chi, show=False, prefix="", q=1, old=True):
        self.theta = theta
        self.chi = chi
        self.q = q

        self.load()
        if old:
            print("OLD")
            self.calc_old()
        else:
            print("NEW")
            self.calc()
        self.dump(show=show, prefix=prefix)

    def load(self):
        "load theta and chi data and normalize (mean 0)"
        logging.debug("start loading data")
        self.tdata = np.fromfile(self.theta,dtype=np.float32)
        self.cdata = np.fromfile(self.chi,dtype=np.float32)
        self.tavg = np.mean(self.tdata[~np.isnan(self.tdata)])
        self.cavg = np.mean(self.cdata[~np.isnan(self.cdata)])
        self.tdel = (self.tdata - self.tavg) * (np.pi/180) * (1/3600) # Convert arcsec to radians 
        self.cdel = (self.cdata - self.cavg) * (np.pi/180) * (1/3600)

    def calc_old(self):
        "simplified matrix calculation (not used currently)"
        logging.debug("start calculating")
        "rotate (0,0,1), see Kim2018_Appl._Phys._Express_11_081002.pdf eqs. (1) and (2)"
        ST = np.sin(self.tdel)
        CT = np.cos(self.tdel)
        SC = np.sin(self.cdel)
        CC = np.cos(self.cdel)
        X = 2000000
        print(ST[X],CT[X],SC[X],CC[X])
        self.qx = ST * (3/4 + 1/4 * CC) - 1/2 * SC * CT
        self.qy = -np.sqrt(3)/4 * ((1 - CC) * ST + 2 * CT * SC)
        self.qz = 1/2 * SC * ST + CC * CT
        self.qx *= self.q
        self.qy *= self.q
        self.qz *= self.q
        print(self.qx[X],self.qy[X],self.qz[X])

    def calc(self):
        "matrix calculations, which can be easily generalized to other angles"
        "left-handed coordinate system"
        # if Data.ANGLE == 120:
        #     rot_t = R(0,1,0,self.tdel)
        #     rot_c = R(np.sqrt(3)/2,-.5,0,self.cdel) 

        # elif Data.ANGLE == -120:
        #     rot_t = R(0,1,0,self.tdel)
        #     rot_c = R(-np.sqrt(3)/2,-.5,0,self.cdel)

        # elif Data.ANGLE == 90:
        #     rot_t = R(0,1,0,self.tdel)
        #     rot_c = R(1,0,0,self.cdel)

        # elif Data.ANGLE == -90:
        #     rot_t = R(0,1,0,self.tdel)
        #     rot_c = R(-1,0,0,self.cdel)

        # elif Data.ANGLE == 120120:
        #     # special case t=120deg form 0deg, c=-120 from 0deg
        #     rot_t = R(np.sqrt(3)/2,-.5,0,self.tdel)
        #     rot_c = R(-np.sqrt(3)/2,-.5,0,self.cdel)
            
        # else:
        #     rot_t = R(0,1,0,self.tdel)
        #     rot_c = R(np.sin(self.ANGLE*np.pi / 180),np.cos(self.ANGLE*np.pi / 180),0,self.cdel)

        rot_t = R(np.sin(self.ANGLE_t*np.pi / 180),np.cos(self.ANGLE_t*np.pi / 180),0,self.tdel)
        rot_c = R(np.sin(self.ANGLE_c*np.pi / 180),np.cos(self.ANGLE_c*np.pi / 180),0,self.cdel)
        print(f'set Angle t:{self.ANGLE_t}, c:{self.ANGLE_c}')    
        # X = 2000000
        #print("T")
        #print(rot_t[X,:,:])
        #print("C")
        #print(rot_c[X,:,:])
        #print("C21",rot_c[X,2,1])
        #print("CT")
        #print(rot_c[X,:,:]@rot_t[X,:,:])
        c = (rot_c @ rot_t) @ np.array([0,0,self.q],dtype=np.float32)
        # c = (rot_t @ rot_c) @ np.array([0,0,self.q],dtype=np.float32)
        #print(c[X,:])
        #print((rot_c[X,:,:]@rot_t[X,:,:]) @ np.array([0,0,self.q],dtype=np.float32).reshape((3,1)))
        #print(rot_c[X,:,:]@(rot_t[X,:,:] @ np.array([0,0,self.q],dtype=np.float32).reshape((3,1))))
        #print(c.dtype)
        self.qx = c[:,0].reshape(self.NX,self.NY)
        self.qy = c[:,1].reshape(self.NX,self.NY)
        self.qz = c[:,2].reshape(self.NX,self.NY)


    def show(self, path, prefix):
        "display heat maps, histogram and vector fields (quivers)"
        import matplotlib.pyplot as plt
        from mpl_toolkits.axes_grid1 import make_axes_locatable
        plt.rcParams["font.size"] = 6

        dtype = np.float32

        fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3)
        fig.suptitle(prefix.upper())
        axs = [ax1,ax2,ax3,ax4,ax5,ax6]
        for c,col in zip("xyzavw",axs):
            cmap = "gist_rainbow_r"
            if c in "xyz":
                p = path[:-5] + c + ".npy"
                data = np.fromfile(p, dtype=dtype).reshape(Data.NX,Data.NY)
            else:
                p = path[:-5] + "x.npy"
                xdata = np.fromfile(p, dtype=dtype).reshape(Data.NX,Data.NY)
                p = path[:-5] + "y.npy"
                ydata = np.fromfile(p, dtype=dtype).reshape(Data.NX,Data.NY)
                p = path[:-5] + "z.npy"
                zdata = np.fromfile(p, dtype=dtype).reshape(Data.NX,Data.NY)

                data = np.hypot(xdata, ydata)
                xyzdata = np.rad2deg(np.arctan(data/np.abs(zdata)))
                # xyzdata = np.where(np.isnan(xyzdata), np.abs(np.random.normal(0.035, 0.015, size=xyzdata.shape)), xyzdata)
            if c in "axy":
                # im = col.imshow(data, cmap=cmap, vmin=-0.2, vmax=0.2)
                im = col.imshow(data, cmap=cmap)
            elif c == "z":
                # im = col.imshow(data, cmap=cmap, vmin=0.99999, vmax=1.000)
                im = col.imshow(data, cmap=cmap)
            elif c == "v":
                xdata = xdata[::50,::50]
                ydata = ydata[::50,::50]
                col.invert_yaxis()
                col.quiver(xdata,-ydata)
                col.set_aspect('equal')
            else:
                # im = col.imshow(xyzdata, cmap=cmap)
                xyzdata = xyzdata.reshape(-1)
                xyzdata = xyzdata[~np.isnan(xyzdata)]
                col.hist(xyzdata, bins=100, density=True)
                col.set_xlim(0, 0.15)
                # col.hist(xyzdata.reshape(-1), bins=25, density=True)
            divider = make_axes_locatable(col)
            if c in "axyz":
                cax = divider.append_axes('right', size='5%', pad=0.06, title=("Q"+c.upper() if c != "w" else "|QX+QY|/|QZ|"))
                fig.colorbar(im, cax=cax, orientation='vertical')
                
        plt.tight_layout()
        plt.savefig(f"{prefix}_f.png",dpi=300)
        print(f"{prefix}_f.png")
        plt.show()

    def dump(self, prefix="vdata", show=False):
        "save rotated unit vectors to one file per coordinate"

        logging.debug(f"writing data to {prefix}_x.npy")
        self.qx.tofile(f"{prefix}_x.npy")
        logging.debug(f"writing data to {prefix}_y.npy")
        self.qy.tofile(f"{prefix}_y.npy")
        logging.debug(f"writing data to {prefix}_z.npy")
        self.qz.tofile(f"{prefix}_z.npy")
        # print(f"{prefix}_x.npy")

        if show:
            self.show(f"{prefix}_x.npy", prefix=prefix)


def main():
    # commandline options
    parser = argparse.ArgumentParser()

    parser.add_argument("--nx", help="number of x pixels; width", type=int)
    parser.add_argument("--ny", help="number of y pixels; height", type=int)
    parser.add_argument("--anglet", help="t angle[deg]: 0, 120, -120, 90, -90 or int", type=int)
    parser.add_argument("--anglec", help="c angle[deg]: 120, -120, 90, -90 or int", type=int)
    
    parser.add_argument("--dtheta", "-t", help="data file with delta theta data [arcsec]")
    parser.add_argument("--dchi", "-c", help="data file with delta chi data [arcsec]")
    parser.add_argument("-q", help="set q unit:Angstrom^-1", default="1.0", type=float)
	# q-vector of GaN (112¯4) for which the length equals 6.258 Å−1 (= 2π/d112¯4)

    parser.add_argument("--prefix", "-p", help="prefix for output images", default="vdata")
    parser.add_argument("--logpath", "-l", help="reroute output to logfile")
    parser.add_argument("--debug", "-d", help="output debug information", action="store_true")
    parser.add_argument("--verbose", "-v", help="more verbose output", action="store_true")
    parser.add_argument("--show", "-s", help="show graph", action="store_true")
    parser.add_argument("--old", help="old calc method", action="store_true")
    args = parser.parse_args()

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

    # nx,ny
    # h, w =image.shape -> 2368(H):NY, 2240(W):NX 
    
    if args.nx is not None:
        Data.NX = args.nx
    if args.ny is not None:
        Data.NY = args.ny
    if args.anglet is not None:
        Data.ANGLE_t = args.anglet
    if args.anglec is not None:
        Data.ANGLE_c = args.anglec

    # print(Data.NX,Data.NY,Data.ANGLE_t,Data.ANGLE_c)

    D = Data(args.dtheta,args.dchi,show=args.show, prefix=args.prefix, q=args.q, old=args.old)
    


if __name__ == "__main__":
    main()

import argparse
from pathlib import Path
import numpy as np
import cv2
import tifffile as tiff
from datetime import datetime as dt
from util.affine_transform import AffineTransform


def main(args):
    afftrans(args.data, args.px, args.py, args.rz, args.sx, args.sy)


def afftrans(data, px, py, rz, sx, sy):
    src_dir = Path(data)
    now = dt.now().isoformat().replace(":","_")
    output_dir = Path(data + f"_transform_P{px}_{py}_R{rz}_S{sx}_{sy}_{now}")
    output_dir.mkdir(exist_ok=True)
    transform = AffineTransform()
    transform.set_position(px, py)
    transform.set_rotation_radian(rz)
    transform.set_scale(sx, sy)
    files = list(src_dir.glob("*.tif"))
    if not files:
        return
    im = tiff.imread(files[0])
    h, w = im.shape
    transform.set_origin(w // 2, h // 2)
    M = transform.M()

    for f in files:
        im = tiff.imread(f)
        h, w = im.shape
        dst = cv2.warpAffine(im, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        tiff.imwrite(output_dir / f.name, dst, compression=None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Affine Transformer")
    parser.add_argument("data", help="data folder")
    parser.add_argument("px", help="", type=int)
    parser.add_argument("py", help="", type=int)
    parser.add_argument("rz", help="", type=int)
    parser.add_argument("sx", help="", type=float)
    parser.add_argument("sy", help="", type=float)

    args = parser.parse_args()
    main(args)

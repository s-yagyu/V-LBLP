import argparse
from pathlib import Path
import numpy as np
import cv2
import tifffile as tiff

from util.editor import Editor
from util.affine_transform import AffineTransform


def main(args):
    input_file = Path(args.input)
    output_dir = Path(args.output)
    editor = Editor(None)
    dict_data = editor.unpack_dict_from_file(input_file)
    dict_src = dict_data["folders"]["rotated"]
    src_dir = Path(dict_src["path"])
    print(src_dir)

    p = dict_src["params"]
    print(p)
    transform = AffineTransform()
    transform.set_position(p["px"], p["py"])
    transform.set_rotation_radian(p["rz"])
    transform.set_scale(p["sx"], p["sy"])
    transform.set_origin(p["ox"], p["oy"])
    M = transform.M()

    file_list = list(src_dir.glob("*.tif"))
    file_list = [f for f in file_list if "dark" not in f.stem]
    file_list = sorted(
        file_list,
        key=lambda x: int(x.stem),
        reverse=True
    )
    dark_file_list = list(src_dir.glob("*dark.tif"))
    file_list.append(dark_file_list[0])
    # file_list = [file_list[0]]
    print(file_list)

    for f in file_list:
        im = tiff.imread(f)
        h, w = im.shape
        dst = cv2.warpAffine(im, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
        tiff.imwrite(output_dir / f.name, dst, compression=None)
        # cv2.imwrite(str(output_dir / f.name), dst)


def test(args):
    input_file = Path(args.input)
    output_dir = Path(args.output)
    editor = Editor(None)
    dict_data = editor.unpack_dict_from_file(input_file)
    dict_src = dict_data["folders"]["rotated"]
    src_dir = Path(dict_src["path"])
    print(src_dir)

    p = dict_src["params"]
    print(p)
    transform = AffineTransform()
    transform.set_position(p["px"], p["py"])
    transform.set_rotation_radian(p["rz"])
    transform.set_scale(p["sx"], p["sy"])
    transform.set_origin(p["ox"], p["oy"])
    M = transform.M()
    src_array = dict_src["raw_img"]
    cv2.imwrite(str(output_dir / "base.png"), dict_data["folders"]["base"]["raw_img"]*65535)
    cv2.imwrite(str(output_dir / "rotated.png"), src_array*65535)
    h, w = src_array.shape
    dst = cv2.warpAffine(src_array, M, (w, h))
    print(dst)
    cv2.imwrite(str(output_dir / "rotated_t.png"), dst*65535)


def write(args):
    input_file = Path(args.input)
    output_dir = Path(args.output)
    editor = Editor(None)
    dict_data = editor.unpack_dict_from_file(input_file)
    dict_src = dict_data["folders"]["rotated"]
    src_dir = Path(dict_src["path"])
    print(src_dir)

    p = dict_src["params"]
    print(p)
    transform = AffineTransform()
    transform.set_position(p["px"], p["py"])
    transform.set_rotation_radian(p["rz"])
    transform.set_scale(p["sx"], p["sy"])
    transform.set_origin(p["ox"], p["oy"])
    M = transform.M()
    src_array = dict_src["raw_img"]
    np.save(str(output_dir / "base.npy"), dict_data["folders"]["base"]["raw_img"])
    np.save(str(output_dir / "rotated.npy"), src_array)
    h, w = src_array.shape
    dst = cv2.warpAffine(src_array, M, (w, h))
    print(dst)
    np.save(str(output_dir / "rotated_transformed.npy"), dst)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Affine Transformer"
    )
    parser.add_argument("input", help="Input file (*.atp)")
    parser.add_argument("output", help="Output directory")
    args = parser.parse_args()

    # main(args)
    write(args)

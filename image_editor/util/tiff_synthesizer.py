import numpy as np
import matplotlib.pyplot as plt
import tifffile as tiff
import cv2
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker

def calc_sum(dark, files, step, spike_threshold=64000):
    if dark:
        d = tiff.imread(dark[0])
    else:
        d = 0
    s = None
    for i in range(0, len(files), step):
        print(i)
        im = tiff.imread(files[i])
        if im is None:
            print(f"Cannot read {files[i]}")
            return None
        im = np.where(im > spike_threshold, np.nan, im)
        mean = np.nanmean(im)
        im = np.nan_to_num(im, mean)
        if s is None:
            s = np.zeros(im.shape)
        s += im - d
    return s

class TiffSynthesizer:
    def __init__(self, folder_path: str):
        self.set_folder_path(folder_path)

    def set_folder_path(self, folder_path: str):
        self.path = Path(folder_path)
        file_list = list(self.path.glob("*.tif"))
        file_list = [f for f in file_list if "dark" not in f.stem]
        self.file_list = sorted(
            file_list,
            key=lambda x: int(x.stem),
            reverse=True
        )
        self.dark_file_list = list(self.path.glob("*dark.tif"))
        # print(f'number of files without dark file: {len(self.file_list)}')
        # print(f'number of dark files: {len(self.dark_file_list)}')

    def get_sum(
            self,
            spike_threshold=64000,
            step=1,
            plot=False):
        sum = calc_sum(self.dark_file_list, self.file_list, step, spike_threshold)
        sum = np.clip(sum, 0.0, None)
        self.sum = sum / np.linalg.norm(sum)
        if plot:
            plt.figure(figsize=(10, 10))
            plt.imshow(self.sum)
            plt.colorbar()
            plt.show()

        return self.sum

    @staticmethod
    def plot_enhanced_image(arr, low_int):
        """
        Histgramによる強度分布を参考に、指定する強度以上のものだけを集めて表示する。
        """
        # binary data
        temp_data = arr > low_int
        plt.figure(figsize=(10, 10))
        plt.imshow(temp_data)
        plt.show()

    @staticmethod
    def get_sum_arr(
            folder_path: str,
            spike_threshold: int = 64000,
            step: int = 1
            ):
        path = Path(folder_path)
        file_list = list(path.glob("*.tif"))
        file_list = [f for f in file_list if "dark" not in f.stem]
        file_list = sorted(
            file_list,
            key=lambda x: int("".join([y for y in x.stem if y in "0123456789"])),
            reverse=True
        )
        dark_file_list = list(path.glob("*dark.tif"))
                
        # 正規化
        sum = calc_sum(dark_file_list, file_list, step, spike_threshold)        
        sum = np.clip(sum, 0.0, None) / np.linalg.norm(sum)
        return sum

    # FIXME: 高速化が必要
    @staticmethod
    def binarize(src_image: np.ndarray) -> np.ndarray:
        """
        src_image はグレースケールの2次元配列。
        threshold より大きいピクセルを r, g, b, a で指定した色に
        それ以外のピクセルを r = g = b = a = 0 に着色した
        uint8 の3次元配列を返す。
        """
        def round_int(x): return np.round((x * 2 + 1) // 2)
        gaus = cv2.GaussianBlur(src_image, (13, 13), 0)
        gaus = gaus * 65535 / gaus.max()
        gaus_ui16 = round_int(gaus).astype(np.uint16)
        ret, otsu = cv2.threshold(gaus_ui16, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return otsu.astype(np.uint8)


class TiffSynthWorker(QObject):
    finished = pyqtSignal()
    updated = pyqtSignal(int)
    aborted = pyqtSignal()
    synthesized = pyqtSignal(np.ndarray)
    error_occured = pyqtSignal(str)

    def __init__(
            self,
            folder_path: str,
            spike_threshold: int = 64000,
            step: int = 1
            ):
        super().__init__()
        self.path = Path(folder_path)
        self.spike_threshold = spike_threshold
        self.step = step

        self.mutex = QMutex()
        self.synth_image = None
        self.is_running = False

    # TODO: エラー処理を記述する
    def run(self):
        print("piyo")
        self.is_running = True

        file_list = list(self.path.glob("*.tif"))
        log = self.path / "output.log"
        if log.exists():
            with open(log) as f:
                for x in f:
                    if "dark" in x.lower():
                        n = int(x.strip().split()[-1])
                        file_list.sort()
                        dark_file_list = file_list[-n:]
                        file_list = file_list[:-n]
                        break
        else:
            file_list = [f for f in file_list if "dark" not in f.stem]
            file_list = sorted(
                file_list,
                key=lambda x: int("".join([y for y in x.stem if y in "0123456789"])),
                reverse=True
            )
            dark_file_list = list(self.path.glob("*dark.tif"))
        num_files = len(file_list)
            
        if file_list == []:
            self.is_running = False
            self.error_occured.emit("CANNOT Find Any TIFF Files")
            return

        #if dark_file_list == []:
        #    self.is_running = False
        #    self.error_occured.emit("CANNOT Find '*dark.tif'")
        #    return
        if dark_file_list == []:
            dark = None
        else:
            dark = tiff.imread(dark_file_list[0])
        #if dark is None:
        #    self.is_running = False
        #    self.error_occured.emit(f"CANNOT Open File: {dark_file_list[0]}")
        #    return
        if dark is not None:
            sum = np.zeros(dark.shape)
        else:
            sum = None
            
        for i in range(0, num_files, self.step):
            if not self.is_running:
                self.aborted.emit()
                return
            im = tiff.imread(file_list[i])
            if im is None:
                self.is_running = False
                self.error_occured.emit(f"CANNOT Open File: {file_list[i]}")
                return
            im = np.where(im > self.spike_threshold, np.nan, im)
            mean = np.nanmean(im)
            im = np.nan_to_num(im, mean)
            if dark is None:
                if sum is None:
                    sum = im[:,:]
                else:
                    sum += im
            else:
                sum += im - dark
            print(f"file_name: {str(file_list[i])}, mean: {str(mean)}")
            self.updated.emit(int(100 * (i+1) / num_files))
        # 正規化
        if not self.is_running:
            self.aborted.emit()
            return
        self.synth_image = np.clip(sum, 0.0, None) / np.linalg.norm(sum)
        self.synthesized.emit(self.synth_image)
        self.finished.emit()
        self.is_running = False

    def stop(self):
        print("CALLED stop")
        with QMutexLocker(self.mutex):
            if self.is_running:
                self.is_running = False


if __name__ == "__main__":
    folder_path = "/prj/xtopo/14_data/20201224/6-inch-120degree/6-inch_120_1/"
    # visualizer = TiffSynthesizer(folder_path)
    # arr = visualizer.get_sum(step=16, plot=True)
    arr = TiffSynthesizer.get_sum_arr(folder_path, step=16)
    print(arr)
    exit()
    val_max = arr.max()
    val_min = arr.min()
    val_med = np.median(arr)
    print(arr.dtype)
    print(f"Max:{val_max}, Min:{val_min}, Median:{val_med}")
    plt.figure()
    plt.hist(arr.flatten(), bins="auto")
    plt.xlim(val_min, val_med*2)
    plt.show()
    TiffSynthesizer.plot_enhanced_image(arr, val_med)

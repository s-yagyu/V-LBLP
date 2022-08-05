import logging
from logging.handlers import RotatingFileHandler
import argparse
import sys
import json
from os import getcwd, listdir, makedirs
from os.path import basename, relpath, isfile, splitext, join
from glob import glob
from pathlib import Path
from time import sleep

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QAction,
    QProgressDialog,
    QFileDialog,
    QInputDialog,
    QGridLayout,
    QWidget,
    QApplication,
    QLabel,
    QMessageBox
)

import numpy as np
import cv2
import tifffile as tiff
from datetime import datetime as dt
from util.affine_transform import AffineTransform

from util.main_window import MainWindow
from atp_editor.atp_editor import ATPEditor
from atp_editor.widgets.main_container import MainContainer

LOGFORM = logging.Formatter(
    "%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s"
)
makedirs("log", exist_ok=True)
LOGFILE = "log/main.log"
LOGSIZE = 1048576
LOGBACK = 2
LOGHAND = RotatingFileHandler(
    LOGFILE, mode="a",
    maxBytes=LOGSIZE,
    backupCount=LOGBACK,
    encoding=None,
    delay=0
)
LOGHAND.setFormatter(LOGFORM)
LOGHAND.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(LOGHAND)


version_str = "version 0.1.0"


class Main(MainWindow):
    def __init__(self, argv):
        super().__init__(argv)

        self.setWindowTitle("Affine Transformation Parameters Editor")
        self.initialize()

    def initialize(self) -> None:
        self.editor = ATPEditor(self)
        self.create_widgets()
        self.create_actions()
        self.layout_widgets()
        self.create_connections()

    def create_widgets(self):
        self.mainContainer = MainContainer(self, self.editor)

    def create_actions(self):
        menubar = self.menuBar()

        # macOS のメニューバーが正しく表示されるように設定する。
        from platform import system
        sysname = system()
        logger.debug("Platform " + sysname)
        if system() == "Darwin":
            menubar.setNativeMenuBar(False)
        del system

        fileMenu = menubar.addMenu("File")
        #editMenu = menubar.addMenu("Edit")
        helpMenu = menubar.addMenu("Help")

        new = QAction("New", self)
        new.setShortcut("Ctrl+N")
        new.setStatusTip("New")
        new.triggered.connect(self.reset_all_windows)

        transform = QAction("Export", self)
        transform.setShortcut("Ctrl+T")
        transform.setStatusTip("Export")
        transform.triggered.connect(self.transform)        

        #openParams = QAction("Open...", self)
        #openParams.setShortcut("Ctrl+O")
        #openParams.setStatusTip("Open A Parameters File")
        #openParams.triggered.connect(self.open_params_file)

        #saveParams = QAction("Save", self)
        #saveParams.setShortcut("Ctrl+S")
        #saveParams.setStatusTip("Save A Parameters File")
        #print(self.save_params_file)
        #saveParams.triggered.connect(self.save_params_file)

        #saveParamsAs = QAction("Save As...", self)
        #saveParamsAs.setShortcut("Ctrl+Shift+S")
        #saveParamsAs.setStatusTip("Save A Parameters File As Name")
        #saveParamsAs.triggered.connect(self.save_params_file_as)

        openBaseImgFolder = QAction("Open Base Images Folder...", self)
        openBaseImgFolder.setStatusTip(
            "Open A Folder Containing Base Image Files")
        openBaseImgFolder.triggered.connect(self.open_images_folder)

        openRotImgFolder = QAction("Open Rotated Images Folder...", self)
        openRotImgFolder.setStatusTip(
            "Open A Folder Containing Rotated Image Files")
        openRotImgFolder.triggered.connect(self.open_rotated_images_folder)

        quitApp = QAction("Quit", self)
        quitApp.setShortcut("Ctrl+Q")
        quitApp.setStatusTip("Quit This Application")
        quitApp.triggered.connect(self.quit_app)

        #Undo = QAction("Undo", self)
        #Undo.setShortcut("Ctrl+Z")
        #Undo.setStatusTip("Undo")
        #Undo.triggered.connect(self.Undo)

        #Redo = QAction("Redo", self)
        #Redo.setShortcuts(["Ctrl+Y", "Ctrl+Shift+Z"])
        #Redo.setStatusTip("Redo")
        #Redo.triggered.connect(self.Redo)

        Shortcuts = QAction("Shortcuts", self)
        Shortcuts.setStatusTip("Shortcuts")
        Shortcuts.triggered.connect(self.shortcuts)

        Mouse = QAction("Mouse", self)
        Mouse.setStatusTip("Mouse")
        Mouse.triggered.connect(self.mouse)

        Wheel = QAction("Wheel", self)
        Wheel.setStatusTip("Wheel")
        Wheel.triggered.connect(self.wheel)                

        fileMenu.addAction(new)
        fileMenu.addAction(transform)        
        fileMenu.addSeparator()
        #fileMenu.addAction(openParams)
        #fileMenu.addSeparator()
        #fileMenu.addAction(saveParams)
        #fileMenu.addAction(saveParamsAs)
        #fileMenu.addSeparator()
        fileMenu.addAction(openBaseImgFolder)
        fileMenu.addAction(openRotImgFolder)
        fileMenu.addSeparator()
        fileMenu.addAction(quitApp)

        #editMenu.addAction(Undo)
        #editMenu.addAction(Redo)

        helpMenu.addAction(Shortcuts)
        helpMenu.addAction(Mouse)
        helpMenu.addAction(Wheel)                

    def shortcuts(self):
        M = QMessageBox()
        M.setWindowTitle("Help")
        M.setText("Short cut keys")
        M.setInformativeText("""Ctrl+N New
    clear all data 
Ctrl+Q Quit
    quit the program immediately (no saves, 
    no questions asked)
Ctrl+T Export
    merge all matching datafiles (using one from 
    each of the four folders) after transforming 
    the images according to the parameters set 
    for each image.""")
        M.exec()

    def mouse(self):
        M = QMessageBox()
        M.setWindowTitle("Help: Mouse")
        M.setText("Mouse clicks")
        M.setInformativeText("""Left click => toggle mesh
Middle click => toggle circle
Right click => fit image in window""")
        M.exec()

    def wheel(self):
        M = QMessageBox()
        M.setWindowTitle("Help: Wheel")
        M.setText("Wheel")
        M.setInformativeText("""No mods
    zoom
Shift
    zoom circle
""")
        M.exec()        

    def open_params_file(self) -> None:
        self._open_file_with_filter("ATP files (*.atp)")

    def open_images_folder(self):
        print("Open Base Images Folder...")
        self.editor.open_folder(
            "base", dialog_message="Open Base Images Folder")

    def open_rotated_images_folder(self):
        print("Open Rotated Images Folder...")
        self.editor.open_folder(
            "rotated", dialog_message="Open Rotated Images Folder")

    def layout_widgets(self):
        self.setCentralWidget(self.mainContainer)

    def transform(self):
        data = self.mainContainer.explorer_container.baseExplorer.ImgFolderLineEdit.text()
        pedit = self.mainContainer.sidebar.paramsEditorB
        px = pedit.pos_sb_x.value()
        py = pedit.pos_sb_y.value()
        rz = pedit.rot_sb.value()
        sx = pedit.scl_sb_x.value()
        sy = pedit.scl_sb_y.value()
        self.afftrans(data,px,py,rz,sx,sy,"base")
        
        data = self.mainContainer.explorer_container.rotatedExplorer.ImgFolderLineEdit.text()
        pedit = self.mainContainer.sidebar.paramsEditorR        
        px = pedit.pos_sb_x.value()
        py = pedit.pos_sb_y.value()
        rz = pedit.rot_sb.value()
        sx = pedit.scl_sb_x.value()
        sy = pedit.scl_sb_y.value()
        self.afftrans(data,px,py,rz,sx,sy,"rotated")

    def cancel(self):
        self.cancelled = True
 
    def afftrans(self, data, px, py, rz, sx, sy, title):
        src_dir = Path(data)
        now = dt.now().isoformat().replace(":","_")
        output_dir = Path(data + f"_transform_P{px}_{py}_R{rz}_S{sx}_{sy}_{now}")
        output_dir.mkdir(exist_ok=True)
        transform = AffineTransform()
        transform.set_position(px, py)
        transform.set_rotation_degree(rz)
        transform.set_scale(sx, sy)
        self.cancelled = False 
        self.synth_progress = QProgressDialog(
            "Progress",
            "Cancel",
            0,
            100,
            self.parent()
            )
        self.synth_progress.setWindowModality(Qt.WindowModal)
        self.synth_progress.setWindowTitle(f"Merging {title}")
        self.synth_progress.setValue(0)
        self.synth_progress.show()
        self.synth_progress.canceled.connect(self.cancel)

        files = list(src_dir.glob("*.tif"))
        if not files:
            return
        im = tiff.imread(files[0])
        h, w = im.shape
        transform.set_origin(w // 2, h // 2)
        M = transform.M()
        n = len(files)
        for i,f in enumerate(files):
            sleep(0.01)
            if self.cancelled:
                break
            self.synth_progress.setValue(((i+1)*100)//n)
            
            print(f)
            im = tiff.imread(f)
            h, w = im.shape
            # dst = cv2.warpAffine(im, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
            # dst = cv2.warpAffine(im, M, (w, h), borderMode=cv2.BORDER_CONSTANT)
            dst = cv2.warpAffine(im, M, (w, h), borderMode=cv2.BORDER_CONSTANT,borderValue=np.nan)
            # cv2.BORDER_CONSTANT: iiiiii|abcdefgh|iiiiiii (default)
            # cv2.BORDER_REPLICATE: aaaaaa|abcdefgh|hhhhhhh
            tiff.imwrite(output_dir / f.name, dst, compression=None)
        self.synth_progress.reset()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Affine Transformation Parameters Editor")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    w = Main(args)
    w.resize(1600, 900)
    w.show()
    sys.exit(app.exec_())

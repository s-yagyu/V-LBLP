import logging
from logging.handlers import RotatingFileHandler
from os import makedirs
from math import sqrt

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QPushButton
)
from PyQt5.QtGui import (
    QPixmap,
    QWheelEvent,
    QKeyEvent,
    QKeySequence,
    QColor,
    QPen,
    QMouseEvent,
    QTransform,
)

from util.editor import Editor

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


class ImageView(QGraphicsView):
    ctrl_wheel = pyqtSignal(int)
    shift_wheel = pyqtSignal(int)

    def __init__(self, parent: QWidget, editor: Editor):
        super().__init__(parent)
        self.editor = editor
        self.dict_items = {}
        self.mesh = []
        self.circ = None
        self.c = 100
        self.xy = 0,0
        #self.center = []
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)

        self.create_widgets()
        self.create_actions()
        self.layout_widgets()
        self.create_connections()

        # FIXME: アフィン変換の動作確認のために原点を表すアイテムを追加してるい

    def add_circ(self):
        x,y = self.xy.x()-self.c//2, self.xy.y()-self.c//2
        R = QPen()
        R.setWidth(6)
        R.setColor(QColor(0,0,0))
        if self.circ is not None:
            self.scene.removeItem(self.circ)
        self.circ = self.scene.addEllipse(x,y,self.c,self.c,R)

    def czoom(self,c):
        self.c = max(0, self.c + c)
        if self.circ is not None:
            self.toggle_circle()
            self.toggle_circle()


    def add_mesh(self, r):
        xmin,xmax,ymin,ymax = r.left(),r.right(),r.top(),r.bottom()
        xmin = 100 * (round(xmin) // 100)
        ymin = 100 * (round(ymin) // 100)
        xmax = 100 * (1 + round(xmax) // 100)
        ymax = 100 * (1 + round(ymax) // 100)
        P = QPen()
        P.setWidth(0)
        P.setColor(QColor(0,0,0,64))
        Q = QPen()
        Q.setWidth(1)
        Q.setColor(QColor(0,0,0))
        R = QPen()
        R.setWidth(1)
        R.setColor(QColor(255,0,0))
        gap0 = 20
        gap1 = 100
        gap2 = 500

        for x in range(xmin,xmax+1,gap0):
            pen = R if x % gap2 == 0 else (Q if x % gap1 == 0 else P)
            self.mesh.append(self.scene.addLine(x,ymin,x,ymax,pen))
        for y in range(ymin,ymax+1,gap0):
            pen = R if y % gap2 == 0 else (Q if y % gap1 == 0 else P)
            self.mesh.append(self.scene.addLine(xmin,y,xmax,y,pen))

    def toggle_mesh(self):
        if self.mesh:
            while self.mesh:
                self.scene.removeItem(self.mesh.pop())
        else:
            print(self.scene.itemsBoundingRect())
            self.add_mesh(self.scene.itemsBoundingRect())

    def toggle_circle(self):
        if self.circ:
            self.scene.removeItem(self.circ)
            self.circ = None
        else:
            self.add_circ()

    def create_widgets(self):
        # TODO: ビュー上の HUD 要素の配置
        self.exp_rate_btn = QPushButton("100%", self)

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

    def create_actions(self):
        pass

    def layout_widgets(self):
        pass

    def create_connections(self):
        self.exp_rate_btn.clicked.connect(self.on_exp_rate_clicked)
        self.shift_wheel.connect(self.czoom)

    def add_pixmapitem(self, key: str, pm: QPixmap) -> bool:
        #if not self.mesh:
        #    self.add_mesh(pm.width(),pm.height())
        if key in self.dict_items:
            print(f"dict_items ALREADY Has Item Of Key: {key}")
            return self.update_pixmapitem(key, pm)
        self.dict_items[key] = QGraphicsPixmapItem(pm)
        self.scene.addItem(self.dict_items[key])
        self.reset_transform_to_fit()
        return True

    def update_pixmapitem(self, key: str, pm: QPixmap) -> bool:
        if key not in self.dict_items:
            print(f"There Is NO Item Of Key: {key}")
            return self.add_pixmapitem(key, pm)
        self.dict_items[key].setPixmap(pm)
        return True

    def remove_item(self, key: str) -> bool:
        if key not in self.dict_items:
            print(f"There Is NO Item Of Key: {key}")
            return False
        self.scene.removeItem(self.dict_items[key])
        del self.dict_items[key]
        return True

    def set_transform_mapitem(self, key: str, transform: QTransform) -> bool:
        if key not in self.dict_items:
            print(f"There Is NO Item Of Key: {key}")
            return False
        self.dict_items[key].setTransform(transform)
        return True

    def set_opacity_mapitem(self, key: str, opacity: float) -> bool:
        if key not in self.dict_items:
            print(f"There Is NO Item Of Key: {key}")
            return False
        self.dict_items[key].setOpacity(opacity)
        return True

    def set_visible_mapitem(self, key: str, is_visible: bool) -> bool:
        if key not in self.dict_items:
            print(f"There Is NO Item Of Key: {key}")
            return False
        self.dict_items[key].setVisible(is_visible)
        return True

    def get_scale(self) -> (float, float):
        trans = self.transform()
        sx = sqrt(trans.m11()**2 + trans.m12()**2)
        sy = sqrt(trans.m21()**2 + trans.m22()**2)
        return sx, sy

    def get_position(self):
        trans = self.transform()
        return trans.m31(), trans.m32()

    def set_scale(self, x: float, y: float) -> bool:
        if x <= 0 or y <= 0:
            print("Scale Factor MUST Be Larger Than 0.")
            return False
        sx, sy = self.get_scale()
        self.scale(x / sx, y / sy)
        return True

    def set_position(self, x: float, y: float):
        dx, dy = self.get_position()
        self.translate(x - dx, y - dy)

    def zoom(self, step_num: int):
        """
        step_num で指定したステップ分だけ拡大縮小する。
        """
        sx, sy = self.get_scale()
        # 現在のスケールに応じてステップ幅を設定する。
        step = 0.25
        if sx < 0.25:
            step = 0.05
        elif sx == 0.25:
            if step_num < 0:
                step = 0.05
            else:
                step = 0.25
        # 現在のスケールを丸め込む。
        sx = sx - (sx % step)
        # 拡大縮小
        val = sx + step*step_num
        if val > 4.0:
            val = 4.0
        elif val < 0.05:
            val = 0.05
        self.set_scale(val, val)
        self.update_exp_rate_btn()

    def update_exp_rate_btn(self):
        sx, sy = self.get_scale()
        self.exp_rate_btn.setText(f"{sx*100:.3g}%")

    def reset_transform_to_fit(self) -> None:
        # NOTE: 原点を示す円以外の item が無いときは拡大率を100%にしている。
        # 初期状態の item の数を増減する場合はここを修正しなくてはいけない。
        if len(self.scene.items()) <= 1:
            self.resetTransform()
        else:
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.update_exp_rate_btn()

    def wheelEvent(self, e: QWheelEvent):
        angle_delta = e.angleDelta()
        ad = angle_delta.x() + angle_delta.y() 
        # print(f"WHEEL ANGLE DELTA X: {angle_delta.x()}, {angle_delta.y()}")
        mods = QApplication.keyboardModifiers()
        if mods & Qt.ControlModifier and mods & Qt.ShiftModifier:
            self.ctrl_wheel.emit(ad//6)
        elif mods & Qt.ControlModifier and mods & Qt.AltModifier:
            self.ctrl_wheel.emit(ad//6)
        elif mods & Qt.ControlModifier:
            self.ctrl_wheel.emit(ad//40)
        elif mods & Qt.ShiftModifier:
            self.shift_wheel.emit(ad//12)
        elif mods & Qt.AltModifier:
            self.shift_wheel.emit(ad//12)
        else:
            self.zoom(int(ad / 120))

    def keyReleaseEvent(self, e: QKeyEvent):
        # FIXME: 手元の環境での検証用に [ キーでズームインにしてるが後で直す。
        if e.matches(QKeySequence.ZoomIn) or e.text() == "[":
            self.zoom(1)
        elif e.matches(QKeySequence.ZoomOut):
            self.zoom(-1)
        #elif e.key() == Qt.Key_Plus:
        #    self.shift_wheel.emit(1)
        #elif e.key() == Qt.Key_Minus:
        #    self.shift_wheel.emit(-1)
        #elif e.key() == Qt.Key_Asterisk:
        #    self.shift_wheel.emit(10)
        #elif e.key() == Qt.Key_Slash:
        #    self.shift_wheel.emit(-10)


        super().keyReleaseEvent(e)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            self.reset_transform_to_fit()
        if e.button() == Qt.LeftButton:
            self.toggle_mesh()
        if e.button() == Qt.MiddleButton:
            self.xy = self.mapToScene(e.pos())
            self.toggle_circle()
        super().mousePressEvent(e)

    def on_exp_rate_clicked(self):
        self.reset_transform_to_fit()

    def showEvent(self, e):
        self.reset_transform_to_fit()
        super().showEvent(e)

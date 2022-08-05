import numpy as np
from math import cos, sin, degrees, radians
from PyQt5.QtGui import QTransform


class AffineTransform:
    # NOTE: せん断は考慮しない。
    def __init__(
            self,
            px: float = 0.0,
            py: float = 0.0,
            rz: float = 0.0,
            sx: float = 1.0,
            sy: float = 1.0,
            origin_x: float = 0.0,
            origin_y: float = 0.0
            ) -> None:
        self.px = px
        self.py = py
        self.rz = rz
        self.sx = sx
        self.sy = sy
        # NOTE: origin_x(or _y) は原点の座標を示す。
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.before_matrix = np.array(
            [
                [1.0, 0.0, -origin_x],
                [0.0, 1.0, -origin_y],
                [0.0, 0.0, 1.0]
            ]
        )
        self.after_matrix = np.array(
            [
                [1.0, 0.0, origin_x],
                [0.0, 1.0, origin_y],
                [0.0, 0.0, 1.0]
            ]
        )
        # NOTE: matrix は origin_x(or _y) の値を加味しない。
        self.matrix = np.zeros((3, 3))
        self._update_matrix

    def _update_matrix(self) -> None:
        self.matrix = np.array(
            [
                [self.sx * cos(self.rz), -self.sy * sin(self.rz), self.px],
                [self.sx * sin(self.rz),  self.sy * cos(self.rz), self.py],
                [0.0,                     0.0,                    1.0]
            ]
        )

    def _update_before_matrix(self) -> None:
        self.before_matrix[0, 2] = -self.origin_x
        self.before_matrix[1, 2] = -self.origin_y

    def _update_after_matrix(self) -> None:
        self.after_matrix[0, 2] = self.origin_x
        self.after_matrix[1, 2] = self.origin_y

    def get_matrix(self) -> np.array:
        return self.matrix

    def get_position(self) -> (float, float):
        return self.px, self.py

    def get_rotation_radian(self) -> float:
        return self.rz

    def get_rotation_degree(self) -> float:
        return degrees(self.rz)

    def get_scale(self) -> (float, float):
        return self.sx, self.sy
    
    def get_origin(self) -> (float, float):
        return self.origin_x, self.origin_y

    def set_position(self, x: float, y: float) -> (float, float):
        self.px = x
        self.py = y
        self._update_matrix()
        return self.px, self.py

    def set_rotation_radian(self, radian: float) -> float:
        self.rz = radian
        self._update_matrix()
        return self.rz

    def set_rotation_degree(self, degree: float) -> float:
        self.rz = radians(degree)
        self._update_matrix()
        return degrees(self.rz)

    def set_scale(self, x: float, y: float) -> (float, float):
        if x == 0 or y == 0:
            return self.sx, self.sy
        self.sx = x
        self.sy = y
        self._update_matrix()
        return self.sx, self.sy

    def set_origin(self, x: float, y: float) -> (float, float):
        self.origin_x = x
        self.origin_y = y
        self._update_before_matrix()
        self._update_after_matrix()
        # self._print_stats()
        return self.origin_x, self.origin_y

    # NOTE: origin_x (or _y) で設定した原点に基づいて変換前後にオフセットを加えた行列を返す。
    def QTransform(self) -> QTransform:
        # self._print_stats()
        trans = self.after_matrix @ self.matrix @ self.before_matrix
        return QTransform(
            trans[0, 0],
            trans[1, 0],
            trans[0, 1],
            trans[1, 1],
            trans[0, 2],
            trans[1, 2]
        )

    # OpenCV の warpAffine() の引数 M に渡すための numpy 配列を返す。
    def M(self) -> np.ndarray:
        t = self.after_matrix @ self.matrix @ self.before_matrix
        return np.array(
            [
                [t[0, 0], t[0, 1], t[0, 2]],
                [t[1, 0], t[1, 1], t[1, 2]]
            ]
        )

    # 動作検証用のプリントメソッド
    def _print_stats(self) -> None:
        print("matrix:")
        print(self.matrix)
        print("before_matrix:")
        print(self.before_matrix)
        print("after_matrix:")
        print(self.after_matrix)
        print("result:")
        print(self.after_matrix @ self.matrix @ self.before_matrix)
        print(f"Origin  x: {self.origin_x}, y: {self.origin_y}")

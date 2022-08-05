from PyQt5.QtWidgets import QWidget, QVBoxLayout

from common_widgets.params_editor import ParamsEditor
from atp_editor.widgets.similarity_indicator import SimilarityIndicator
from atp_editor.widgets.diff_view import DiffView
from util.editor import Editor


class SideBar(QWidget):
    def __init__(self, parent: QWidget, editor: Editor) -> None:
        super().__init__(parent)

        self.editor = editor

        self.create_widgets()
        self.create_actions()
        self.layout_widgets()
        self.create_connections()

    def create_widgets(self):
        self.paramsEditorB = ParamsEditor(self, self.editor, "base", "Parameters Base")
        self.paramsEditorR = ParamsEditor(self, self.editor, "rotated", "Parameters Rotated")        
        self.indicator = SimilarityIndicator(self, self.editor)
        self.diff_view = DiffView(self, self.editor)

    def create_actions(self):
        ...

    def layout_widgets(self):
        layout = QVBoxLayout()
        layout.addWidget(self.paramsEditorB)
        layout.addWidget(self.paramsEditorR)        
        layout.addWidget(self.indicator)
        layout.addWidget(self.diff_view)
        self.setLayout(layout)

    def create_connections(self):
        ...

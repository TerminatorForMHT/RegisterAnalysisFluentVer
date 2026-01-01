from typing import Optional
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QMouseEvent
from qfluentwidgets import LineEdit


class ClickableLineEdit(LineEdit):
    """
    一个自定义的LineEdit，它可以在被鼠标点击时发射一个信号。
    """
    clicked = pyqtSignal(int)

    def __init__(self, index: int, parent: Optional[LineEdit] = None):
        super().__init__(parent)
        self.index = index

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event)

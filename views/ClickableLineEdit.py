from typing import Optional
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QMouseEvent
from qfluentwidgets import LineEdit


class ClickableLineEdit(LineEdit):
    """
    一个自定义的LineEdit，它可以在被鼠标点击时发射一个信号，使用圆角样式。
    """
    clicked = pyqtSignal(int)

    def __init__(self, index: int, parent: Optional[LineEdit] = None):
        super().__init__(parent)
        self.index = index
        # 确保组件能正确响应主题变化
        self._updateStyleSheet()
    
    def _updateStyleSheet(self):
        """
        更新样式表，确保圆角效果和透明背景在不同主题下都能正确显示
        """
        self.setStyleSheet("QLineEdit{background: transparent; border-radius: 8px; border: none}")
        
    def updateStyle(self, is_high: bool):
        """
        更新样式，根据比特值设置不同的背景色和圆角效果
        """
        from config import BIT_HIGH_COLOR
        if is_high:
            self.setStyleSheet(f"QLineEdit{{background-color: {BIT_HIGH_COLOR}; color: black; border-radius: 8px; border: none}}")
        else:
            self.setStyleSheet(f"QLineEdit{{background: transparent; color: white; border-radius: 8px; border: none}}")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event)

from typing import Optional
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QMouseEvent
from qfluentwidgets import LineEdit


class ClickableLineEdit(LineEdit):
    """
    一个自定义的LineEdit，它可以在被鼠标点击时发射一个信号，使用圆角样式。
    """
    clicked = pyqtSignal(int)

    def __init__(self, index: int, parent = None):
        super().__init__(parent)
        self.index = index
        # 确保组件能正确响应主题变化
        self._updateStyleSheet()
    
    def _updateStyleSheet(self):
        """
        更新样式表，确保圆角效果和透明背景在不同主题下都能正确显示
        """
        from qfluentwidgets import isDarkTheme
        
        # 根据当前主题动态调整颜色
        dark_theme = isDarkTheme()
        text_color = "white" if dark_theme else "black"
        border_color = "rgba(255, 255, 255, 0.2)" if dark_theme else "rgba(0, 0, 0, 0.2)"
        
        self.setStyleSheet(f"QLineEdit{{background: transparent; color: {text_color}; border-radius: 6px; border: 1px solid {border_color}; font-size: 16px; font-weight: bold}}")
        
    def updateStyle(self, is_high: bool):
        """
        更新样式，根据比特值设置不同的背景色和圆角效果
        """
        from config import BIT_HIGH_COLOR
        from qfluentwidgets import isDarkTheme
        
        # 根据当前主题动态调整颜色
        dark_theme = isDarkTheme()
        
        if is_high:
            # 1值的比特位：黄色背景，文字颜色根据主题调整
            text_color = "black" if dark_theme else "black"
            border_color = "rgba(0, 0, 0, 0.4)" if dark_theme else "rgba(0, 0, 0, 0.6)"
            self.setStyleSheet(f"QLineEdit{{background-color: {BIT_HIGH_COLOR}; color: {text_color}; border-radius: 6px; border: 1px solid {border_color}; font-size: 16px; font-weight: bold}}")
        else:
            # 0值的比特位：透明背景，文字颜色根据主题调整
            text_color = "white" if dark_theme else "black"
            border_color = "rgba(255, 255, 255, 0.2)" if dark_theme else "rgba(0, 0, 0, 0.2)"
            self.setStyleSheet(f"QLineEdit{{background: transparent; color: {text_color}; border-radius: 6px; border: 1px solid {border_color}; font-size: 16px; font-weight: bold}}")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event)

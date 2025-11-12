import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QGridLayout

# ✅ 正确导入 qfluentwidgets 组件
from qfluentwidgets import (
    FluentTitleBar,
    CardWidget,
    BodyLabel,
    LineEdit,
    setFont,
    PushButton,
    RadioButton,
    PrimaryPushButton,
    setTheme,
    Theme,
)
from qfluentwidgets.common.animation import BackgroundAnimationWidget
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow
from views.ClickableLineEdit import ClickableLineEdit


class MainWindow(BackgroundAnimationWidget, FramelessWindow):
    """ Fluent window with a bitwise analyzer """

    def __init__(self, parent=None):
        # 必须先初始化父类，再启用 Mica
        super().__init__(parent=parent)

        # ✅ 启用 Mica 特效（仅 Windows 11）
        if sys.platform == "win32":
            self.windowEffect.setMicaEffect(self.winId())

        # ✅ 自动跟随系统主题（深色/浅色）
        setTheme(Theme.AUTO)  # 这是关键！

        # 注意：启用 Mica 后，不要手动设置窗口背景色！
        # 原来的 _lightBackgroundColor / _darkBackgroundColor 不再需要
        self._isMaximizedFake = False
        self._normalGeometry = None

        self.maxDigit = 16
        self.maxBit = 4
        self.bitCount = self.maxDigit * self.maxBit
        self.bitValue = [0] * self.bitCount
        self.bitEntry = []

        self.resize(1280, 520)

        # 顶层布局改为垂直布局，结构更清晰
        self.main_layout = QVBoxLayout(self)

        self.initMainPanel()
        self.initControlsPanel()

        # 标题栏
        self.setTitleBar(FluentTitleBar(self))
        self.titleBar.raise_()
        self.titleBar.setTitle('数位分析器')
        self.titleBar.setIcon('titleico.svg')
        self.titleBar.setContentsMargins(15, 0, 0, 0)
        self.titleBar.maxBtn.hide()
        self.setWindowIcon(QIcon('titleico.svg'))

        # 自适应设置主布局与标题栏的垂直间距
        self._applyLayoutSpacing()

        self.clearBits()

    def _applyLayoutSpacing(self, extra=12):
        top_gap = self.titleBar.height() + extra if hasattr(self, "titleBar") and self.titleBar else 48 + extra
        self.main_layout.setContentsMargins(12, top_gap, 12, 12)
        self.main_layout.setSpacing(12)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._applyLayoutSpacing()

    def SLBits(self):
        try:
            value = self.getResult()
            shift_amount = int(self.shEntry.text())
            value = (value << shift_amount) & 0xFFFFFFFFFFFFFFFF
            self.setResult(value)
        except (ValueError, TypeError):
            pass

    def SRBits(self):
        try:
            value = self.getResult()
            shift_amount = int(self.shEntry.text())
            value = (value >> shift_amount) & 0xFFFFFFFFFFFFFFFF
            self.setResult(value)
        except (ValueError, TypeError):
            pass

    def formatBitEntry(self, entry, val):
        if val == 1:
            entry.setStyleSheet("background-color: yellow; color: black;")
        else:
            entry.setStyleSheet("")

    def clearBits(self):
        for bit in range(self.bitCount):
            self.bitValue[bit] = 0
            self.bitEntry[bit].setText('0')
            self.formatBitEntry(self.bitEntry[bit], 0)
        self.numSysSelect()

    def getResult(self):
        try:
            text = self.wordEntry.text()
            if self.hexRadio.isChecked():
                return int(text, 16)
            elif self.decRadio.isChecked():
                return int(text, 10)
            elif self.binRadio.isChecked():
                return int(text, 2)
        except ValueError:
            return 0

    def setResult(self, v):
        self.wordEntry.blockSignals(True)
        if self.hexRadio.isChecked():
            self.wordEntry.setText(f'{v:X}')
        elif self.decRadio.isChecked():
            self.wordEntry.setText(f'{v:d}')
        elif self.binRadio.isChecked():
            self.wordEntry.setText(f'{v:b}')
        self.wordEntry.blockSignals(False)
        self.updateBitsFromValue(v)

    def calResult(self):
        data = 0
        for i, val in enumerate(self.bitValue):
            if val == 1:
                data |= (1 << (self.bitCount - 1 - i))
        return data

    def calBits(self):
        value = self.getResult()
        if value is not None:
            self.updateBitsFromValue(value)

    def updateBitsFromValue(self, value):
        for bit in range(self.bitCount):
            v = (value >> (self.bitCount - 1 - bit)) & 0x1
            self.bitValue[bit] = v
            self.bitEntry[bit].setText(str(v))
            self.formatBitEntry(self.bitEntry[bit], v)

    def handleBitClick(self, index):
        self.bitValue[index] = 1 - self.bitValue[index]
        v = self.bitValue[index]

        entry = self.bitEntry[index]
        entry.setText(str(v))
        self.formatBitEntry(entry, v)

        self.numSysSelect()

    def numSysSelect(self):
        result = self.calResult()
        self.setResult(result)

    def initMainPanel(self):
        for i in range(2):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)

            start_digit = 8 if i == 1 else 0
            end_digit = 16 if i == 1 else 8

            for digit in range(start_digit, end_digit):
                digit_card = CardWidget()
                digit_layout = QGridLayout(digit_card)
                digit_num = self.maxDigit - digit - 1

                title_label = BodyLabel(f"数位 {digit_num}")
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                digit_layout.addWidget(title_label, 0, 0, 1, 4)

                for bit in range(self.maxBit):
                    idx = digit * self.maxBit + bit
                    bit_num = (self.maxDigit - digit - 1) * 4 + (self.maxBit - bit - 1)

                    bit_label = BodyLabel(str(bit_num))
                    bit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    bit_entry = ClickableLineEdit(idx)
                    bit_entry.setReadOnly(True)
                    bit_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    bit_entry.setFixedWidth(35)
                    bit_entry.clicked.connect(lambda _, i=idx: self.handleBitClick(i))

                    self.bitEntry.append(bit_entry)

                    digit_layout.addWidget(bit_label, 1, bit)
                    digit_layout.addWidget(bit_entry, 2, bit)

                row_layout.addWidget(digit_card)

            self.main_layout.addWidget(row_widget)

    def initControlsPanel(self):
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)

        type_card = self.initTypeButton()
        result_card = self.initResultPanel()
        func_widget = self.initFuncButton()

        controls_layout.addWidget(type_card, stretch=2)
        controls_layout.addWidget(result_card, stretch=5)
        controls_layout.addWidget(func_widget, stretch=1)

        self.main_layout.addWidget(controls_widget)

    def initResultPanel(self):
        result_card = CardWidget()
        result_layout = QVBoxLayout(result_card)

        header_layout = QHBoxLayout()
        header_layout.addWidget(BodyLabel("最高有效位 (MSB)"))
        header_layout.addStretch(1)
        header_layout.addWidget(BodyLabel("最低有效位 (LSB)"))

        self.wordEntry = LineEdit()
        self.wordEntry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setFont(self.wordEntry, 16)
        self.wordEntry.textEdited.connect(self.calBits)

        shift_layout = QHBoxLayout()
        shlButton = PushButton("左移")
        shlButton.clicked.connect(self.SLBits)

        self.shEntry = LineEdit()
        self.shEntry.setText("1")
        self.shEntry.setFixedWidth(50)
        self.shEntry.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sfrButton = PushButton("右移")
        sfrButton.clicked.connect(self.SRBits)

        shift_layout.addWidget(shlButton)
        shift_layout.addStretch(1)
        shift_layout.addWidget(self.shEntry)
        shift_layout.addStretch(1)
        shift_layout.addWidget(sfrButton)

        result_layout.addLayout(header_layout)
        result_layout.addWidget(self.wordEntry)
        result_layout.addLayout(shift_layout)

        return result_card

    def initTypeButton(self):
        type_card = CardWidget()
        type_layout = QVBoxLayout(type_card)
        type_layout.setSpacing(10)

        title_label = BodyLabel("进制")
        type_layout.addWidget(title_label)

        self.hexRadio = RadioButton("十六进制", type_card)
        self.decRadio = RadioButton("十进制", type_card)
        self.binRadio = RadioButton("二进制", type_card)

        self.hexRadio.setChecked(True)

        self.hexRadio.toggled.connect(lambda checked: self.numSysSelect() if checked else None)
        self.decRadio.toggled.connect(lambda checked: self.numSysSelect() if checked else None)
        self.binRadio.toggled.connect(lambda checked: self.numSysSelect() if checked else None)

        type_layout.addWidget(self.hexRadio)
        type_layout.addWidget(self.decRadio)
        type_layout.addWidget(self.binRadio)
        type_layout.addStretch(1)

        return type_card

    def initFuncButton(self):
        func_widget = QWidget()
        func_layout = QVBoxLayout(func_widget)
        func_layout.setContentsMargins(0, 0, 0, 0)

        clearButton = PushButton("清空")
        clearButton.clicked.connect(self.clearBits)

        closeButton = PrimaryPushButton("关闭")
        closeButton.clicked.connect(self.close)

        func_layout.addWidget(clearButton)
        func_layout.addStretch(1)
        func_layout.addWidget(closeButton)

        return func_widget
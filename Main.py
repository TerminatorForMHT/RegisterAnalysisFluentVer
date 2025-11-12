import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QGridLayout, QApplication
from qfluentwidgets import FluentTitleBar, FluentIcon, CardWidget, BodyLabel, LineEdit, PushButton, RadioButton, \
    PrimaryPushButton
from qfluentwidgets.common.animation import BackgroundAnimationWidget
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow


class ClickableLineEdit(LineEdit):
    """
    一个自定义的LineEdit，它可以在被鼠标点击时发射一个信号。
    """
    clicked = pyqtSignal(int)

    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event)


class MainWindow(BackgroundAnimationWidget, FramelessWindow):
    """ Fluent window with ToDo list """

    def __init__(self, parent=None):
        self._isMicaEnabled = False
        self._lightBackgroundColor = QColor(240, 244, 249)
        self._darkBackgroundColor = QColor(32, 32, 32)
        self._isMaximizedFake = False
        self._normalGeometry = None

        super().__init__(parent=parent)

        self.maxDigit = 16
        self.maxBit = 4
        self.bitCount = self.maxDigit * self.maxBit
        self.bitValue = [0] * self.bitCount
        self.bitEntry = []

        self.resize(300, 200)

        # 顶层布局
        self.main_layout = QGridLayout(self)

        self.initMainPanel()
        self.initResultPanel()
        self.initTypeButton()
        self.initFuncButton()

        # 标题栏
        self.setTitleBar(FluentTitleBar(self))
        self.titleBar.raise_()
        self.titleBar.setTitle('Register Analyzer')
        self.titleBar.setIcon('titleico.svg')
        self.titleBar.setContentsMargins(15, 0, 0, 0)
        self.titleBar.maxBtn.hide()
        self.setWindowIcon(QIcon('titleico.svg'))
        # 自适应设置主布局与标题栏的垂直间距
        self._applyLayoutSpacing()

        self.clearBits()

    def _applyLayoutSpacing(self, extra=12):
        """
        根据标题栏高度自适应设置主布局的上边距，从而拉开标题栏与主界面内容的距离。
        extra 为标题栏下方额外留白（像素），可按需调整。
        """
        top_gap = self.titleBar.height() + extra if hasattr(self, "titleBar") and self.titleBar else 48 + extra
        # 设置主布局边距和内部间距
        self.main_layout.setContentsMargins(12, top_gap, 12, 12)
        # 统一内边距/间距
        try:
            self.main_layout.setHorizontalSpacing(12)
            self.main_layout.setVerticalSpacing(12)
        except Exception:
            # 兼容性处理（一般不需要）
            self.main_layout.setSpacing(12)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        # 窗口尺寸或DPI变化时，保持与标题栏的自适应间距
        self._applyLayoutSpacing()

    def SLBits(self):
        """ 左移位 """
        try:
            value = self.getResult()
            shift_amount = int(self.shEntry.text())
            value = (value << shift_amount) & 0xFFFFFFFFFFFFFFFF
            self.setResult(value)
        except (ValueError, TypeError):
            pass

    def SRBits(self):
        """ 右移位 """
        try:
            value = self.getResult()
            shift_amount = int(self.shEntry.text())
            value = (value >> shift_amount) & 0xFFFFFFFFFFFFFFFF
            self.setResult(value)
        except (ValueError, TypeError):
            pass

    def formatBitEntry(self, entry, val):
        """ 根据位的值设置样式 """
        if val == 1:
            entry.setStyleSheet("background-color: yellow; color: black;")
        else:
            entry.setStyleSheet("")

    def clearBits(self):
        """ 清除所有位 """
        for bit in range(self.bitCount):
            self.bitValue[bit] = 0
            self.bitEntry[bit].setText('0')
            self.formatBitEntry(self.bitEntry[bit], 0)
        self.numSysSelect()

    def getResult(self):
        """ 从主输入框获取整数值 """
        try:
            text = self.wordEntry.text()
            if self.hexRadio.isChecked():
                return int(text, 16)
            elif self.decRadio.isChecked():
                return int(text, 10)
            elif self.octRadio.isChecked():
                return int(text, 8)
        except ValueError:
            return 0

    def setResult(self, v):
        """ 根据选择的数字系统，设置主输入框的值 """
        self.wordEntry.blockSignals(True)
        if self.hexRadio.isChecked():
            self.wordEntry.setText(f'{v:X}')
        elif self.decRadio.isChecked():
            self.wordEntry.setText(f'{v:d}')
        elif self.octRadio.isChecked():
            self.wordEntry.setText(f'{v:o}')
        self.wordEntry.blockSignals(False)
        self.updateBitsFromValue(v)

    def calResult(self):
        """ 从位数组计算整数结果 """
        data = 0
        for i, val in enumerate(self.bitValue):
            if val == 1:
                data |= (1 << (self.bitCount - 1 - i))
        return data

    def calBits(self):
        """ 当主输入框文本被用户编辑时，更新所有位 """
        value = self.getResult()
        if value is not None:
            self.updateBitsFromValue(value)

    def updateBitsFromValue(self, value):
        """ 根据给定的整数值更新所有位的值和显示 """
        for bit in range(self.bitCount):
            v = (value >> (self.bitCount - 1 - bit)) & 0x1
            self.bitValue[bit] = v
            self.bitEntry[bit].setText(str(v))
            self.formatBitEntry(self.bitEntry[bit], v)

    def handleBitClick(self, index):
        """ 处理位的点击事件 """
        self.bitValue[index] = 1 - self.bitValue[index]
        v = self.bitValue[index]

        entry = self.bitEntry[index]
        entry.setText(str(v))
        self.formatBitEntry(entry, v)

        self.numSysSelect()

    def numSysSelect(self):
        """ 当数字系统切换时，重新格式化结果 """
        result = self.calResult()
        self.setResult(result)

    def initMainPanel(self):
        """ 初始化64位的显示面板 """
        # 为了更好地布局，我们将两行bit卡片分别放入垂直布局中
        main_bits_layout = QVBoxLayout()
        main_bits_layout.setSpacing(10)

        for i in range(2):  # 创建两行，每行8个digit
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
                # Fluent-Widgets 的 CardWidget 没有 title 属性，我们用一个标签来模拟
                title_label = BodyLabel(f"Digit {digit_num}")
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                digit_layout.addWidget(title_label, 0, 0, 1, 4)  # 标签跨越4列

                for bit in range(self.maxBit):
                    idx = digit * self.maxBit + bit
                    bit_num = (self.maxDigit - digit - 1) * 4 + (self.maxBit - bit - 1)

                    bit_label = BodyLabel(str(bit_num))
                    bit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    bit_entry = ClickableLineEdit(idx)
                    bit_entry.setReadOnly(True)
                    bit_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    bit_entry.setFixedWidth(35)
                    bit_entry.clicked.connect(self.handleBitClick)

                    self.bitEntry.append(bit_entry)

                    digit_layout.addWidget(bit_label, 1, bit)
                    digit_layout.addWidget(bit_entry, 2, bit)

                row_layout.addWidget(digit_card)

            main_bits_layout.addWidget(row_widget)

        self.main_layout.addLayout(main_bits_layout, 0, 0, 1, 4)

    def initResultPanel(self):
        """ 初始化结果显示和移位操作面板 """
        result_card = CardWidget()
        result_layout = QVBoxLayout(result_card)

        header_layout = QHBoxLayout()
        header_layout.addWidget(BodyLabel("MSB"))
        header_layout.addStretch(1)
        header_layout.addWidget(BodyLabel("LSB"))

        self.wordEntry = LineEdit()
        self.wordEntry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.wordEntry.font()
        font.setPointSize(14)
        self.wordEntry.setFont(font)
        self.wordEntry.textEdited.connect(self.calBits)

        shift_layout = QHBoxLayout()
        shlButton = PushButton()
        shlButton.setText(("<< Shift"))
        shlButton.clicked.connect(self.SLBits)

        self.shEntry = LineEdit()
        self.shEntry.setText("1")
        self.shEntry.setFixedWidth(50)
        self.shEntry.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sfrButton = PushButton()
        sfrButton.setText("Shift >>")
        sfrButton.clicked.connect(self.SRBits)

        shift_layout.addWidget(shlButton)
        shift_layout.addWidget(self.shEntry)
        shift_layout.addWidget(sfrButton)

        result_layout.addLayout(header_layout)
        result_layout.addWidget(self.wordEntry)
        result_layout.addLayout(shift_layout)

        self.main_layout.addWidget(result_card, 1, 1)

    def initTypeButton(self):
        """ 初始化数字系统选择面板 """
        type_card = CardWidget()
        type_layout = QVBoxLayout(type_card)

        # 同样，用标签作为标题
        title_label = BodyLabel("Number System")
        type_layout.addWidget(title_label)

        self.hexRadio = RadioButton("Hex", type_card)
        self.decRadio = RadioButton("Dec", type_card)
        self.octRadio = RadioButton("Oct", type_card)

        self.hexRadio.setChecked(True)

        self.hexRadio.toggled.connect(lambda checked: self.numSysSelect() if checked else None)
        self.decRadio.toggled.connect(lambda checked: self.numSysSelect() if checked else None)
        self.octRadio.toggled.connect(lambda checked: self.numSysSelect() if checked else None)

        type_layout.addWidget(self.hexRadio)
        type_layout.addWidget(self.decRadio)
        type_layout.addWidget(self.octRadio)

        self.main_layout.addWidget(type_card, 1, 0)

    def initFuncButton(self):
        """ 初始化功能按钮 """
        func_layout = QVBoxLayout()
        func_widget = QWidget()  # 使用一个widget来容纳布局
        func_widget.setLayout(func_layout)

        clearButton = PushButton()
        clearButton.setText("Clear")
        clearButton.clicked.connect(self.clearBits)

        closeButton = PrimaryPushButton()
        closeButton.setText("Close")
        closeButton.clicked.connect(self.close)

        func_layout.addWidget(clearButton)
        func_layout.addStretch(1)
        func_layout.addWidget(closeButton)

        self.main_layout.addWidget(func_widget, 1, 3)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

import sys
from typing import Optional
from PyQt5.QtCore import Qt, QEvent, QRegularExpression, QTimer
from PyQt5.QtGui import QIcon, QRegularExpressionValidator
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QGridLayout

from config import (
    APP_NAME, MAIN_ICON, WINDOW_WIDTH, WINDOW_HEIGHT,
    MAX_DIGIT, MAX_BIT_PER_DIGIT, MAX_BIT_COUNT,
    BIT_HIGH_COLOR, BIT_LOW_COLOR, MAX_SHIFT_VALUE,
)

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
    InfoBar,
    InfoBarPosition,
    FluentWindow,
    FluentWidget,
    SystemThemeListener,
    isDarkTheme
)
from qfluentwidgets.common.config import qconfig
from PyQt5.QtCore import QTimer
from views.ClickableLineEdit import ClickableLineEdit


class MainWindow(FluentWidget):
    """ Fluent window with a bitwise analyzer """

    def __init__(self, parent: Optional[QWidget] = None):
        # 必须先初始化父类，Mica效果会在父类初始化中自动应用
        super().__init__(parent)

        # ✅ 自动跟随系统主题（深色/浅色）
        from qfluentwidgets import Theme
        setTheme(Theme.AUTO)  # 这是关键！

        # 创建主题监听器
        self.themeListener = SystemThemeListener(self)

        # 注意：启用 Mica 后，不要手动设置窗口背景色！

        # 使用配置文件中的常量
        self.maxDigit = MAX_DIGIT
        self.maxBit = MAX_BIT_PER_DIGIT
        self.bitCount = MAX_BIT_COUNT
        self.bitValue = [0] * self.bitCount
        self.bitEntry = []

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # 设置窗口图标和标题
        self.setWindowIcon(QIcon(MAIN_ICON))
        self.setWindowTitle(APP_NAME)

        # 顶层布局改为垂直布局，结构更清晰
        self.main_layout = QVBoxLayout(self)
        # 留出标题栏的空间
        self.main_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.main_layout.setSpacing(10)

        self.init_main_panel()
        self.init_controls_panel()

        # 连接主题变化信号，确保界面能响应系统主题变化
        qconfig.themeChanged.connect(self.on_theme_changed)

        # 启动主题监听器
        self.themeListener.start()

        self.clear_bits()

    def shift_left_bits(self) -> None:
        """
        将当前值左移指定的位数。
        
        从输入框获取移位量，将当前结果左移相应位数，并更新显示。
        仅在输入有效时执行操作。
        """
        try:
            value = self.get_result()
            shift_amount_str = self.shEntry.text().strip()
            if not shift_amount_str:
                return
            
            shift_amount = int(shift_amount_str)
            if shift_amount < 0 or shift_amount > MAX_SHIFT_VALUE:
                return
                
            value = (value << shift_amount) & 0xFFFFFFFFFFFFFFFF
            self.set_result(value)
        except ValueError as e:
            InfoBar.warning(
                title="输入错误",
                content=f"移位量必须是0到{MAX_SHIFT_VALUE}之间的整数",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM,
                duration=3000,
                parent=self
            )

    def shift_right_bits(self) -> None:
        """
        将当前值右移指定的位数。
        
        从输入框获取移位量，将当前结果右移相应位数，并更新显示。
        仅在输入有效时执行操作。
        """
        try:
            value = self.get_result()
            shift_amount_str = self.shEntry.text().strip()
            if not shift_amount_str:
                return
            
            shift_amount = int(shift_amount_str)
            if shift_amount < 0 or shift_amount > MAX_SHIFT_VALUE:
                return
                
            value = (value >> shift_amount) & 0xFFFFFFFFFFFFFFFF
            self.set_result(value)
        except ValueError as e:
            InfoBar.warning(
                title="输入错误",
                content=f"移位量必须是0到{MAX_SHIFT_VALUE}之间的整数",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM,
                duration=3000,
                parent=self
            )

    def format_bit_entry(self, entry: ClickableLineEdit, val: int) -> None:
        """
        根据比特值设置输入框的样式。
        
        Args:
            entry: 要格式化的比特输入框
            val: 比特值（0或1）
        """
        if val == 1:
            entry.setStyleSheet(f"background-color: {BIT_HIGH_COLOR}; color: black;")
        else:
            entry.setStyleSheet(BIT_LOW_COLOR)

    def clear_bits(self) -> None:
        """
        清空所有比特位，将其设置为0，并更新显示。
        """
        for bit in range(self.bitCount):
            self.bitValue[bit] = 0
            self.bitEntry[bit].setText('0')
            self.format_bit_entry(self.bitEntry[bit], 0)
        self.number_system_select()

    def get_result(self) -> int:
        """
        获取当前输入的结果值。
        
        根据当前选择的进制，将输入框中的文本转换为整数。
        如果输入无效，返回0。
        
        Returns:
            当前输入的整数值
        """
        text = self.wordEntry.text().strip()
        if not text:
            return 0
            
        try:
            if self.hexRadio.isChecked():
                return int(text, 16)
            elif self.decRadio.isChecked():
                return int(text, 10)
            elif self.binRadio.isChecked():
                return int(text, 2)
            return 0
        except ValueError as e:
            # 不显示错误信息，因为用户可能正在输入过程中
            return 0

    def set_result(self, v: int) -> None:
        """
        设置结果值，并更新显示。
        
        根据当前选择的进制，将整数值转换为文本显示在输入框中，
        并更新所有比特位的状态。
        
        Args:
            v: 要设置的整数值
        """
        self.wordEntry.blockSignals(True)
        if self.hexRadio.isChecked():
            self.wordEntry.setText(f'{v:X}')
        elif self.decRadio.isChecked():
            self.wordEntry.setText(f'{v:d}')
        elif self.binRadio.isChecked():
            self.wordEntry.setText(f'{v:b}')
        self.wordEntry.blockSignals(False)
        self.update_bits_from_value(v)

    def calculate_result(self) -> int:
        """
        根据当前比特位状态计算结果值。
        
        遍历所有比特位，将值为1的比特位转换为对应的整数值并累加。
        
        Returns:
            计算得到的整数值
        """
        data = 0
        for i, val in enumerate(self.bitValue):
            if val == 1:
                data |= (1 << (self.bitCount - 1 - i))
        return data

    def calculate_bits(self) -> None:
        """
        根据输入值计算并更新所有比特位的状态。
        
        获取当前输入值，并根据该值更新所有比特位的显示状态。
        """
        value = self.get_result()
        self.update_bits_from_value(value)

    def update_bits_from_value(self, value: int) -> None:
        """
        根据整数值更新所有比特位的状态。
        
        将整数值转换为二进制，并更新每个比特位的显示和样式。
        优化：只在比特位值实际变化时才更新UI，减少不必要的刷新。
        
        Args:
            value: 用于更新比特位的整数值
        """
        # 预先计算所有比特位的新值
        new_bit_values = []
        for bit in range(self.bitCount):
            v = (value >> (self.bitCount - 1 - bit)) & 0x1
            new_bit_values.append(v)
        
        # 只更新值发生变化的比特位
        for bit in range(self.bitCount):
            if self.bitValue[bit] != new_bit_values[bit]:
                self.bitValue[bit] = new_bit_values[bit]
                v = new_bit_values[bit]
                self.bitEntry[bit].setText(str(v))
                self.format_bit_entry(self.bitEntry[bit], v)

    def handle_bit_click(self, index: int) -> None:
        """
        处理比特位点击事件。
        
        当用户点击某个比特位时，切换其值（0变1，1变0），
        并更新显示和结果值。
        
        Args:
            index: 被点击的比特位索引
        """
        self.bitValue[index] = 1 - self.bitValue[index]
        v = self.bitValue[index]

        entry = self.bitEntry[index]
        entry.setText(str(v))
        self.format_bit_entry(entry, v)

        self.number_system_select()

    def number_system_select(self) -> None:
        """
        进制选择变化处理函数。
        
        当用户切换进制时，重新计算并显示结果，并更新输入验证器。
        """
        self._update_input_validator()
        result = self.calculate_result()
        self.set_result(result)

    def init_main_panel(self) -> None:
        """
        初始化主面板，创建所有比特位显示组件。
        
        创建16个数位卡片，每个卡片包含4个比特位，
        并将它们添加到主布局中。
        """
        # 创建主面板容器
        main_panel = QWidget()
        main_layout = QVBoxLayout(main_panel)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)  # 增大行间距，让各行之间更有层次感
        
        for i in range(4):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)  # 减小卡片间距，使布局更紧凑
            row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐

            start_digit = i * 4
            end_digit = (i + 1) * 4

            for digit in range(start_digit, end_digit):
                digit_card = CardWidget()
                digit_layout = QGridLayout(digit_card)
                digit_layout.setContentsMargins(15, 15, 15, 15)  # 增大卡片内边距
                digit_layout.setSpacing(12)  # 增大卡片内元素间距
                digit_num = self.maxDigit - digit - 1

                title_label = BodyLabel(f"数位 {digit_num}")
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                setFont(title_label, 14)  # 增大标题字体大小
                digit_layout.addWidget(title_label, 0, 0, 1, 4)

                for bit in range(self.maxBit):
                    idx = digit * self.maxBit + bit
                    bit_num = (self.maxDigit - digit - 1) * 4 + (self.maxBit - bit - 1)

                    bit_label = BodyLabel(str(bit_num))
                    bit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    setFont(bit_label, 12)  # 增大比特位编号字体大小

                    bit_entry = ClickableLineEdit(idx)
                    bit_entry.setReadOnly(True)
                    bit_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    bit_entry.setFixedWidth(50)  # 进一步增大比特位输入框宽度
                    bit_entry.setFixedHeight(55)  # 进一步增大比特位输入框高度，增加卡片整体高度
                    bit_entry.clicked.connect(lambda _, i=idx: self.handle_bit_click(i))
                    setFont(bit_entry, 18, weight=700)  # 进一步增大字体大小并加粗

                    self.bitEntry.append(bit_entry)

                    digit_layout.addWidget(bit_label, 1, bit)
                    digit_layout.addWidget(bit_entry, 2, bit)

                row_layout.addWidget(digit_card)

            main_layout.addWidget(row_widget)
        
        # 将主面板添加到窗口的主布局中，设置拉伸因子让它占据更多空间
        self.main_layout.addWidget(main_panel, stretch=1)

    def init_controls_panel(self) -> None:
        """
        初始化控制面板，包含进制选择、结果显示和功能按钮。
        
        创建包含进制选择、结果输入框和功能按钮的控制面板，
        并将其添加到主布局中。
        """
        controls_widget = QWidget()
        controls_layout = QGridLayout(controls_widget)
        controls_layout.setContentsMargins(5, 5, 5, 5)
        controls_layout.setSpacing(8)

        type_card = self.init_type_button()
        result_card = self.init_result_panel()
        func_widget = self.init_func_button()

        # 使用GridLayout排列组件，使其更紧凑
        controls_layout.addWidget(type_card, 0, 0)
        controls_layout.addWidget(result_card, 0, 1, 1, 2)
        controls_layout.addWidget(func_widget, 0, 3)
        
        # 设置列拉伸比例，让结果面板占据更多空间
        controls_layout.setColumnStretch(0, 1)
        controls_layout.setColumnStretch(1, 2)
        controls_layout.setColumnStretch(2, 1)
        controls_layout.setColumnStretch(3, 1)

        self.main_layout.addWidget(controls_widget)

    def init_result_panel(self) -> CardWidget:
        """
        初始化结果显示面板。
        
        创建包含结果输入框和移位控制的面板，
        用于显示当前结果和进行移位操作。
        
        Returns:
            结果显示面板组件
        """
        result_card = CardWidget()
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(5, 5, 5, 5)  # 减小面板内边距
        result_layout.setSpacing(5)  # 减小组件间距，使布局更紧凑

        self.wordEntry = LineEdit()
        self.wordEntry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setFont(self.wordEntry, 14)  # 调整结果显示字体大小
        self.wordEntry.setMinimumHeight(35)  # 调整结果输入框高度
        self.wordEntry.textEdited.connect(self.calculate_bits)
        # 设置初始输入验证器
        self._update_input_validator()

        shift_layout = QHBoxLayout()
        shlButton = PushButton("左移")
        setFont(shlButton, 12)  # 增大按钮字体大小
        shlButton.setMinimumHeight(30)  # 增大按钮高度
        shlButton.setFixedSize(70, 30)  # 固定按钮大小
        shlButton.clicked.connect(self.shift_left_bits)

        self.shEntry = LineEdit()
        self.shEntry.setText("1")
        self.shEntry.setFixedWidth(40)  # 增大宽度
        self.shEntry.setMinimumHeight(30)  # 增大高度
        self.shEntry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setFont(self.shEntry, 12)  # 增大字体大小
        # 设置移位输入验证器，只允许数字
        shift_validator = QRegularExpressionValidator(QRegularExpression(r"[0-9]*"), self.shEntry)
        self.shEntry.setValidator(shift_validator)

        sfrButton = PushButton("右移")
        setFont(sfrButton, 12)  # 增大按钮字体大小
        sfrButton.setMinimumHeight(30)  # 增大按钮高度
        sfrButton.setFixedSize(70, 30)  # 固定按钮大小
        sfrButton.clicked.connect(self.shift_right_bits)

        shift_layout.addWidget(shlButton)
        shift_layout.addStretch(1)
        shift_layout.addWidget(self.shEntry)
        shift_layout.addStretch(1)
        shift_layout.addWidget(sfrButton)

        result_layout.addWidget(self.wordEntry)
        result_layout.addLayout(shift_layout)

        return result_card

    def init_type_button(self) -> CardWidget:
        """
        初始化进制选择按钮组。
        
        创建包含十六进制、十进制和二进制选择的单选按钮组。
        
        Returns:
            进制选择面板组件
        """
        type_card = CardWidget()
        type_layout = QVBoxLayout(type_card)
        type_layout.setSpacing(6)  # 大幅度减小间距
        type_layout.setContentsMargins(8, 8, 8, 8)  # 设置内边距

        title_label = BodyLabel("进制")
        setFont(title_label, 10)  # 大幅度降低标题字体大小
        type_layout.addWidget(title_label)

        self.hexRadio = RadioButton("十六进制", type_card)
        setFont(self.hexRadio, 9)  # 大幅度降低单选按钮字体大小
        self.hexRadio.setMaximumHeight(20)  # 大幅度降低单选按钮高度
        self.decRadio = RadioButton("十进制", type_card)
        setFont(self.decRadio, 9)  # 大幅度降低单选按钮字体大小
        self.decRadio.setMaximumHeight(20)  # 大幅度降低单选按钮高度
        self.binRadio = RadioButton("二进制", type_card)
        setFont(self.binRadio, 9)  # 大幅度降低单选按钮字体大小
        self.binRadio.setMaximumHeight(20)  # 大幅度降低单选按钮高度

        self.hexRadio.setChecked(True)

        self.hexRadio.toggled.connect(lambda checked: self.number_system_select() if checked else None)
        self.decRadio.toggled.connect(lambda checked: self.number_system_select() if checked else None)
        self.binRadio.toggled.connect(lambda checked: self.number_system_select() if checked else None)

        type_layout.addWidget(self.hexRadio)
        type_layout.addWidget(self.decRadio)
        type_layout.addWidget(self.binRadio)
        type_layout.addStretch(1)

        return type_card

    def init_func_button(self) -> QWidget:
        """
        初始化功能按钮面板。
        
        创建包含清空和关闭按钮的面板。
        
        Returns:
            功能按钮面板组件
        """
        func_widget = QWidget()
        func_layout = QVBoxLayout(func_widget)
        func_layout.setContentsMargins(0, 0, 0, 0)
        func_layout.setSpacing(8)  # 设置间距

        clearButton = PushButton("清空")
        setFont(clearButton, 13)  # 调整按钮字体大小
        clearButton.setMinimumHeight(35)  # 调整按钮高度
        clearButton.clicked.connect(self.clear_bits)

        closeButton = PrimaryPushButton("关闭")
        setFont(closeButton, 13)  # 调整按钮字体大小
        closeButton.setMinimumHeight(35)  # 调整按钮高度
        closeButton.clicked.connect(self.close)

        func_layout.addWidget(clearButton)
        func_layout.addStretch(1)
        func_layout.addWidget(closeButton)

        return func_widget
        
    def _update_input_validator(self) -> None:
        """
        根据当前选择的进制更新输入验证器。
        """
        if self.hexRadio.isChecked():
            # 十六进制验证器，允许0-9和A-F（大小写不敏感）
            validator = QRegularExpressionValidator(QRegularExpression(r"[0-9A-Fa-f]*"), self.wordEntry)
        elif self.decRadio.isChecked():
            # 十进制验证器，允许0-9
            validator = QRegularExpressionValidator(QRegularExpression(r"[0-9]*"), self.wordEntry)
        elif self.binRadio.isChecked():
            # 二进制验证器，允许0-1
            validator = QRegularExpressionValidator(QRegularExpression(r"[01]*"), self.wordEntry)
        else:
            validator = None
            
        if validator:
            self.wordEntry.setValidator(validator)
            
    def show_info_bar(self, title: str, content: str, type: str = "info") -> None:
        """
        显示信息提示条。
        
        Args:
            title: 提示条标题
            content: 提示条内容
            type: 提示类型，可选值：info, success, warning, error
        """
        if type == "success":
            InfoBar.success(
                title=title,
                content=content,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        elif type == "warning":
            InfoBar.warning(
                title=title,
                content=content,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        elif type == "error":
            InfoBar.error(
                title=title,
                content=content,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            InfoBar.info(
                title=title,
                content=content,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def closeEvent(self, e):
        """
        窗口关闭事件处理函数。
        
        确保主题监听器线程正确停止，避免资源泄漏。
        """
        # 停止监听器线程
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        super().closeEvent(e)

    def _onThemeChangedFinished(self):
        """
        主题变化完成后的回调函数。
        
        确保Mica特效在主题变化后正确应用，添加重试机制以提高可靠性。
        """
        super()._onThemeChangedFinished()

        # 云母特效启用时需要增加重试机制
        if self.isMicaEffectEnabled():
            QTimer.singleShot(100, lambda: self.windowEffect.setMicaEffect(self.winId(), isDarkTheme()))

    def on_theme_changed(self) -> None:
        """
        主题变化时的回调函数。
        
        确保Mica效果能在主题变化时正确应用，并更新界面元素。
        """
        # 更新所有自定义组件的样式，确保它们能正确响应主题变化
        for bit_entry in self.bitEntry:
            if hasattr(bit_entry, '_updateStyleSheet'):
                bit_entry._updateStyleSheet()
        
        # 如果有其他需要更新的组件，也可以在这里添加
        pass

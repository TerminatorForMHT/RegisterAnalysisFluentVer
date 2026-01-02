import sys
import os
from views.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

if __name__ == '__main__':
    # 启用高分屏支持
    os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
    os.environ['QT_SCALE_FACTOR_ROUNDING_POLICY'] = 'PassThrough'
    
    # 在创建QApplication之前设置高DPI属性
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())

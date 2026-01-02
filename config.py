from pathlib import Path

ROOT_PATH = Path(__file__).parent

# 应用程序配置
APP_NAME = "数位分析器"
MAIN_ICON = str(ROOT_PATH.joinpath('titleico.svg'))

# 窗口配置
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 720

# 数位配置
MAX_DIGIT = 16  # 最大数位数量
MAX_BIT_PER_DIGIT = 4  # 每数位的比特数
MAX_BIT_COUNT = MAX_DIGIT * MAX_BIT_PER_DIGIT  # 总比特数

# 颜色配置
BIT_HIGH_COLOR = "yellow"
BIT_LOW_COLOR = ""

# 输入限制
MAX_SHIFT_VALUE = 64

# 状态消息
STATUS_OK = "就绪"
STATUS_ERROR = "错误：输入无效"
STATUS_INFO = "信息"

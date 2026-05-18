"""配置文件：存储所有可配置参数"""
from datetime import datetime
# 文件保存路径配置
BASE_SAVE_PATH = "北京电梯数据库"
CONTENT_RESULT_PATH = f"{BASE_SAVE_PATH}/conanda"
WARNINGS_AND_LOG_PATH=f"{BASE_SAVE_PATH}/warnings_and_log"
WARNINGS_PATH=f"{WARNINGS_AND_LOG_PATH}/warnings"
LOG_PATH=f"{WARNINGS_AND_LOG_PATH}/log"



# 输出文件路径
CONTENT_FINAL_FILENAME = f"{CONTENT_RESULT_PATH}/succeed.json"
CONTENT_TEMP_FILENAME_TEMPLATE = f"{CONTENT_RESULT_PATH}/succeed_{{}}.json"
CLAASIFY_FILENAME=f"{BASE_SAVE_PATH}/classify_in_street.json"
OUTPUT_FILE_community=f"{BASE_SAVE_PATH}/url地址/电梯数据_社区_all.json"


#警告和日志保存路径
# 文件运行日志配置
date_str = datetime.now().strftime('%Y%m%d')

URL_WARNING_FILENAME=f"{WARNINGS_PATH}/{date_str}_get_url_warnings.json"
CONTENT_WARNING_FILENAME=f"{WARNINGS_PATH}/{date_str}_get_content_warnings.json"

RUN_LOG_FILENAME=f"{LOG_PATH}/{date_str}_running_log.json"
SAVE_LOG_FILENAME=f"{LOG_PATH}/{date_str}_save_log.json"
WARNINGS_ITEM_FILR=f"{WARNINGS_PATH}/{date_str}_warnings_item.json"


# 输入文件路径
INPUT_URL_FILE = f"{BASE_SAVE_PATH}/classify_in_street.json"
INPUT_CONTENT_FILE=OUTPUT_FILE_community
#INPUT_CONTENT_FILE = "北京电梯数据库\朝阳区_电梯数据_社区.json"

# 页面等待时间配置(毫秒)
BASE_WAIT_TIME = 3000  # 基础等待时间
RANDOM_WAIT_RANGE = (0, 2000)  # 随机等待时间范围
RETRY_WAIT_RANGE = (1, 3)  # 重试时的等待时间范围(秒)
PAGE_LOAD_WAIT = 1000  # 页面加载后等待时间
NEXT_PAGE_WAIT = 200  # 翻页后基础等待时间
NEXT_PAGE_RANDOM = 100  # 翻页后随机等待时间



# 临时保存阈值
TEMP_SAVE_THRESHOLD_CONTENT = 200  # 内容爬取时的临时保存阈值

# 随机User-Agent池
# 模拟不同浏览器/设备的请求标识，降低被识别为爬虫的概率
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.71 Safari/537.36"
]

# 目标网站URL
TARGET_URL = "https://zjw.beijing.gov.cn/bjjs/xxgk/ztzl/ljxqjzdt/jtdt/index.shtml"

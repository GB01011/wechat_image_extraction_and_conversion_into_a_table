import sys
from loguru import logger
import os

# 确保日志目录存在
if not os.path.exists("logs"):
    os.makedirs("logs")

logger.remove() # 移除默认配置
# 控制台输出
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")
# 文件输出，每天一个文件，保留7天
logger.add("logs/system_{time:YYYY-MM-DD}.log", rotation="00:00", retention="7 days", level="INFO", encoding="utf-8")
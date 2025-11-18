"""
日志配置模块
"""
import sys
from pathlib import Path
from loguru import logger
from config import settings


def setup_logger():
    """配置日志系统"""
    
    # 移除默认handler
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True,
    )
    
    # 文件输出
    logger.add(
        settings.LOGS_DIR / "app_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="00:00",  # 每天午夜轮换
        retention="30 days",  # 保留30天
        compression="zip",  # 压缩旧日志
        encoding="utf-8",
    )
    
    # 错误日志单独记录
    logger.add(
        settings.LOGS_DIR / "error_{time:YYYY-MM-DD}.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="00:00",
        retention="90 days",
        compression="zip",
        encoding="utf-8",
    )
    
    return logger


# 初始化日志
log = setup_logger()

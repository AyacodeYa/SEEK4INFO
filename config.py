"""
配置管理模块
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""
    
    # 项目基础路径
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = BASE_DIR / "data"
    CACHE_DIR: Path = BASE_DIR / "cache"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Ollama配置
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="qwen2.5:14b")
    OLLAMA_TEMPERATURE: float = Field(default=0.7)
    OLLAMA_MAX_TOKENS: int = Field(default=2048)
    
    # MCP服务器配置
    MCP_SERVER_HOST: str = Field(default="localhost")
    MCP_SERVER_PORT: int = Field(default=8765)
    
    # 数据库配置
    DATABASE_URL: Optional[str] = Field(default=None)
    
    # 爬虫配置
    CRAWLER_USER_AGENT: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    CRAWLER_TIMEOUT: int = Field(default=30)
    CRAWLER_RETRY_TIMES: int = Field(default=3)
    CRAWLER_DELAY: float = Field(default=1.0)
    
    # 代理配置
    HTTP_PROXY: Optional[str] = Field(default=None)
    HTTPS_PROXY: Optional[str] = Field(default=None)
    
    # 缓存配置
    CACHE_EXPIRY_HOURS: int = Field(default=24)
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO")
    
    # 简历解析配置
    RESUME_MAX_SIZE_MB: int = Field(default=10)
    RESUME_ALLOWED_FORMATS: list[str] = Field(
        default=["pdf", "docx", "doc", "txt"]
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 创建必要的目录
        self.DATA_DIR.mkdir(exist_ok=True)
        self.CACHE_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)


# 全局配置实例
settings = Settings()

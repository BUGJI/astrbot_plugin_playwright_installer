from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import os
import subprocess
import asyncio

@register("playwright_installer", "BUGJI", "自动安装 Playwright 浏览器依赖", "1.0.0")
class PlaywrightInstaller(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """插件初始化时自动安装 playwright chromium 和依赖"""
        logger.info("开始检查并安装 Playwright 环境...")
        
        try:
            # 检查是否已安装 playwright
            result = subprocess.run(
                ["pip", "show", "playwright"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.warning("playwright 未安装，正在安装...")
                install_result = subprocess.run(
                    ["pip", "install", "playwright"],
                    capture_output=True,
                    text=True
                )
                if install_result.returncode != 0:
                    logger.error(f"安装 playwright 失败: {install_result.stderr}")
                    return
            
            # 安装 chromium
            logger.info("正在安装 Playwright Chromium...")
            chromium_result = await asyncio.create_subprocess_exec(
                "playwright", "install", "chromium",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await chromium_result.communicate()
            
            if chromium_result.returncode == 0:
                logger.info("Playwright Chromium 安装成功")
            else:
                logger.error(f"Playwright Chromium 安装失败: {stderr.decode()}")
            
            # 安装依赖
            logger.info("正在安装 Playwright 系统依赖...")
            deps_result = await asyncio.create_subprocess_exec(
                "playwright", "install-deps",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await deps_result.communicate()
            
            if deps_result.returncode == 0:
                logger.info("Playwright 系统依赖安装成功")
            else:
                logger.error(f"Playwright 系统依赖安装失败: {stderr.decode()}")
                
        except FileNotFoundError:
            logger.error("未找到 playwright 命令，请确保已安装 Playwright")
        except Exception as e:
            logger.error(f"安装过程中发生错误: {str(e)}")
        
        logger.info("Playwright 安装流程完成")

    async def terminate(self):
        """插件卸载时的清理操作"""
        logger.info("Playwright Installer 插件已卸载")

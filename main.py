from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import subprocess
import asyncio

# 全局状态
_install_status = "pending"  # pending | installing | success | failed
_install_error = None
_install_progress = []

@register("astrbot_plugin_playwright_installer", "BUGJI", "自动安装 Playwright 浏览器依赖", "1.1.0")
class PlaywrightInstaller(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        logger.info("开始检查并安装 Playwright 环境...")
        asyncio.create_task(self._install_playwright())
        logger.info("Playwright 安装任务已在后台启动")

    async def _install_playwright(self):
        global _install_status, _install_error, _install_progress
        _install_status = "installing"
        _install_progress = []
        _install_error = None

        try:
            # Step 1: 检查 playwright pip 包
            result = subprocess.run(
                ["pip", "show", "playwright"],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                _install_progress.append("⏳ 安装 playwright pip 包...")
                logger.warning("playwright 未安装，正在安装...")
                install_result = subprocess.run(
                    ["pip", "install", "playwright"],
                    capture_output=True, text=True
                )
                if install_result.returncode != 0:
                    _install_status = "failed"
                    _install_error = f"pip install playwright 失败:\n{install_result.stderr}"
                    logger.error(_install_error)
                    return
                _install_progress.append("✅ playwright pip 包安装完成")
            else:
                _install_progress.append("✅ playwright 已安装")

            # Step 2: 安装 Chromium（流式输出实时进度）
            _install_progress.append("⏳ 正在安装 Chromium 浏览器...")
            chromium_ok = await self._run_with_progress(
                ["playwright", "install", "chromium"],
                "Chromium"
            )
            if not chromium_ok:
                _install_status = "failed"
                _install_error = "安装 Chromium 失败，查看日志获取详情"
                return
            _install_progress.append("✅ Chromium 安装完成")

            # Step 3: 安装系统依赖
            _install_progress.append("⏳ 正在安装系统依赖...")
            deps_ok = await self._run_with_progress(
                ["playwright", "install-deps"],
                "系统依赖"
            )
            if not deps_ok:
                _install_status = "failed"
                _install_error = "安装系统依赖失败，查看日志获取详情"
                return
            _install_progress.append("✅ 系统依赖安装完成")

            _install_status = "success"
            logger.info("Playwright 全部安装完成 ✅")

        except FileNotFoundError:
            _install_status = "failed"
            _install_error = "未找到 playwright 命令，请确保 pip install playwright 成功"
            logger.error(_install_error)
        except Exception as e:
            _install_status = "failed"
            _install_error = f"安装过程中发生错误: {str(e)}"
            logger.error(_install_error)

    async def _run_with_progress(self, cmd, label):
        """流式执行命令，实时输出进度到 logger，返回是否成功"""
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,  # 合并 stderr 到 stdout
        )
        output_lines = []
        # 逐行读取，实时打日志
        async for line in proc.stdout:
            text = line.decode("utf-8", errors="replace").rstrip()
            if text:
                logger.info(f"[{label}] {text}")
                output_lines.append(text)
        await proc.wait()
        ok = proc.returncode == 0
        global _install_progress
        _install_progress.append(f"[{label}] 退出码: {proc.returncode}")
        return ok

    # ========== 状态查询指令 ==========
    @filter.command("pw_status")
    async def check_status(self, event: AstrMessageEvent):
        """查询 Playwright 安装状态"""
        global _install_status, _install_error, _install_progress
        emoji = {"pending": "⏸", "installing": "🔄", "success": "✅", "failed": "❌"}
        lines = [
            f"{emoji.get(_install_status, '❓')} **Playwright 安装状态: {_install_status}**",
        ]
        if _install_error:
            lines.append(f"❌ 错误: {_install_error}")
        if _install_progress:
            lines.append("\n📋 进度明细:")
            for p in _install_progress:
                lines.append(f"  {p}")
        yield event.plain_result("\n".join(lines))

    async def terminate(self):
        logger.info("Playwright Installer 插件已卸载")

# 自动安装 Playwright 浏览器依赖

字面意思，在插件载入的时候，执行一遍安装和环境修复流程

适用于 Docker 部署 Astrbot，且容器经常如 Watchtower 自动更新等被破坏容器持久化的用户

# 它做了什么

1. 检查是否已安装 playwright
   通过 `pip show playwright` 检查pip依赖
2. 安装 Chromium
   通过 `playwright install chromium` 安装chromium
3. 安装 Playwright 系统依赖
   通过 `playwright install-deps` 补全依赖

# 你需要吗

如果你也需要好几次执行 `playwright install-deps` 来解决你的问题，那么你就需要这个插件来帮你自动干这个事

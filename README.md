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

# 检查进度

执行 `pw_status` 命令查看安装进度

> 注：可能会误报安装失败，因为有时候执行结束返回值不一定返回0，不过通常显示安装成功的话就是真安装成功了

# 执行重新安装

直接重载插件即可，通常网络稳定的情况下，会随着框架更新自动进行重载，而自动完成安装。

如果你希望让下载更快速，建议手动配置系统代理环境变量


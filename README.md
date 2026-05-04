# DataLeakDetector - 企业管理端

基于 PyQt6 的数据泄露检测系统（企业后台管理端），提供实时监控轮播、风险告警统计、员工行为分析等功能。

📁 项目结构（必须保留的目录）
text
dataleak_app/
├── app/                       # 核心程序目录
│   ├── main.py                # 程序入口
│   ├── load.py                # 登录界面模块
│   ├── app.py                 # 主窗口模块
│   ├── risk_overview.py       # 风险总览页面
│   ├── backlist.py            # 黑名单管理页面
│   ├── models/                # 数据模型（MockData 等）
│   ├── views/                 # 各业务视图
│   ├── widgets/               # 自定义控件（侧边栏、顶部栏等）
│   ├── assets/                # 静态资源（登录轮播图、图标）
│   └── vlm_debug_frames/      # 实时监控示例截图（轮播图用）
├── .gitignore                 # Git 忽略规则
└── README.md                  # 本文件
🔧 环境要求与依赖
Python 3.8 及以上（推荐 3.12）

主要依赖：

PyQt6

requests

安装命令：

bash
pip install PyQt6 requests
如果运行时提示缺少其他模块（如 psutil, pygame 等），请根据报错信息额外安装。

🚀 运行源码（开发调试）
bash
cd app
python main.py
程序启动后将显示登录界面（无账号密码验证，仅供演示），点击“进入控制台”即可查看主界面。

📦 打包为独立 .exe（发布用）
在虚拟环境或干净的 Python 环境中安装 PyInstaller：

bash
pip install pyinstaller
然后执行打包命令（必须在 app 目录下执行）：

bash
cd app
pyinstaller --onefile --windowed --name DataLeakDetector_Enterprise ^
    --add-data "assets;assets" ^
    --add-data "vlm_debug_frames;vlm_debug_frames" ^
    main.py
打包完成后，可执行文件位于 app/dist/DataLeakDetector_monitor.exe。直接双击即可运行，无需 Python 环境。

注意：如果程序需要管理员权限（如监控系统），可在打包命令中加入 --uac-admin 参数。

❓ 常见问题
轮播图片不显示
请检查 app/vlm_debug_frames/ 文件夹是否存在且包含 .jpg 图片。打包时已通过 --add-data 包含该目录。

打包后的 exe 闪退
用命令行窗口运行 exe，查看错误输出。通常是缺少某些动态库（如 PyQt6 的 DLL），可尝试将 Python 安装目录下的 PyQt6/Qt6/bin 中的 DLL 复制到 exe 所在目录。

如何更新项目代码？
使用 git pull。修改代码后如需重新打包，请先删除 build, dist 和 .spec 文件。

📄 许可证
本工具仅供企业内部安全测试与学习使用，请勿用于非法用途。



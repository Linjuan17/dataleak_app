launcher.py放在DataLeakDetector\
main_app.py放在DataLeakDetector\
requirements.txt放在DataLeakDetector\
installer.iss放在DataLeakDetector\
其他两个文件是有更改的部分，直接复制粘贴修改就行，路径：DataLeakDetector\3-RiskHunter\run_upload_detection.py & DataLeakDetector\ScreenMonitor\winows_monitor\web_server.py

运行步骤：
1、以管理员身份运行CMD

2、进入项目，创造虚拟环境（可选）
venv\Scripts\activate

3、安装依赖
pip install -r ../requirements.txt

4、运行main.py
python main_app.py

5、步骤4运行成功后进入软件封装环节，所有代码上的更改都要在这一步之前完成，如果封装后还有更改要再次进行封装

6、安装打包工具
pip install pyinstaller

7、安装依赖
pip install flask flask-cors requests langgraph

8、PyInstaller 打包（要在管理员CMD运行）
pyinstaller -D -w launcher.py ^
--name DataLeakDetector ^
--uac-admin ^
--add-data "1-FrameAnalyzer;1-FrameAnalyzer" ^
--add-data "2-FileTracker;2-FileTracker" ^
--add-data "3-RiskHunter;3-RiskHunter" ^
--add-data "4-ThreatDetector;4-ThreatDetector" ^
--add-data "ScreenMonitor;ScreenMonitor" ^
--hidden-import flask ^
--hidden-import flask_cors ^
--hidden-import requests ^
--hidden-import langgraph

9、运行打包结果
进入dist\DataLeakDetector\，双击DataLeakDetector.exe运行，会弹出管理员权限运行

10、生成安装包
下载 Inno Setup，打开 Inno Setup：File → Open → installer.iss → Build
输出：output\DataLeakDetector_Setup.exe
这个有安装引导

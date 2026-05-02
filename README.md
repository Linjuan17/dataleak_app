launcher.py放在DataLeakDetector\
main_app.py放在DataLeakDetector\
requirements.txt放在DataLeakDetector\
installer.iss放在DataLeakDetector\
path_utils.py放在DataLeakDetector\
assets放在DataLeakDetector\
修改DataLeakDetector\3-RiskHunter\run_upload_detection.py
运行步骤：
1、以管理员身份运行CMD

2、进入项目，创造虚拟环境（可选）  
venv\Scripts\activate

3、安装依赖  
pip install -r ../requirements.txt

4、运行main.py  
python main_app.py

5、步骤4运行成功后进入软件封装环节，所有代码上的更改都要在这一步之前完成，如果封装后还有更改要再次进行封装   
清理封裝包：  
rmdir /s /q build  
rmdir /s /q dist  
del *.spec  

6、安装打包工具  
pip install pyinstaller

7、安装依赖  
pip install flask flask-cors requests langgraph

8、PyInstaller 打包（要在管理员CMD运行）  
pyinstaller launcher.py ^  
--onefile ^  
--noconsole ^  
--uac-admin ^   
--hidden-import sip ^   
--name DataLeakDetector ^   
--add-data "ScreenMonitor;ScreenMonitor" ^   
--add-data "1-FrameAnalyzer;1-FrameAnalyzer" ^    
--add-data "2-FileTracker;2-FileTracker" ^   
--add-data "3-RiskHunter;3-RiskHunter" ^  
--add-data "4-ThreatDetector;4-ThreatDetector" ^   
--add-data "icons;icons"   

9、运行打包结果  
进入dist\DataLeakDetector\，双击DataLeakDetector.exe运行，会弹出管理员权限运行

10、生成安装包  
下载 Inno Setup，打开 Inno Setup：File → Open → installer.iss → Build  
输出：output\DataLeakDetector_Setup.exe  
这个有安装引导  

封装后的软件包太大了传不上来，大家自己在本地封装一下吧

import threading
import time
import frida
import os
import psutil
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
import json
"""
processname = "MinecraftLegends.Windows.exe"
processpath = r"D:\Download\Minecraft Legends\MinecraftLegends.Windows.exe"
scriptpath = "D:\Download\yqqs\legends.js"
"""
processname = "reverse_engineers_test.exe"
processpath = r"C:\Users\O2C14\source\repos\reverse_engineers_test\x64\Debug\reverse_engineers_test.exe"
scriptpath = "D:\Download\yqqs\legends.js"
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.buttons = []
        
    def load_ui(self,myQWidgetjson):
        # 读取JSON文件
        data = json.loads(myQWidgetjson)

        # 创建控件
        for button_data in data['buttons']:
            button = QPushButton(button_data['text'], self)
            button.move(button_data['x'], button_data['y'])
            button.resize(button_data['width'], button_data['height'])
            self.buttons.append(button)
            
        # 显示窗口
        self.show()

    def reload_ui(self,myQWidgetjson):
        # 清空旧的控件列表
        for button in self.buttons:
            button.deleteLater()
        self.buttons = []
        # 重新读取JSON文件并创建新的控件列表
        data = json.loads(myQWidgetjson)

        for button_data in data['buttons']:
            button = QPushButton(button_data['text'], self)
            button.move(button_data['x'], button_data['y'])
            button.resize(button_data['width'], button_data['height'])
            self.buttons.append(button)

        # 重新绘制窗口
        self.update()
def on_message(message, data):
    if message["type"] == "send":
        print("{}".format(message["payload"]))


class myapplication:
    pid = 0
    QWidgetjson=''
    def __init__(self):
        while self.pid == 0:
            os.startfile(processpath)
            pids = psutil.process_iter()
            for apid in pids:
                if apid.name() == processname and apid.status() != "stopped":
                    self.pid = apid.pid
        print("进程PID:", self.pid)

        self.session, self.script,self.scripterror = self.attach_and_load_script()

        self.last_modified_time = os.path.getmtime(scriptpath)

    def scriptreload(self):
        try:
            while True:
                time.sleep(2)
                self.modified_time = os.path.getmtime(scriptpath)
                if self.modified_time != self.last_modified_time:
                    self.last_modified_time = self.modified_time
                    if not self.scripterror:
                        self.script.unload()
                        self.session.detach()
                    self.session, self.script,self.scripterror = self.attach_and_load_script()
        except KeyboardInterrupt:
            pass
        finally:
            self.session.detach()
    def attach_and_load_script(self):
        session = frida.attach(self.pid)
        js_file = open(scriptpath, encoding='utf-8')
        js_code = js_file.read()
        js_file.close()
        script = session.create_script(js_code)
        scripterror=False
        try:
            script.load()
            script.exports_sync.start(processname)
            script.on('message', on_message)
        except Exception as e:
            print(f"脚本错误：{str(e)}")
            script.unload()
            session.detach()
            scripterror=True
        #finally:
        return session, script,scripterror

def main():
    mainapplication = myapplication()
    app = QApplication(sys.argv)
    widget = MyWidget()
    # 在单独的线程中启动脚本重载函数
    script_reload_thread = threading.Thread(target=mainapplication.scriptreload, daemon=True)
    script_reload_thread.start()
    while mainapplication.QWidgetjson=='':
        time.sleep(1)
    widget.load_ui(mainapplication.QWidgetjson)
    widget.setGeometry(100, 100, 300, 200)

    # 开始事件循环
    while True:
        app.processEvents()
        widget.reload_ui(mainapplication.QWidgetjson)
        time.sleep(0.1)
        if not widget.isVisible():
            break

    # 程序退出
    sys.exit()
if __name__ == "__main__":
    main()

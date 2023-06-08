import threading
import time
import frida
import os
import psutil
import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton,QWidget,QVBoxLayout, QLabel
import json
"""
processname = "MinecraftLegends.Windows.exe"
processpath = r"D:\Download\Minecraft Legends\MinecraftLegends.Windows.exe"
scriptpath = "D:\Download\yqqs\legends.js"
"""
processname = "reverse_engineers_test.exe"
processpath = r"C:\Users\O2C14\source\repos\reverse_engineers_test\x64\Debug\reverse_engineers_test.exe"
scriptpath = "D:\Download\yqqs\legends.js"
QWidgetjsonpath="D:\Download\yqqs\QWidgetjson.json"
class FlieWatcher(QThread):
    data_changed = pyqtSignal()
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.last_data = None
        self.last_modified_time = os.path.getmtime(self.file_path)
    def run(self):
        while True:
            time.sleep(2)
            modified_time = os.path.getmtime(self.file_path)
            if modified_time != self.last_modified_time:
                self.last_modified_time=modified_time
                self.data_changed.emit()
def on_message(message, data):
    if message['type'] == 'send':
        print(message['payload'])
    elif message['type'] == 'error':
        print(message['stack'])
class MyWindow(QWidget):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self._load_json()

        # 创建文件监视器并启动线程
        self.watcher = FlieWatcher(file_path)
        self.watcher.data_changed.connect(self.on_data_changed)
        self.watcher.start()

    def on_data_changed(self):
        self._update_window()

    def _load_json(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def _update_window(self):
        # 清空布局中的控件
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            widget.setParent(None)

        # 重新添加控件
        self._load_json()
        for item in self.data['items']:
            label = QLabel(item['text'])
            self.layout.addWidget(label)
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # 从 JSON 文件中读取数据
        with open(file_path, 'r',encoding='utf-8') as f:
            data = json.load(f)

        # 逐个创建控件并添加到布局
        for item in data['items']:
            label = QLabel(item['text'])
            self.layout.addWidget(label)

        # 创建 JsonWatcher 对象并启动线程
        self.watcher = FlieWatcher(file_path)
        self.watcher.data_changed.connect(self.on_data_changed)
        self.watcher.start()

    def on_data_changed(self):
        # 更新窗口内容
        for i in range(self.layout.count()):
            self.layout.itemAt(i).widget().deleteLater()
        with open(self.file_path, 'r',encoding='utf-8') as f:
            data = json.load(f)
        for item in data['items']:
            label = QLabel(item['text'])
            self.layout.addWidget(label)
class myapplication:
    pid = 0
    QWidgetjson=''
    def __init__(self):
        if self.checkprocess()==0:
            os.startfile(processpath)
        while self.checkprocess()==0:pass
        print("进程PID:", self.pid)
        self.session, self.script,self.scripterror = self.attach_and_load_script()
        self.last_modified_time = os.path.getmtime(scriptpath)
        self.watcher = FlieWatcher(scriptpath)
        self.watcher.data_changed.connect(self.scriptreload)
        self.watcher.start()
    def checkprocess(self):
        pids = psutil.process_iter()
        for apid in pids:
            if apid.name() == processname and apid.status() != "stopped":
                self.pid = apid.pid
                return apid.pid
        return 0

    def scriptreload(self,):
        if not self.scripterror:
            self.script.unload()
            self.session.detach()
        self.session, self.script,self.scripterror = self.attach_and_load_script()
    def attach_and_load_script(self):
        #print(self.pid)
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
        finally:
            pass
        return session, script,scripterror
def main():
    myapp = myapplication()
    app = QApplication(sys.argv)
    window = MyWindow(QWidgetjsonpath)
    window.show()
    window.resize(400,300)
    try:
        ret_code = app.exec_()
    except KeyboardInterrupt:
        myapp.session.detach()
        sys.exit()
    else:
        if ret_code == 0:
            # 退出事件循环时断开 Frida session
            myapp.session.detach()
if __name__ == "__main__":
    main()

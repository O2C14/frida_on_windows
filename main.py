import threading
import time
import frida
import os
import psutil
import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton,QWidget,QVBoxLayout, QLabel
import json
processname = "reverse_engineers_test.exe"
processpath = r"C:\Users\O2C14\source\repos\reverse_engineers_test\x64\Debug\reverse_engineers_test.exe"
scriptpath = "D:\Download\yqqs\legends.js"
QWidgetjsonpath="D:\Download\yqqs\QWidgetjson.json"
class JsonWatcher(QThread):
    data_changed = pyqtSignal()
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.last_data = None
        self.last_modified_time = os.path.getmtime(QWidgetjsonpath)
    def run(self):
        while True:
            time.sleep(2)
            self.modified_time = os.path.getmtime(QWidgetjsonpath)
            if self.modified_time != self.last_modified_time:
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

        # 从 JSON 文件中读取数据
        with open(file_path, 'r',encoding='utf-8') as f:
            data = json.load(f)

        # 逐个创建控件并添加到布局
        for item in data['items']:
            label = QLabel(item['text'])
            self.layout.addWidget(label)

        # 创建 JsonWatcher 对象并启动线程
        self.watcher = JsonWatcher(file_path)
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
    def checkprocess(self):
        pids = psutil.process_iter()
        for apid in pids:
            if apid.name() == processname and apid.status() != "stopped":
                self.pid = apid.pid
                return apid.pid
        return 0

    def scriptreload(self,):
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
    mainapplication = myapplication()
    script_reload_thread = threading.Thread(target=mainapplication.scriptreload, daemon=True)
    script_reload_thread.start()
    app = QApplication(sys.argv)
    window = MyWindow(QWidgetjsonpath)
    window.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()

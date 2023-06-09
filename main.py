import time,frida,os,psutil,sys,json
from changewidgets import changewidget
from PyQt5.QtCore import QThread, pyqtSignal,QObject
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout

processname = "reverse_engineers_test.exe"
processpath = r"C:\Users\O2C14\source\repos\reverse_engineers_test\x64\Debug\reverse_engineers_test.exe"
scriptpath = "D:\Download\yqqs\legends.js"
QWidgetjsonpath="D:\Download\yqqs\QWidgetjson.json"

def on_message(message, data):
    if message['type'] == 'send':#消息分类
        tmpdic=message['payload']
        if "widget" in tmpdic:
            trans.message_changed.emit(tmpdic)
        elif "message" in tmpdic:
            print(message['payload'])
    elif message['type'] == 'error':
        print(message['stack'])

class transimtmessage(QObject):
    message_changed = pyqtSignal(dict)
global trans
trans =transimtmessage()
class FlieWatcher(QThread):
    data_changed = pyqtSignal()
    def __init__(self, file_path,delay, parent=None):
        super().__init__(parent)
        self.delay=delay
        self.file_path = file_path
        self.last_data = None
        self.last_modified_time = os.path.getmtime(self.file_path)
    def run(self):
        while True:
            time.sleep(self.delay)
            modified_time = os.path.getmtime(self.file_path)
            if modified_time != self.last_modified_time:
                self.last_modified_time=modified_time
                self.data_changed.emit()
class MyWindow(QWidget):
    def __init__(self, file_path,script, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.script=script
        # 从 JSON 文件中读取数据
        with open(file_path, 'r',encoding='utf-8') as f:
            self.data = json.load(f)
            self.data=self.data['main']
        changewidget(self)
        # 检测布局改动
        self.watcher = FlieWatcher(file_path,2)
        self.watcher.data_changed.connect(self.on_data_changed)
        self.watcher.start()
        trans.message_changed.connect(self.on_send_message)
    def on_send_message(self,jsWidget):
        #传递js中的Widget
        jsWidget=json.loads(jsWidget['widget'])
        print(jsWidget)
    def on_data_changed(self):
        # 更新窗口内容
        for i in range(self.layout.count()):
            self.layout.itemAt(i).widget().deleteLater()
        with open(self.file_path, 'r',encoding='utf-8') as f:
            self.data = json.load(f)
            self.data=self.data['main']
        changewidget(self)
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
        self.watcher = FlieWatcher(scriptpath,2)
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
            script.on('message',on_message)
        except Exception as e:
            print(f"脚本错误：{str(e)}")
            script.unload()
            session.detach()
            scripterror=True
        finally:
            pass
        return session, script,scripterror
def main():
    global myapp
    myapp=myapplication()
    app = QApplication(sys.argv)
    window = MyWindow(QWidgetjsonpath,myapp.script)
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

import time,frida,os,psutil,sys,json,pickle
from changewidgets import changewidget,updatalist
from PyQt5.QtCore import QThread, pyqtSignal,QObject
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout

processname=
processpath=
scriptpath = 
QWidgetjsonpath=

def on_message(message, data):#因为on_message只能是全局函数(写进类就会引入self这个参数然后报错)
    if message['type'] == 'send':#消息分类
        tmpdic=message['payload']
        if "callfunc" in tmpdic: 
            转发消息.message_changed.emit(tmpdic)
        elif "message" in tmpdic:
            print(message['payload'])
    elif message['type'] == 'error':
        print(message['stack'])


class mySignal(QObject):
    message_changed = pyqtSignal(dict)
    reloadscript = pyqtSignal(bytes)
global 转发消息
转发消息 =mySignal()#转发消息

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
    def __init__(self, file_path,app, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        # 从 JSON 文件中读取数据
        with open(file_path, 'r',encoding='utf-8') as f:
            self.data = json.load(f)
            self.data=self.data['main']
        self.myapp=app    
        changewidget(self)
        
        # 检测布局改动
        self.watcher = FlieWatcher(file_path,2)
        self.watcher.data_changed.connect(self.on_data_changed)
        self.watcher.start()
        
        转发消息.message_changed.connect(self.receive_message)
        转发消息.reloadscript.connect(self.onreloadscript)
    def onreloadscript(self,app):
        self.myapp=pickle.loads(app)
        #self.on_data_changed()
    def receive_message(self,message):
        return
        print(message)
    def on_data_changed(self):
        # 更新窗口内容
        for i in range(self.layout.count()):#清除原有布局
            self.layout.itemAt(i).widget().deleteLater()
        with open(self.file_path, 'r',encoding='utf-8') as f:
            self.data = json.load(f)
            self.data=self.data['main']
        changewidget(self)

class myapplication:
    pid = 0
    QWidgetjson=''
    spawnmode=True
    def __init__(self):
        if self.checkprocess()==0:
            if self.spawnmode==True:
                self.pid = frida.spawn(processpath)
            else:
                os.startfile(processpath)
                while self.checkprocess()==0:pass
        else:
            self.spawnmode=False
        print("进程PID:", self.pid)
        self.attach_and_load_script()
        self.watcher = FlieWatcher(scriptpath,2)
        self.watcher.data_changed.connect(self.scriptreload)
        self.watcher.start()
        转发消息.message_changed.connect(self.receive_message)
    def receive_message(self,message):
        #return
        if(message['callfunc']=='updatalist'):
            updatalist(message['arg'],self)
            print(message)
    def checkprocess(self):
        pids = psutil.process_iter()
        for apid in pids:
            if apid.name() == processname and apid.status() != "stopped":
                self.pid = apid.pid
                return apid.pid
        return 0
    def scriptreload(self):
        if not self.spawnmode:
            if not self.session.is_detached:
                self.script.exports_sync.unloadscript()
                self.script.unload()
                self.session.detach()
            self.attach_and_load_script()
        
    def attach_and_load_script(self):
        #print(self.pid)
        self.session = frida.attach(self.pid)
        js_file = open(scriptpath, encoding='utf-8')
        js_code = js_file.read()
        js_file.close()
        self.script =  self.session.create_script(js_code)
        try:
            self.script.load()
            #script.exports_sync.start()
            self.script.on('message',on_message)
            if self.spawnmode:
                frida.resume(self.pid)
                #转发消息.reloadscript.emit(pickle.dumps(self.script))
        except Exception as e:
            print(f"脚本错误：{str(e)}")
            self.script.unload()
            self.session.detach()
        finally:
            pass

def main():
    global myapp
    myapp=myapplication()
    app = QApplication(sys.argv)
    window = MyWindow(QWidgetjsonpath,myapp)
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

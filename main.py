import time,frida,os,psutil,sys,json,pickle
from PyQt5.QtCore import QThread, pyqtSignal,QObject,Qt
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QLabel, QComboBox, QSlider, QListWidget, QScrollBar, QMessageBox,QListWidgetItem

QWidgetjsonpath="D:\\Download\\yqqs\\QWidgetjson.json"
configpath="D:\\Download\\yqqs\\hookconfig\\flutter.json"
#因为on_message只能是全局函数(写进类就会引入self这个参数然后报错)
def on_message(message, data):
    if message['type'] == 'send':#消息分类
        tmpdic=message['payload']
        if "callfunc" in tmpdic: 
            转发消息.message_changed.emit(tmpdic)
        elif "message" in tmpdic:
            print(message['payload'])
    elif message['type'] == 'error':
        print(message['stack'])


class globalSignal(QObject):
    message_changed = pyqtSignal(dict)
    reloadscript = pyqtSignal(bytes)
    sendmessage = pyqtSignal(dict)
global 转发消息
转发消息 =globalSignal()#转发消息

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
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        # 从 JSON 文件中读取数据
        with open(file_path, 'r',encoding='utf-8') as f:
            self.data = json.load(f)
            self.data=self.data['main']
        self.changewidget()
        
        # 检测布局文件改动
        self.watcher = FlieWatcher(file_path,2)
        self.watcher.data_changed.connect(self.on_data_changed)
        self.watcher.start()
        
        转发消息.message_changed.connect(self.receive_message)
        转发消息.reloadscript.connect(self.onreloadscript)
        
    def onreloadscript(self,app):
        self.myapp=pickle.loads(app)
        #self.on_data_changed()
    def receive_message(self,message):
        if(message['callfunc']=='updatalist'):
            #self.updatalist(message['arg'])
            print(message)
    def on_data_changed(self):
        # 更新窗口内容
        for i in range(self.layout.count()):#清除原有布局
            self.layout.itemAt(i).widget().deleteLater()
        with open(self.file_path, 'r',encoding='utf-8') as f:
            self.data = json.load(f)
            self.data=self.data['main']
        self.changewidget(self)
    def setwidgetAttribute(self,widget, item):
        if not ('x' in item):
            item['x'] = 50
        if not ('y' in item):
            item['y'] = 50
        if not ('width' in item):
            item['width'] = 100
        if not ('height' in item):
            item['height'] = 30
        widget.move(item['x'], item['y'])
        widget.resize(item['width'], item['height'])
        return widget
    def updatalist(self,arg):
        for i in range(self.layout.count()):#清除原有布局
            self.layout.itemAt(i).widget().deleteLater()
        arg['id']
        arg['item']
    def onwidgetchanged(self):
        sender = self.sender()
        aMessage={"null":"null"}
        if isinstance(sender, QSlider):
            # 处理 QSlider 发送的信号
            guid = int(sender.objectName())
            #print(sender.objectName())
            #return
            value = sender.value()
            aMessage = {
            "event": "changeslider",
            "id": guid ,
            "value": value
            }
        elif isinstance(sender, QPushButton):
            #return
            # 处理 QPushButton 发送的信号
            guid = int(sender.objectName())
            aMessage = {
            "event": "clickbuttons",
            "id": guid
            }
        转发消息.sendmessage.emit(aMessage)
    def changewidget(self):
        # 逐个创建控件并添加到布局
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(15)
        print('正在刷新窗口')
        for key in self.data:
            if key['type'] == 'Label':
                label = QLabel(key['text'])
                label.setFont(font)
                label.setObjectName(str(key['id']))
                label=self.setwidgetAttribute(label, key)
                self.layout.addWidget(label)
            if key['type'] == 'Buttons':
                button = QPushButton(key['text'])
                button.setFont(font)
                button.setObjectName(str(key['id']))
                button.clicked.connect(self.onwidgetchanged)
                button=self.setwidgetAttribute(button, key)
                self.layout.addWidget(button)
            if key['type'] == 'ComboBox':
                combobox = QComboBox()
                combobox.setFont(font)
                combobox.setObjectName(str(key['id']))
                combobox=self.setwidgetAttribute(combobox, key)
                for item in key['item']:
                    combobox.addItem(item)
                self.layout.addWidget(combobox)
            if key['type'] == 'Slider':
                Slider = QSlider()
                Slider.setFont(font)
                Slider=self.setwidgetAttribute(Slider, key)
                Slider.setMinimum(key['minimum'])
                Slider.setMaximum(key['maximum'])
                Slider.setSingleStep(key['singleStep'])
                Slider.setPageStep(key['pageStep'])
                Slider.setObjectName(str(key['id']))
                if (key['orientation'] == "Horizontal"):
                    Slider.setOrientation(Qt.Horizontal)
                else:
                    Slider.setOrientation(Qt.Vertical)
                Slider.valueChanged.connect(self.onwidgetchanged)
                self.layout.addWidget(Slider)
            if key['type'] == 'ListWidget':
                List = QListWidget()
                List.setVerticalScrollBar(QScrollBar(List))
                List.setObjectName(str(key['id']))
                List.addItems(key['item'])
                self.layout.addWidget(List)


class myapplication:
    pid = 0
    QWidgetjson=''
    spawnmode=True
    def __init__(self):            
        global QWidgetjsonpath
        with open(configpath, 'r',encoding='utf-8') as hookconfig:
            configread = json.load(hookconfig)
            self.processname = configread['processname']
            self.processpath = configread['processpath']
            self.scriptpath = configread['scriptpath']
            self.spawnmode = configread['spawnmode']
            QWidgetjsonpath = configread['QWidgetjsonpath']
        if self.checkprocess()==0:
            if self.spawnmode==True:
                self.pid = frida.spawn(self.processpath)
            else:
                os.startfile(self.processpath)
                while self.checkprocess()==0:pass
        else:
            self.spawnmode=False
        print("进程PID:", self.pid)
        self.attach_and_load_script()
        self.watcher = FlieWatcher(self.scriptpath,2)
        self.watcher.data_changed.connect(self.scriptreload)
        self.watcher.start()
        转发消息.message_changed.connect(self.receive_message)
        转发消息.sendmessage.connect(self.sendmessage)
    def sendmessage(self,message):
        self.script.exports_sync.onchange(message)
    def receive_message(self,message):
        return
        if(message['callfunc']=='updatalist'):
            updatalist(message['arg'],self)
            print(message)
    def checkprocess(self):
        pids = psutil.process_iter()
        for apid in pids:
            if apid.name() == self.processname and apid.status() != "stopped":
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
        js_file = open(self.scriptpath, encoding='utf-8')
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

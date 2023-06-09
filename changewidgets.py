from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QLabel,QComboBox,QSlider,QListWidget,QScrollBar,QMessageBox

def setwidgetAttribute(widget,item):
    if not ('x' in item):
        item['x']=50
    if not ('y' in item):
        item['y']=50
    if not ('width' in item):
        item['width']=100
    if not ('height' in item):
        item['height']=30
    widget.move(item['x'],item['y'])
    widget.resize(item['width'],item['height'])
def changewidget(widgetdate):
    # 逐个创建控件并添加到布局
    font = QFont()
    font.setFamily("Consolas")
    font.setPointSize(15)
    print('正在刷新窗口')
    for key in widgetdate.data:
        if key['type']=='Label':
            label=QLabel(key['text'])
            label.setFont(font)
            setwidgetAttribute(label,key)
            widgetdate.layout.addWidget(label)
        if key['type']=='Buttons':
            button=QPushButton(key['text'])
            button.setFont(font)
            aMessage='You clicked the OK button.'
            button.clicked.connect(lambda: widgetdate.script.exports_sync.message(aMessage))
            setwidgetAttribute(button,key)
            widgetdate.layout.addWidget(button)
        if key['type']=='ComboBox':
            combobox=QComboBox()
            combobox.setFont(font)
            setwidgetAttribute(combobox,key)
            for item in key['item']:
                combobox.addItem(item)
            widgetdate.layout.addWidget(combobox)
        if key['type']=='Slider':
            Slider=QSlider()
            Slider.setFont(font)
            setwidgetAttribute(Slider,key)
            Slider.setMinimum(key['minimum'])
            Slider.setMaximum(key['maximum'])
            Slider.setSingleStep(key['singleStep'])
            Slider.setPageStep(key['pageStep'])
            if(key['orientation']=="Horizontal"):
                Slider.setOrientation(Qt.Horizontal)
            else:
                Slider.setOrientation(Qt.Vertical)
            widgetdate.layout.addWidget(Slider)
        if key['type']=='ListWidget':
            List=QListWidget()
            List.setVerticalScrollBar(QScrollBar(List))
            List.addItems(key['item'])
            widgetdate.layout.addWidget(List)
def showMessage(title, message):
    print(title,message)

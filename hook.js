function alog(arg) {
    console.log(arg);
}
var BaseAddr = null;
function main() {
    rpc.exports = {
        start: function (processname) {
            alog('脚本加载成功');
            while (BaseAddr === null) {
                console.log("尝试查找" + processname + "的基址");
                BaseAddr = Module.findBaseAddress(processname);
            }
            alog("基址: " + BaseAddr);
            //hook_function();
            //hooktest();
            setTimeout(sendwidget, 3000);
        },
        message:function(messagedic){
            alog(messagedic);
        }
    };
}
var QWidget = {
    "modmenu": [
        {
            "type": "Label",
            "text": "JS菜单",
            "x": 50,
            "y": 100,
            "width": 100,
            "height": 30
        },
        {
            "type": "Buttons",
            "text": "js按钮",
            "x": 50,
            "y": 100,
            "width": 100,
            "height": 30
        }
    ]

}
function sendwidget() {
    send({
        'widget': JSON.stringify(QWidget)
    });
}
function sendmessage(message) {
    send({
        'message': message
    });
}
main();

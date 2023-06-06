import time
import frida
import sys
import os
import psutil

processname = "MinecraftLegends.Windows.exe"
processpath = r"D:\Download\Minecraft Legends\MinecraftLegends.Windows.exe"
scriptpath = "D:\Download\yqqs\legends.js"

def attach_and_load_script(pid):
    session = frida.attach(pid)
    js_file = open(scriptpath, encoding='utf-8')
    js_code = js_file.read()
    js_file.close()
    script = session.create_script(js_code)
    script.load()
    scripterror=False
    try:
        script.exports_sync.init(processname)
    except Exception as e:
        print(f"发生了异常：{str(e)}")
    finally:
        session.detach()
        scripterror=True
    return session, script,scripterror

def main():
    pid = 0
    while pid == 0:
        os.startfile(processpath)
        pids = psutil.process_iter()
        for apid in pids:
            if apid.name() == processname and apid.status() != "stopped":
                pid = apid.pid
    print("进程PID:", pid)

    session, script,scripterror = attach_and_load_script(pid)

    last_modified_time = os.path.getmtime(scriptpath)

    try:
        while True:
            time.sleep(2)
            modified_time = os.path.getmtime(scriptpath)
            if modified_time != last_modified_time:
                last_modified_time = modified_time
                if(scripterror==False):
                    script.unload()
                    session.detach()
                session, script,scripterror = attach_and_load_script(pid)
                print("重载脚本成功")
    except KeyboardInterrupt:
        pass
    finally:
        session.detach()
if __name__ == "__main__":
    main()

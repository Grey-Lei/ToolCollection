# -*- coding: utf-8 -*-
import ctypes
import json
import subprocess
import sys
import tkinter as tk
from time import sleep
from tkinter import messagebox
import winreg


class SwitchEnv(object):
    def __init__(self):
        self.pre_server = "https://sp.pre.eagleyun.cn"
        self.prod_server = "https://sp.eagleyun.cn"
        self.private_server = None

        # 1.创建主窗口
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.__on_closing)

    def create_button(self):
        self.root.title("Server环境切换工具")
        # 创建一个Frame作为按钮容器
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, anchor="s")
        # 创建按钮框
        button1 = tk.Button(button_frame, text="正式环境", command=lambda: self.set_sp_server(button1))
        button1.pack(side=tk.LEFT, padx=5, pady=10)
        button2 = tk.Button(button_frame, text="预发环境", command=lambda: self.set_sp_server(button2))
        button2.pack(side=tk.LEFT, padx=5, pady=10)
        button3 = tk.Button(button_frame, text="私有化环境", command=lambda: self.set_sp_server(button3))
        button3.pack(side=tk.LEFT, padx=5, pady=10)
        # 固定窗口大小
        self.root.geometry("500x150")
        # 运行主循环
        self.root.mainloop()

    def __on_closing(self):
        if tk.messagebox.askokcancel("退出", "确定要退出吗？"):
            self.root.destroy()
            sys.exit()

    @staticmethod
    def modify_server(server):
        file_path = r'C:\Program Files\YunShu\SetupSettings.json'
        # 读取文件内容
        with open(file_path, 'r') as file:
            settings = json.load(file)
        # 修改文件内容
        settings['Server'] = server
        # 写入文件
        try:
            with open(file_path, 'w') as file:
                json.dump(settings, file, indent=4)
        except Exception as e:
            print(e)
            messagebox.showinfo("提示", "请确认实例是否已开启自保护功能")
            sys.exit()

    def set_sp_server(self, button):
        if button.cget("text") == "正式环境":
            # 切换至正式环境
            print("server:", self.prod_server)
            self.modify_server(self.prod_server)
            self.root.destroy()
        elif button.cget("text") == "预发环境":
            # 切换至预发环境
            print("server:", self.pre_server)
            self.modify_server(self.pre_server)
            self.root.destroy()
        elif button.cget("text") == "私有化环境":
            self.create_input_window()
            # 切换至私有化环境
            print("server:", self.private_server)
            self.modify_server(self.private_server)
            self.root.destroy()

    @staticmethod
    def kill_process():
        # 定义进程名称或进程ID（PID）
        process_name = "YunShu*"
        # 根据进程名称或PID查找进程ID
        cmd = f'tasklist /FI "IMAGENAME eq {process_name}" /NH'
        output = subprocess.check_output(cmd, shell=True).decode('utf-8')
        print(output)
        process_ids = [line.split()[-5] for line in output.splitlines() if line]
        # 杀死进程
        for pid in process_ids:
            print(pid)
            try:
                subprocess.run(f'taskkill /F /PID {pid}', shell=True, check=True)
                sleep(1)
                # 执行成功
                print("命令执行成功:", pid)
            except subprocess.CalledProcessError as e:
                print("命令执行失败:", e.returncode)
                print("失败原因:", e.output)
                raise "进程kill失败"
            except Exception as e:
                # 捕捉其他异常
                raise ("发生异常:", str(e))

    def on_confirm_click(self):
        self.private_server = self.input_text.get()
        self.input_window.destroy()  # 销毁弹窗

    def create_input_window(self):
        self.input_window = tk.Toplevel(self.root)
        self.input_text = tk.StringVar()
        self.input_entry = tk.Entry(self.input_window, textvariable=self.input_text)
        self.input_window.title("请输入server地址")
        self.input_window.geometry("300x80")
        self.input_entry.pack(pady=10, padx=10, fill=tk.X)

        confirm_button = tk.Button(self.input_window, text="确 认", command=self.on_confirm_click)
        confirm_button.pack(pady=5)
        self.input_entry.focus()
        # 等待窗口关闭
        self.input_window.wait_window()

    @staticmethod
    def start_exe():
        exe_path = r'C:\Program Files\YunShu\YunShu.exe'
        # 启动 .exe 文件，并等待其执行完成
        try:
            subprocess.Popen(exe_path, shell=True)
            sys.exit()
        except Exception as e:
            messagebox.showinfo("提示", "进程重新启动失败")
            print("启动失败:", e)

    def main(self):
        self.create_button()
        self.kill_process()
        sleep(3)
        self.start_exe()


if __name__ == '__main__':
    # 判断是否以管理员权限运行脚本
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        messagebox.showinfo("提示", "请以管理员身份运行程序")
        sys.exit()

    # 判断当前客户端是否已注销
    # 1.未注销，提示用户手动注销
    key_path = r'SOFTWARE\WOW6432Node\YunShu'
    value_name = "Logout"

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        # 读取指定值
        value, value_type = winreg.QueryValueEx(key, value_name)
        # 关闭注册表键
        winreg.CloseKey(key)
        # 返回读取到的值和值类型
    except FileNotFoundError:
        print(f"注册表键 {key_path} 或值 {value_name} 不存在。")
        sys.exit()
    except PermissionError:
        print(f"没有足够的权限访问注册表键 {key_path}。")
        sys.exit()
    except Exception as e:
        print(f"读取注册表时发生错误: {e}")
        sys.exit()
    if value == 0:
        messagebox.showinfo("提示", "请注销客户端后再试！")
        sys.exit()

    obj = SwitchEnv()
    obj.main()




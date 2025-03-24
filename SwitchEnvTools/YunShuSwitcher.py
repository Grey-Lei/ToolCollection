import os
import sys
import json
import ctypes
import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
import psutil
import time
import winreg

# 常量定义
SETTINGS_FILE_PATH = r"C:\Program Files\YunShu\SetupSettings.json"
YUNSHU_EXE_PATH = r"C:\Program Files\YunShu\YunShu.exe"
API_PROXY_PATH = r"C:\Windows\pigeon\api_proxy.dat"
TASK_NAME = "YunShu Service Task Scheduler"
PRODUCTION_URL = "https://sp.eagleyun.cn"
PRE_URL = "https://sp.pre.eagleyun.cn"

def is_admin():
    """检查程序是否以管理员身份运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员身份重新运行程序"""
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def update_config_file(server_url):
    """更新配置文件中的服务器地址"""
    try:
        with open(SETTINGS_FILE_PATH, 'r', encoding='utf-8-sig') as file:
            config = json.load(file)
        
        config["Server"] = server_url
        
        with open(SETTINGS_FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent='\t')
        
        return True
    except PermissionError:
        messagebox.showerror("错误", "更新配置文件失败: 请尝试关闭客户端自保护功能后重试")
        return False
    except Exception as e:
        messagebox.showerror("错误", f"更新配置文件失败: {e}")
        return False

def disable_scheduled_task():
    """禁用Windows计划任务"""
    try:
        subprocess.run(
            ['schtasks', '/Change', '/TN', TASK_NAME, '/DISABLE'], 
            check=False, 
            capture_output=True
        )
        return True
    except Exception as e:
        messagebox.showerror("错误", f"禁用计划任务失败: {e}")
        return False

def kill_yunshu_processes():
    """结束所有以YunShu开头的进程"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower().startswith('yunshu'):
                    process = psutil.Process(proc.info['pid'])
                    process.kill()
            except psutil.NoSuchProcess as e:
                # 进程不存在，忽略
                pass
            except psutil.AccessDenied as e:
                messagebox.showerror("错误", "结束进程失败: 请尝试客户端关闭自保护功能后重试")
                return False  # 返回False而不是终止程序
            except psutil.ZombieProcess as e:
                messagebox.showerror("错误", f"结束僵尸进程失败: {e}")
                return False  # 返回False而不是终止程序
        return True
    except Exception as e:
        messagebox.showerror("错误", f"结束进程失败: {e}")
        return False  # 返回False而不是终止程序

def restart_yunshu():
    """重启云枢应用程序"""
    try:
        if os.path.exists(YUNSHU_EXE_PATH):
            subprocess.Popen(YUNSHU_EXE_PATH)
            return True
        else:
            messagebox.showwarning("警告", f"无法找到云枢应用程序：{YUNSHU_EXE_PATH}")
            return False
    except Exception as e:
        messagebox.showerror("错误", f"重启云枢失败: {e}")
        return False

def check_logout_status():
    """检查注册表中的 Logout 值"""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\YunShu", 0, winreg.KEY_ALL_ACCESS) as key:
            logout_value, _ = winreg.QueryValueEx(key, "Logout")
            # 仅在 Logout 值为 0 时修改为 1
            if logout_value == 0:
                winreg.SetValueEx(key, "Logout", 0, winreg.REG_DWORD, 1)
                print("Logout 值已修改为 1。")
    except FileNotFoundError:
        print("注册表项未找到，继续执行。")
    except Exception as e:
        messagebox.showerror("错误", f"检查注册表失败: {e}")
        sys.exit(1)

def switch_environment(server_url):
    """切换环境的主要流程"""
    # 1. 禁用任务计划程序
    if not disable_scheduled_task():
        sys.exit(1)
    
    # 2. 结束进程
    if not kill_yunshu_processes():
        sys.exit(1)
    
    # 3. 检查注销状态并修改 Logout 值
    check_logout_status()
    
    # 4. 修改配置文件
    if not update_config_file(server_url):
        sys.exit(1)
    
    # 5. 尝试删除 api_proxy.dat 文件
    if not os.path.exists(API_PROXY_PATH):
        print(f"文件不存在，跳过删除: {API_PROXY_PATH}")
    else:
        for attempt in range(3):
            try:
                os.remove(API_PROXY_PATH)
                print(f"已删除文件: {API_PROXY_PATH}")
                break  # 成功删除后退出循环
            except Exception as e:
                if attempt == 2:
                    messagebox.showerror("错误", f"删除文件失败: {e}")
                time.sleep(1)  # 等待 1 秒再重试
        else:
            # 如果三次都失败，退出程序
            messagebox.showerror("错误", "删除文件失败，程序将退出。")
            sys.exit(1)
    
    # 6. 重启应用程序
    if not restart_yunshu():
        sys.exit(1)
    
    messagebox.showinfo("成功", f"环境已成功切换到：{server_url}")
    sys.exit(0)

class SwitcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("云枢环境切换工具")
        self.root.geometry("370x180")
        self.root.resizable(False, False)
        
        # 设置窗口居中显示
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 370) // 2
        y = (screen_height - 180) // 2
        self.root.geometry(f"370x180+{x}+{y}")
        
        # 创建标签
        self.label = tk.Label(
            root, 
            text="请选择要切换的云枢运行环境：", 
            font=("微软雅黑", 12)
        )
        self.label.pack(pady=20)
        
        # 创建按钮框架
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        # 创建线上环境按钮
        self.btn_production = tk.Button(
            button_frame, 
            text="线上环境", 
            width=13, 
            height=2, 
            font=("微软雅黑", 10),
            command=self.switch_to_production
        )
        self.btn_production.grid(row=0, column=0, padx=10)
        
        # 创建预发环境按钮
        self.btn_prerelease = tk.Button(
            button_frame, 
            text="预发环境", 
            width=13, 
            height=2, 
            font=("微软雅黑", 10),
            command=self.switch_to_prerelease
        )
        self.btn_prerelease.grid(row=0, column=1, padx=10)
        
        # 创建其他环境按钮并调整到右下角
        self.btn_other = tk.Button(
            button_frame, 
            text="其他", 
            width=5, 
            # height=0.5,
            font=("微软雅黑", 9),
            fg="blue",
            bd=0,
            command=self.switch_to_other
        )
        self.btn_other.grid(row=1, column=1, padx=10, sticky='se')  # 移动到右下角
        
        # 检查配置文件是否存在
        if not os.path.exists(SETTINGS_FILE_PATH):
            messagebox.showerror("错误", f"无法找到配置文件：{SETTINGS_FILE_PATH}")
            sys.exit(1)
    
    def switch_to_production(self):
        """切换到线上环境"""
        switch_environment(PRODUCTION_URL)
    
    def switch_to_prerelease(self):
        """切换到预发环境"""
        switch_environment(PRE_URL)

    def switch_to_other(self):
        """切换到其他环境"""
        url = simpledialog.askstring("输入URL", "请输入完整的URL地址：")
        if url:
            switch_environment(url)

if __name__ == "__main__":
    # 检查是否以管理员身份运行
    if not is_admin():
        run_as_admin()
        sys.exit(0)
    
    # 创建并运行GUI
    root = tk.Tk()
    app = SwitcherApp(root)
    root.mainloop() 
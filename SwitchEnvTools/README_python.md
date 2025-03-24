# 云枢环境切换工具 (Python版)

这是一个用Python开发的工具，用于在云枢产品的预发环境和线上环境之间切换。

## 功能特点

1. 双击默认使用管理员权限打开
2. 提供简单的用户界面，一键切换环境
3. 自动修改配置文件，切换服务器地址
4. 自动禁用相关Windows任务计划
5. 自动结束相关进程
6. 自动重启云枢应用

## 安装依赖

在使用之前，需要安装以下Python库：

```bash
pip install psutil
```

tkinter通常已包含在Python标准库中，无需额外安装。

## 使用方法

1. 双击运行`YunShuSwitcher.py`或通过命令行运行：
   ```bash
   python YunShuSwitcher.py
   ```

2. 程序会自动请求管理员权限
3. 在弹出的界面中选择目标环境（线上环境或预发环境）
4. 工具将自动完成以下操作：
   - 修改`C:\Program Files\YunShu\SetupSettings.json`配置文件中的服务器地址
   - 禁用名为"YunShu Service Task Scheduler"的Windows计划任务
   - 结束所有以"YunShu"开头的进程
   - 重启云枢应用程序

## 环境配置

- 线上环境服务器地址：https://sp.eagleyun.cn
- 预发环境服务器地址：https://sp.pre.eagleyun.cn

## 系统要求

- Windows 7 及以上操作系统
- Python 3.6 或更高版本
- 管理员权限

## 注意事项

- 如果遇到无法保存配置文件的情况，请检查您的安全软件是否开启了自保护功能
- 该工具需要管理员权限才能正常运行
- 切换环境后，云枢应用会自动重启

## 打包为可执行文件

如果想将脚本打包为独立的.exe文件，可以使用PyInstaller：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --uac-admin --icon=icon.ico YunShuSwitcher.py
```

打包后的可执行文件将生成在dist目录中。 
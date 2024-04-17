import ctypes


def is_admin():
    # 调用IsUserAnAdmin函数检查当前用户是否为管理员
    return ctypes.windll.shell32.IsUserAnAdmin() != 0


if __name__ == "__main__":
    if is_admin():
        print("当前用户拥有管理员权限！")
    else:
        print("当前用户没有管理员权限。")
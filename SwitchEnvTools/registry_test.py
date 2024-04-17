import winreg


def get_registry_value(value_name):
    # 定义注册表键路径
    key_path = r'SOFTWARE\WOW6432Node\YunShu'

    # 打开注册表键，使用winreg.HKEY_LOCAL_MACHINE作为根键
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)

        # 读取指定值
        value, value_type = winreg.QueryValueEx(key, value_name)

        # 关闭注册表键
        winreg.CloseKey(key)

        # 返回读取到的值和值类型
        return value, value_type
    except FileNotFoundError:
        print(f"注册表键 {key_path} 或值 {value_name} 不存在。")
        return None, None
    except PermissionError:
        print(f"没有足够的权限访问注册表键 {key_path}。")
        return None, None
    except Exception as e:
        print(f"读取注册表时发生错误: {e}")
        return None, None

    # 使用示例


value_name = 'Logout'  # 替换为你要读取的值名称
value, value_type = get_registry_value(value_name)
if value is not None:
    print(f"值: {value}, 类型: {value_type}")
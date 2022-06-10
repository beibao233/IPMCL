from System import base_path

from yaml import load, dump, FullLoader, SafeDumper
from loguru import logger
import platform
import atexit
import os

# 提前准备好变量免得Pycharm对动态变量报错
global languages
global l_current

global sources
global setting
global accounts

# 准备好文件名退出程序时保存
file_names = list()


class NoAliasDumper(SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(NoAliasDumper, self).increase_indent(flow, False)

    def ignore_aliases(self, data):
        return True


for file in os.listdir(os.path.join(base_path, "IPMCL")):
    if file in ["__init__.py", "__pycache__"]:
        continue
    else:
        try:
            with open(os.path.join(base_path, "IPMCL", file), encoding="UTF-8") as f:
                data = load(f, Loader=FullLoader)

            file_names.append(file)

            exec(f"{os.path.splitext(file)[0]} = {data}")
        except (PermissionError, IsADirectoryError):
            exec(f"{os.path.splitext(file)[0]} = {dict()}")

            try:
                for deeper_file in os.listdir(os.path.join(base_path, "IPMCL", os.path.splitext(file)[0])):
                    with open(os.path.join(base_path, "IPMCL", os.path.splitext(file)[0], deeper_file),
                              encoding="UTF-8") as f:
                        exec(f"{os.path.splitext(file)[0]}['{os.path.splitext(deeper_file)[0]}'] "
                             f"= "
                             f"{load(f, Loader=FullLoader)}")
            except PermissionError:
                logger.warning('Supports up to two levels of file directories! The program exits!')
                exit()

        except FileNotFoundError:
            pass


# 设置当前语言
def language(language_name: str):
    global l_current
    global setting

    setting['Launcher']['Language'] = language_name
    l_current = languages[setting['Launcher']['Language']]


language(setting['Launcher']['Language'])

operating_system = setting['Platforms'][platform.system()]


@atexit.register
def config_save():
    for file_name in file_names:
        with open(os.path.join(base_path, "IPMCL", file_name), 'w', encoding="utf-8") as f:
            dump(eval(os.path.splitext(file_name)[0]), f, allow_unicode=True, Dumper=NoAliasDumper)

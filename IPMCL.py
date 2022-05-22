from yaml import load, dump, FullLoader, SafeDumper
from main import base_path
from loguru import logger
import atexit
import os

# 提前准备好变量免得Pycharm对动态变量报错
global languages
global l_current

global sources
global setting

# 准备好文件名退出程序时保存
file_names = list()


class NoAliasDumper(SafeDumper):
    def ignore_aliases(self, data):
        return True


for file in os.listdir(os.path.join(base_path, "IPMCL")):
    if file in ["__init__.py", "__pycache__"]:
        continue
    else:
        try:
            with open(os.path.join(base_path, "IPMCL", file)) as f:
                data = load(f, Loader=FullLoader)

            file_names.append(file)

            exec(f"{os.path.splitext(file)[0]} = {data}")
        except PermissionError:
            exec(f"{os.path.splitext(file)[0]} = {dict()}")

            try:
                for deeper_file in os.listdir(os.path.join(base_path, "IPMCL", os.path.splitext(file)[0])):
                    with open(os.path.join(base_path, "IPMCL", os.path.splitext(file)[0], deeper_file)) as f:
                        exec(f"{os.path.splitext(file)[0]}['{os.path.splitext(deeper_file)[0]}'] "
                             f"= "
                             f"{load(f, Loader=FullLoader)}")
            except PermissionError:
                logger.warning('Supports up to two levels of file directories! The program exits!')
                exit()


# 设置当前语言
def language(language_name: str):
    global l_current
    global setting

    setting['Launcher']['Language'] = language_name
    l_current = languages[setting['Launcher']['Language']]


language(setting['Launcher']['Language'])


@atexit.register
def config_save():
    for file_name in file_names:
        with open(os.path.join(base_path, "IPMCL", file_name), 'w', encoding="utf-8") as f:
            dump(eval(os.path.splitext(file_name)[0]), f, allow_unicode=True, Dumper=NoAliasDumper)

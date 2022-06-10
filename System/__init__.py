import asyncio
import os

import sys
import platform
import hashlib

if platform.system() == 'Windows':
    import ctypes.wintypes

    def getDocPath(path_id: int):
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, path_id, None, 0, buf)
        return buf.value


def system_uuid():
    sysinfo = str()

    sysinfo += str(platform.architecture())

    sysinfo += str(platform.machine())

    sysinfo += str(platform.platform())

    sysinfo += str(platform.processor())

    sysinfo += str(platform.system())

    syslen = str(len(sysinfo))

    syshash = hashlib.md5(sysinfo.encode("utf-8")).hexdigest()

    syslen_hash = hashlib.sha512(syslen.encode("utf-8")).hexdigest()

    return hashlib.sha256(syshash.encode("utf-8") + syslen_hash.encode("utf-8")).hexdigest().upper()


if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    download_loop = asyncio.new_event_loop()
else:
    download_loop = asyncio.get_event_loop()


base_path = os.path.dirname(os.path.realpath(sys.executable))


if not os.path.exists(os.path.join(base_path, "IPMCL")):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))


if not os.path.exists(os.path.join(base_path, "IPMCL")):
    # 需要提示

    exit()

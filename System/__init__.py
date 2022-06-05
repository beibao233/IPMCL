from IPMCL import setting
import platform
import hashlib

operating_system = setting['Platforms'][platform.system()]

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

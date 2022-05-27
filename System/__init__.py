from IPMCL import setting
import platform

operating_system = setting['Platforms'][platform.system()]

if platform.system() == 'Windows':
    import ctypes.wintypes

    def getDocPath(path_id: int):
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, path_id, None, 0, buf)
        return buf.value

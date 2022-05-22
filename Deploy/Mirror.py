from IPMCL import setting


def set_mirror(official_mode: bool = True, mirror_name: str = ""):
    if not official_mode:
        setting["Mirror"]["Official"] = False
        setting["Mirror"]["Mame"] = mirror_name
    else:
        setting["Mirror"]["Official"] = True

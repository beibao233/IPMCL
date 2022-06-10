from IPMCL import setting

from json import dump
from pathlib import Path
import shutil
import uuid
import time
import os

if "Paths" not in setting:
    setting["Paths"] = list()


def add(home_path: str):
    setting["Paths"].append(home_path)
    setting["Launch"]["CurrentPath"] = home_path

    return True


def create(home_path: str):
    if not os.path.exists(home_path):
        os.makedirs(home_path)
    else:
        if os.path.isdir(home_path):
            shutil.rmtree(home_path)
            os.makedirs(home_path)
        else:
            return False

    for path in ["assets", "libraries", "versions"]:
        if not Path(os.path.join(home_path, path)).exists():
            os.makedirs(os.path.join(home_path, path))

    for path in ["indexes", "objects"]:
        if not Path(os.path.join(home_path, 'assets', path)).exists():
            os.makedirs(os.path.join(home_path, 'assets', path))

    launcher_profiles = \
        {
            "profiles": {
                setting['Launcher']['Name']: {
                    "icon": "Grass",
                    "name": setting['Launcher']['Name'],
                    "lastVersionId": setting['Launcher']['Version'],
                    "type": setting['Launcher']['Version'],
                    "lastUsed": time.strftime("%Y-%m-%dT%H:%M:%S.0000Z", time.localtime())
                }
            },
            "selectedProfile": setting['Launcher']['Name'],
            "clientToken": str(uuid.uuid4()).replace("-", "")
        }

    with open(os.path.join(home_path, "launcher_profiles.json"), "w+") as f:
        dump(launcher_profiles, f, indent=4)

    setting["Paths"].append(home_path)
    setting["Launch"]["CurrentPath"] = home_path

    return True

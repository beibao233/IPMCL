from IPMCL import setting
from json import dump
from pathlib import Path
from os.path import join
from os import makedirs
import uuid
import time


def create(home_path: str):
    for path in ["assets", "libraries", "versions"]:
        if not Path(join(home_path, path)).exists():
            makedirs(join(home_path, path))

    for path in ["indexes", "objects"]:
        if not Path(join(home_path, 'assets', path)).exists():
            makedirs(join(home_path, 'assets', path))

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

    with open(join(home_path, "launcher_profiles.json"), "w+") as f:
        dump(launcher_profiles, f, indent=4)

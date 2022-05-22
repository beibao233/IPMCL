from Request import uload
from IPMCL import sources, setting, l_current
from main import download_loop

from loguru import logger


class Versions:
    def __init__(self,
                 versions: dict,
                 detects: list = None
                 ):
        self.unknowns = list()
        self.versions = versions

        if "latest" in self.versions:
            for push_type in self.versions['latest']:
                exec(f"self.latest_{push_type} = '{self.versions['latest'][push_type]}'")

        if detects is None:
            self.detects = ["snapshot", "release"]
        else:
            self.detects = detects

        for detect_sign in self.detects:
            exec(f"self.{detect_sign} = {dict()}")

        for version in self.versions['versions']:
            try:
                if version["type"] in self.detects:
                    version_data = [
                        version['url'],
                        version['releaseTime'],
                        version['sha1'],
                        version['complianceLevel']
                    ]

                    exec(f"self.{version['type']}['{version['id']}'] = {version_data}")
                else:
                    self.unknowns.append(version['id'])
            except KeyError:
                self.unknowns.append(version['id'])


class Manifest(Versions):
    def __init__(self):
        self.latest_release = str()
        self.latest_snapshot = str()
        self.release = dict()
        self.snapshot = dict()
        self.all = dict()

        if setting['Mirror']['Official']:
            data = download_loop.run_until_complete(
                uload(
                    sources["Minecraft"]["Versions"]["Official"] + sources["Minecraft"]["Versions"]["Path"]
                )
            )
        else:
            data = download_loop.run_until_complete(
                uload(
                    sources["Minecraft"]["Versions"]["Mirrors"][
                        setting['Mirror']['Name']
                    ] + sources["Minecraft"]["Versions"]["Path"]
                )
            )

        super().__init__(data)

        self.all = dict(self.release, **self.snapshot)

        logger.info(l_current['Minecraft']['Version']['Success'])

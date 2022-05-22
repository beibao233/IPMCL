from Manifest import Manifest
from Deploy.Path import create
from File_Download import download
from Request import uload
from main import download_loop
from IPMCL import setting, sources, l_current

from pathlib import Path
from loguru import logger
import os


def installer(home_path: str, version: str):
    logger.info(l_current['Minecraft']['Install']['Start'].format(version=version))

    create(home_path=home_path)

    if not Path(os.path.join(home_path, 'versions', version)).exists():
        os.makedirs(os.path.join(home_path, 'versions', version))

    source_url = Manifest().all[version][0]

    if not setting['Mirror']['Official']:
        source_url = source_url.replace(
            sources['Minecraft']['Versions']['Official'],
            sources['Minecraft']['Versions']['Mirrors'][
                setting['Mirror']['Name']
            ]
        )

    source_dict = download_loop.run_until_complete(uload(source_url))

    try:
        download(home_path, source_dict)

        logger.info(l_current['Minecraft']['Install']['Finished'].format(version=version))
    except PermissionError:
        logger.warning(l_current['Minecraft']['Install']['Errors']['PermissionError'])


installer("C:\\Users\\27845\\Desktop\\Games", "1.12.2")

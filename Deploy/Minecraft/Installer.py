from .Manifest import Manifest
from .File_Download import download
from Deploy.Path import create
from Request import uload
from main import download_loop
from IPMCL import setting, sources, l_current

from pathlib import Path
from loguru import logger
import os


def installer(home_path: str, version: str, version_name: str = None):
    logger.info(l_current['Minecraft']['Install']['Start'].format(version=version))

    if version_name is None:
        version_name = version

    create(home_path=home_path)

    if not Path(os.path.join(home_path, 'versions', version)).exists():
        os.makedirs(os.path.join(home_path, 'versions', version))

    sources_all = Manifest().all

    source_url = sources_all[version][0]
    source_hash = sources_all[version][2]

    if not setting['Mirror']['Official']:
        source_url = source_url.replace(
            sources['Minecraft']['Versions']['Official'],
            sources['Minecraft']['Versions']['Mirrors'][
                setting['Mirror']['Name']
            ]
        )

    source_dict = download_loop.run_until_complete(uload(source_url, file_hash=source_hash))

    try:
        download(home_path, source_dict, version_name)

        logger.info(l_current['Minecraft']['Install']['Finished'].format(version=version))
    except PermissionError:
        logger.warning(l_current['Minecraft']['Install']['Errors']['PermissionError'])

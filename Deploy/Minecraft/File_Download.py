from Request import fdownload, uload
from IPMCL import setting, sources, l_current
from main import download_loop
from System import operating_system

from pathlib import Path
from loguru import logger
from json import dump
import asyncio
import os


async def download_assets(asset_hash_f2, asset_hash, assets_path, asset, semaphore=None):
    if operating_system == "natives-windows" and setting['Download']['Concurrency'] > 500:
        setting['Download']['Concurrency'] = 500
        semaphore = await asyncio.Semaphore(setting['Download']['Concurrency'])

    async with semaphore:
        if not setting['Mirror']['Official']:
            asset_file = await fdownload(
                f"{sources['Minecraft']['Assets']['Mirrors'][setting['Mirror']['Name']]}"
                f"/{asset_hash_f2}"
                f"/{asset_hash}",
                file_hash=asset_hash
            )
        else:
            asset_file = await fdownload(
                f"{sources['Minecraft']['Assets']['Official']}"
                f"/{asset_hash_f2}"
                f"/{asset_hash}",
                file_hash=asset_hash
            )

        if asset_file is False:
            logger.warning(l_current["Minecraft"]["Download"]["Fail"]["Asset"].format(name=asset))

        else:
            if not Path(os.path.join(assets_path, 'objects', asset_hash_f2)).exists():
                os.makedirs(os.path.join(assets_path, 'objects', asset_hash_f2))

            with open(os.path.join(assets_path, 'objects', asset_hash_f2, asset_hash), "wb+") as f:
                f.write(asset_file)

            logger.info(l_current["Minecraft"]["Download"]["Success"]["Asset"].format(name=asset))


async def download_libraries(library_url: str,
                             libraries_path: str,
                             library_path: str,
                             library_name: str,
                             library_hash: str = None
                             ):
    if not setting['Mirror']['Official']:
        library_url = library_url.replace(
            sources['Minecraft']['Libraries']['Official'],
            sources['Minecraft']['Libraries']['Mirrors'][
                setting['Mirror']['Name']
            ]
        )

    library_jar = await fdownload(library_url)

    # 需要校验

    if not Path(library_path).exists():
        os.makedirs(library_path)

    with open(os.path.join(libraries_path, library_path, library_name), "wb+") as f:
        f.write(library_jar)

    logger.info(l_current['Minecraft']['Download']['Success']['Library'].format(name=library_name))


def download(base_path: str, source_dict: dict, version_name: str, side: str = "client"):
    # 准备所需路径
    version_path = os.path.join(base_path, "versions", version_name)
    libraries_path = os.path.join(base_path, "libraries")
    assets_path = os.path.join(base_path, "assets")

    # 保存游戏文件源
    with open(os.path.join(version_path, f"{version_name}.json"), "w+") as f:
        dump(source_dict, f, indent=4, sort_keys=True)

    # 下载游戏本体

    if not setting['Mirror']['Official']:
        game_jar_url = source_dict['downloads'][side]['url'].replace(
            sources['Minecraft']['Self']['Official'],
            sources['Minecraft']['Self']['Mirrors'][
                setting['Mirror']['Name']
            ]
        )
    else:
        game_jar_url = source_dict['downloads'][side]['url']

    game_jar = download_loop.run_until_complete(
        fdownload(game_jar_url)
    )

    with open(os.path.join(version_path, f"{version_name}.jar"), "wb+") as f:
        f.write(game_jar)

    logger.info(l_current['Minecraft']['Download']['Success']['Self'].format(name= version_name))

    # 下载资源
    if not setting['Mirror']['Official']:
        assets_index_url = source_dict['assetIndex']['url'].replace(
            sources['Minecraft']['Versions']['Official'],
            sources['Minecraft']['Versions']['Mirrors'][
                setting['Mirror']['Name']
            ]
        )
    else:
        assets_index_url = source_dict['assetIndex']['url']

    assets_index = download_loop.run_until_complete(
        uload(assets_index_url)
    )

    with open(os.path.join(assets_path, 'indexes', f"{source_dict['assetIndex']['id']}.json"), "w+") as f:
        dump(assets_index, f, indent=4)

    assets_download_tasks = []
    assets_semaphore = asyncio.Semaphore(setting['Download']['Concurrency'])

    for asset in assets_index['objects']:
        asset_hash = assets_index['objects'][asset]["hash"]
        asset_hash_f2 = assets_index['objects'][asset]["hash"][:2]

        assets_download_tasks.append(
            download_assets(
                asset_hash_f2=asset_hash_f2,
                asset_hash=asset_hash,
                assets_path=assets_path,
                asset=asset,
                semaphore=assets_semaphore
            )
        )

    download_loop.run_until_complete(asyncio.wait(assets_download_tasks))

    # 下载支持库

    libraries_download_tasks = []

    for library in source_dict['libraries']:
        try:
            library_url = library['downloads']['artifact']['url']
            library_hash = library['downloads']['artifact']['sha1']
            library_name = os.path.split(library['downloads']['artifact']['path'])[1]

            library_path = os.path.join(libraries_path,
                                        os.path.split(library['downloads']['artifact']['path'])[0])

            libraries_download_tasks.append(
                download_libraries(
                    libraries_path=libraries_path,
                    library_path=library_path,
                    library_name=library_name,
                    library_url=library_url,
                    library_hash=library_hash
                )
            )

        except KeyError:
            pass

        try:
            library_url = library['downloads']['classifiers'][operating_system]['url']
            library_hash = library['downloads']['classifiers'][operating_system]['sha1']
            library_name = os.path.split(library['downloads']['classifiers'][operating_system]['path'])[1]

            library_path = os.path.join(
                libraries_path,
                os.path.split(library['downloads']['classifiers'][operating_system]['path'])[0]
            )

            libraries_download_tasks.append(
                download_libraries(
                    libraries_path=libraries_path,
                    library_path=library_path,
                    library_name=library_name,
                    library_url=library_url,
                    library_hash=library_hash
                )
            )

        except KeyError:
            pass

    download_loop.run_until_complete(asyncio.wait(libraries_download_tasks))

from Request import fdownload, uload
from Deploy.System import operating_system
from IPMCL import setting, sources, l_current
from main import download_loop

from pathlib import Path
from loguru import logger
from json import dump
import os


def download(base_path: str, source_dict: dict, side: str = "client"):
    # 准备所需路径
    version_path = os.path.join(base_path, "versions", source_dict['id'])
    libraries_path = os.path.join(base_path, "libraries")
    assets_path = os.path.join(base_path, "assets")

    # 保存游戏文件源
    with open(os.path.join(version_path, f"{source_dict['id']}.json"), "w+") as f:
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

    with open(os.path.join(version_path, f"{source_dict['id']}.jar"), "wb+") as f:
        f.write(game_jar)

    logger.info(l_current['Minecraft']['Download']['Success']['Self'].format(name=source_dict['id']))

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

    for asset in assets_index['objects']:
        asset_hash = assets_index['objects'][asset]["hash"]
        asset_hash_f2 = assets_index['objects'][asset]["hash"][:2]

        if not setting['Mirror']['Official']:
            asset_file = download_loop.run_until_complete(
                fdownload(f"{sources['Minecraft']['Assets']['Mirrors'][setting['Mirror']['Name']]}"
                          f"/{asset_hash_f2}"
                          f"/{asset_hash}")
                )
        else:
            asset_file = download_loop.run_until_complete(
                fdownload(f"{sources['Minecraft']['Assets']['Official']}"
                          f"/{asset_hash_f2}"
                          f"/{asset_hash}")
                )

        if not Path(os.path.join(assets_path, 'objects', asset_hash_f2)).exists():
            os.makedirs(os.path.join(assets_path, 'objects', asset_hash_f2))

        with open(os.path.join(assets_path, 'objects', asset_hash_f2, asset_hash), "wb+") as f:
            f.write(asset_file)

        logger.info(l_current["Minecraft"]["Download"]["Success"]["Asset"].format(name=asset))

    # 下载支持库

    for library in source_dict['libraries']:
        try:
            library_url = library['downloads']['artifact']['url']
            library_name = os.path.split(library['downloads']['artifact']['path'])[1]

            library_path = os.path.join(libraries_path,
                                        os.path.split(library['downloads']['artifact']['path'])[0])
        except KeyError:
            library_url = library['downloads']['classifiers'][operating_system]['url']
            library_name = os.path.split(library['downloads']['classifiers'][operating_system]['path'])[1]

            library_path = os.path.join(
                libraries_path,
                os.path.split(library['downloads']['classifiers'][operating_system]['path'])[0]
            )

        if not setting['Mirror']['Official']:
            library_url = library_url.replace(
                sources['Minecraft']['Libraries']['Official'],
                sources['Minecraft']['Libraries']['Mirrors'][
                    setting['Mirror']['Name']
                ]
            )

        library_jar = download_loop.run_until_complete(fdownload(library_url))

        # 需要校验

        if not Path(library_path).exists():
            os.makedirs(library_path)

        with open(os.path.join(libraries_path, library_path, library_name), "wb+") as f:
            f.write(library_jar)

        logger.info(l_current['Minecraft']['Download']['Success']['Library'].format(name=library_name))

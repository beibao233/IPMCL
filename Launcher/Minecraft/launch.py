from IPMCL import setting, l_current
from Launcher.Java import finder
from .libraries import library_paths, unzip_natives

from loguru import logger
from shutil import copyfile, rmtree
import platform
import subprocess
import json
import os
import re


def realname(argument_name: str, ):
    return argument_name.replace("${", '').replace('}', '')


def legacy(assets_root, version_assets_index):

    legacy_path = os.path.join(assets_root, "legacy")

    if os.path.exists(legacy_path):
        rmtree(legacy_path)
        os.makedirs(legacy_path)
    else:
        os.makedirs(legacy_path)

    for asset_object in version_assets_index["objects"]:

        asset_hash = version_assets_index["objects"][asset_object]["hash"]
        asset_hash_f2 = version_assets_index["objects"][asset_object]["hash"][:2]

        new_path = os.path.join(legacy_path, asset_object)

        try:
            os.makedirs(os.path.dirname(new_path))
        except FileExistsError:
            pass

        copyfile(os.path.join(assets_root, 'objects', asset_hash_f2, asset_hash),
                 new_path)

    return legacy_path


def jvm_argument(version_json, natives_directory, classpath):
    platform_name = None

    flag_replace_index = {'-Dos.name=Windows 10': '-Dos.name="Windows 10"'}

    if platform.system() == "Windows":
        platform_name = 'windows'
    elif platform.system() == "Darwin":
        platform_name = 'osx'

    launcher_name = setting['Launcher']['Name']
    launcher_version = setting['Launcher']['Version']

    jvm_command = str()

    for argument in version_json["arguments"]['jvm']:
        if isinstance(argument, str):
            try:
                argument_name = re.search(r"\$\{[\w]*}", argument).group()
                argument_realname = realname(argument_name)

                jvm_command += f"""{eval(f"argument.replace('{argument_name}', {argument_realname})")} """

            except AttributeError:
                jvm_command += f"{argument} "
            
        else:
            try:
                # 确定是否可以使用此规则并确保操作平台正确
                if argument['rules'][0]['action'] == 'allow' and argument['rules'][0]['os']['name'] == platform_name:
                    # 如果规则没有操作平台版本限制
                    if 'version' not in argument['rules'][0]:
                        # 如果flag值是一个列表则按表添加
                        if isinstance(argument['value'], list):
                            for value in argument['value']:
                                # 如果值在值替换表里则替换
                                if value in flag_replace_index:
                                    value = flag_replace_index[value]

                                jvm_command += f"{value} "
                        # 字符串直接添加
                        else:
                            if argument['value'] in flag_replace_index:
                                argument['value'] = flag_replace_index[argument['value']]

                            jvm_command += f"{argument['value']} "
                    # 如果规则有操作平台版本限制且系统版本为10
                    elif platform.version().startswith('10'):
                        if argument['value'] in flag_replace_index:
                            argument['value'] = flag_replace_index[argument['value']]

                        jvm_command += f"{argument['value']} "
            except KeyError:
                continue

    return jvm_command


def minecraft_argument(version_json,
                       auth_player_name,
                       version_name,
                       game_directory,
                       assets_root,
                       assets_index_name,
                       auth_uuid,
                       auth_access_token,
                       clientid,
                       auth_xuid,
                       user_type,
                       version_type,
                       is_demo_user,
                       has_custom_resolution,
                       resolution_width,
                       resolution_height,
                       auth_session,
                       version_index=None,
                       high_mode=True):

    with open(os.path.join(assets_root, "indexes", version_index["assetIndex"]["id"])+".json") as f:
        version_assets_index = json.load(f)

    if "map_to_resources" in version_assets_index or "assets" in version_index and version_index["assets"] == "legacy":
        game_assets = legacy(assets_root=assets_root, version_assets_index=version_assets_index)

    command = str()

    if high_mode is True:
        arguments = version_json["arguments"]['game']
    else:
        arguments = version_json

    for argument in arguments:
        if isinstance(argument, str):
            try:
                argument_name = re.search(r"\$\{[\w]*}", argument).group()
                argument_realname = realname(argument_name)

                command += f"""{eval(f"argument.replace('{argument_name}', {argument_realname})")} """

            except AttributeError:
                command += f"{argument} "
        else:
            features = False

            for rule in argument['rules']:
                if rule['action'] != 'allow':
                    continue
                else:
                    features = eval(
                        f"{list(rule['features'].keys())[0]} is {rule['features'][list(rule['features'].keys())[0]]}")

            if features:
                if isinstance(argument['value'], list):
                    for flag in argument['value']:
                        try:
                            argument_name = re.search(r"\$\{[\w]*}", flag).group()
                            argument_realname = realname(argument_name)

                            command += f"""{eval(f"flag.replace('{argument_name}', str({argument_realname}))")} """
                        except AttributeError:
                            command += f"{flag} "
                else:
                    try:
                        argument_name = re.search(r"\$\{[\w]*}", argument['value']).group()
                        argument_realname = realname(argument_name)

                        command += f"""{eval(f"flag.replace('{argument_name}', str({argument_realname}))")} """
                    except AttributeError:
                        command += f"{argument['value']} "

    return command


def launch(
        game_directory,
        version_name,
        auth_player_name,
        auth_uuid,
        auth_access_token,
        auth_session=None,
        xmn: int = 256,
        xmx: int = 2048,
        is_demo_user: bool = False,
        has_custom_resolution=False,
        resolution_width: int = None,
        resolution_height: int = None
):
    version_path = os.path.join(game_directory, 'versions', version_name)

    with open(os.path.join(version_path, version_name + ".json")) as f:
        version_json = json.load(f)

    javas = finder()

    command = str()

    for java in javas:
        try:
            if javas[java][0].replace("1.", '').startswith(str(version_json["javaVersion"]["majorVersion"])):
                logger.info(l_current["Minecraft"]["Launcher"]["JavaSelect"].format(version=javas[java][0]))
                command += f'"{javas[java][1]}" '
                break

        except KeyError:
            if javas[java][0].replace("1.", '').startswith(str(8)):
                logger.info(l_current["Minecraft"]["Launcher"]["JavaSelect"].format(version=javas[java][0]))
                command += f'"{javas[java][1]}" '
                break

    cp = f'"{library_paths(base_path=game_directory, libraries=version_json["libraries"], version_name=version_name)}"'
    nd = f'"{unzip_natives(base_path=game_directory, libraries=version_json["libraries"], version_name=version_name)}"'

    assets_root = os.path.join(game_directory, 'assets')
    clientid = "${clientid}"
    auth_xuid = "${auth_xuid}"
    user_type = "Mojang"
    version_type = setting["Launcher"]["Name"]
    assets_index_name = version_json["assetIndex"]["id"]

    try:
        command += jvm_argument(version_json=version_json,
                                natives_directory=nd,
                                classpath=cp)

        command += f"-Xmn{str(xmn)}m -Xmx{str(xmx)}m {version_json['mainClass']} "

        command += minecraft_argument(version_json=version_json,
                                      auth_player_name=auth_player_name,
                                      version_name=version_name,
                                      game_directory=game_directory,
                                      assets_root=assets_root,
                                      assets_index_name=assets_index_name,
                                      auth_uuid=auth_uuid,
                                      auth_access_token=auth_access_token,
                                      clientid=clientid,
                                      auth_xuid=auth_xuid,
                                      user_type=user_type,
                                      version_type=version_type,
                                      is_demo_user=is_demo_user,
                                      has_custom_resolution=has_custom_resolution,
                                      resolution_width=resolution_width,
                                      auth_session=auth_session,
                                      resolution_height=resolution_height
                                      )
    except KeyError:
        if platform.version().startswith('10'):
            command += '-Dos.name="Windows 10" -Dos.version=10.0 '

        command += f"-Dminecraft.launcher.brand={setting['Launcher']['Name']} " \
                   f"-Dminecraft.launcher.version={setting['Launcher']['Version']} "

        command += f"-Djava.library.path={nd} "

        command += f"-cp {cp} "

        command += f"-Xmn{str(xmn)}m -Xmx{str(xmx)}m {version_json['mainClass']} "

        command += minecraft_argument(version_json=version_json["minecraftArguments"].split(),
                                      auth_player_name=auth_player_name,
                                      version_name=version_name,
                                      game_directory=game_directory,
                                      assets_root=assets_root,
                                      assets_index_name=assets_index_name,
                                      auth_uuid=auth_uuid,
                                      auth_access_token=auth_access_token,
                                      clientid=clientid,
                                      auth_xuid=auth_xuid,
                                      user_type=user_type,
                                      version_type=version_type,
                                      is_demo_user=is_demo_user,
                                      has_custom_resolution=has_custom_resolution,
                                      resolution_width=resolution_width,
                                      resolution_height=resolution_height,
                                      auth_session=auth_session,
                                      version_index=version_json,
                                      high_mode=False
                                      )

    subprocess.Popen(command, shell=True)

    return True

from .LocalServer import start_server_thread, stop_thread, code_buffer_read
from IPMCL import setting, l_current, accounts

from loguru import logger

import json
import socket
import random
import asyncio
import aiohttp
import webbrowser


def isOpen(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("localhost", int(port)))
        s.shutdown(2)
        return True
    except:
        return False


def get_port():
    for time in range(10):
        port = random.randint(1024, 25565)

        if isOpen(port) is False:
            return port

    return setting['Launch']['MS_OAuth']['DefaultPort']


async def oauth_flow(login_port):
    login_url = f"{setting['Launch']['MS_OAuth']['URL']['Authorize']}" \
                f"?client_id={setting['Launch']['MS_OAuth']['ClientId']}" \
                f"&response_type=code" \
                f"&redirect_uri=http://localhost:{str(login_port)}" \
                f"&scope=XboxLive.signin%20offline_access"

    id = start_server_thread(login_port)

    webbrowser.open(login_url)

    for check in range(setting['Launch']['MS_OAuth']['CheckTimes']):
        if code_buffer_read() != str():
            break
        else:
            await asyncio.sleep(setting['Launch']['MS_OAuth']['CheckInterval'])

    stop_thread(id)

    logger.info(l_current["Minecraft"]["Auth"]["LocalServerStopped"])

    if code_buffer_read() != str():
        return code_buffer_read()


async def code2token(code=None,
                     redirect_url=None,
                     auth_port=None,
                     login_mode: bool = False):
    client_id = setting['Launch']['MS_OAuth']['ClientId']
    client_secret = setting['Launch']['MS_OAuth']['ClientSecret']

    if login_mode:
        data_json = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": code,
            "grant_type": "refresh_token",
            "redirect_uri": redirect_url
        }

    else:
        data_json = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code_buffer_read(),
            "grant_type": "authorization_code",
            "redirect_uri": f"http://localhost:{str(auth_port)}"
        }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    async with aiohttp.ClientSession() as session:
        async with session.post(setting['Launch']['MS_OAuth']['URL']['Access'],
                                data=data_json,
                                headers=headers) as resp:
            result = await resp.json()

    logger.info(l_current["Minecraft"]["Auth"]["AuthorizationToken"])

    return result


async def auth5xbl(access_token):
    rps_ticket = "d=" + access_token

    data_json = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": rps_ticket
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT"
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(setting['Launch']['MS_OAuth']['URL']['XBL'],
                                json=data_json,
                                headers=headers) as resp:
            result = await resp.json()

    logger.info(l_current["Minecraft"]["Auth"]["Authenticate"]["XBL"])

    return result


async def auth5xsts(xbl_token):
    data_json = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [
                xbl_token
            ]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT"
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(setting['Launch']['MS_OAuth']['URL']['XSTS'],
                                json=data_json,
                                headers=headers) as resp:
            result = await resp.json()

    logger.info(l_current["Minecraft"]["Auth"]["Authenticate"]["XSTS"])

    return result


async def auth5minecraft(userhash, xsts_token):
    identity_token = f"XBL3.0 x={userhash};{xsts_token}"

    data_json = {
        "identityToken": identity_token
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(setting['Launch']['MS_OAuth']['URL']['Minecraft'],
                                json=data_json) as resp:
            result = await resp.json()

    logger.info(l_current["Minecraft"]["Auth"]["Authenticate"]["Minecraft"])

    return result


async def is_game_owner(minecraft_access_token):
    authorization = "Bearer " + minecraft_access_token

    headers = {
        'Authorization': authorization
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(setting['Launch']['MS_OAuth']['URL']['Ownership'],
                               headers=headers) as resp:
            result = await resp.json()

    logger.info(l_current["Minecraft"]["Auth"]["GameOwnership"])

    return result


async def get_profile(minecraft_access_token):
    authorization = "Bearer " + minecraft_access_token

    headers = {
        'Authorization': authorization
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(setting['Launch']['MS_OAuth']['URL']['Profile'],
                               headers=headers) as resp:
            result = await resp.json()

    logger.info(l_current["Minecraft"]["Auth"]["Profile"])

    return result


async def start_auth():
    login_port = get_port()

    if await oauth_flow(login_port) is not None:
        access_token_index = await code2token(auth_port=login_port)

        xbl_token_index = await auth5xbl(access_token_index["access_token"])

        xsts_token_index = await auth5xsts(xbl_token_index["Token"])

        if "XErr" in xsts_token_index:
            logger.warning(l_current["Minecraft"]["Auth"]["Errors"]["XSTS"][xsts_token_index["XErr"]])

            return False

        minecraft_access_token_index = await auth5minecraft(xsts_token_index["DisplayClaims"]["xui"][0]["uhs"],
                                                            xsts_token_index["Token"])

        ownership_index = await is_game_owner(minecraft_access_token_index["access_token"])

        minecraft_java_ed = int()

        # 应该搬到上面的is_owner中 暂时不动
        for item in ownership_index["items"]:
            if item["name"] in ["product_minecraft", "game_minecraft"]:
                minecraft_java_ed += 1

        if not minecraft_java_ed == 2:
            logger.warning(l_current["Minecraft"]["Auth"]["Errors"]["IsntOwn"])

            return False

        profile = await get_profile(minecraft_access_token_index["access_token"])

        accounts[minecraft_access_token_index["username"]] = {
            "refresh_token": access_token_index["refresh_token"],
            "redirect_url": f"http://localhost:{str(login_port)}",
            "uuid": profile["id"],
            "name": profile["name"],
            "skin_url": profile["skins"][0]["url"]
        }

        setting["Launch"]["Select"] = minecraft_access_token_index["username"]

        logger.info(l_current["Minecraft"]["Auth"]["AuthSuccess"])

        return True

    else:
        seconds = int(setting['Launch']['MS_OAuth']['CheckTimes']) * \
                  int(setting['Launch']['MS_OAuth']['CheckInterval'])

        logger.warning(l_current["Minecraft"]["Auth"]["Errors"]["OAuth_Flow_TimeOut"].format(seconds=seconds))

        return False


async def launch_login(account_uuid=None):
    if account_uuid is None:
        if "Select" not in setting["Launch"]:
            # 需要warning log

            return False
        else:
            account = accounts[setting['Launch']['Select']]

    else:
        account = accounts[account_uuid]

    access_token_index = await code2token(code=account["refresh_token"],
                                          redirect_url=account["redirect_url"],
                                          login_mode=True)

    xbl_token_index = await auth5xbl(access_token_index["access_token"])

    xsts_token_index = await auth5xsts(xbl_token_index["Token"])

    minecraft_access_token_index = await auth5minecraft(xsts_token_index["DisplayClaims"]["xui"][0]["uhs"],
                                                        xsts_token_index["Token"])

    profile = await get_profile(minecraft_access_token_index["access_token"])

    logger.info(l_current["Minecraft"]["Auth"]["LoginSucces"])

    return profile["name"], profile["id"], minecraft_access_token_index["access_token"]

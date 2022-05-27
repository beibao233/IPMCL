import aiohttp
import hashlib
import json


async def uload(url, file_hash=None):
    """
    通过URL获取JSON树
    :param file_hash:
    :param url: 字符串URL
    :return: JSON转换的字典
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            json_data = await resp.text()

            if not (hashlib.sha1(await resp.read()).hexdigest() == file_hash or file_hash is None):
                return False

    data = json.loads(json_data)

    return data

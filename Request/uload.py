import aiohttp
import json


async def uload(url):
    """
    通过URL获取JSON树
    :param url: 字符串URL
    :return: JSON转换的字典
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            json_data = await resp.text()

    data = json.loads(json_data)

    return data

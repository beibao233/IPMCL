from IPMCL import setting
import aiohttp
import asyncio
import hashlib


async def fdownload(url, file_hash=None, retry: int = 0):
    if retry >= setting['Download']['CountOfRetry']:
        return False

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as resp:
                data = await resp.read()

                if hashlib.sha1(data).hexdigest() == file_hash or file_hash is None:
                    return data
                else:
                    return False
    except:
        await asyncio.sleep(setting['Download']['TimeAfterConnectionReset'])
        retry += 1
        return await fdownload(url, retry)

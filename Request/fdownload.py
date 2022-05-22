import aiohttp


async def fdownload(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as resp:
            data = await resp.read()

    return data

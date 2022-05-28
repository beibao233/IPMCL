import platform
import asyncio
import os

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    download_loop = asyncio.new_event_loop()
else:
    download_loop = asyncio.get_event_loop()


global base_path
base_path = os.path.dirname(__file__)

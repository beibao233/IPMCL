import platform
import asyncio
import sys
import os

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    download_loop = asyncio.new_event_loop()
else:
    download_loop = asyncio.get_event_loop()


base_path = os.path.dirname(os.path.realpath(sys.executable))

if not os.path.exists(os.path.join(base_path, "IPMCL")):
    base_path = os.path.dirname(__file__)

if not os.path.exists(os.path.join(base_path, "IPMCL")):
    # 需要提示

    exit()

import asyncio
import os

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
download_loop = asyncio.new_event_loop()

global base_path
base_path = os.path.dirname(__file__)

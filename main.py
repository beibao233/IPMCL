from System import operating_system
import asyncio
import os

if operating_system == "natives-windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

download_loop = asyncio.new_event_loop()

global base_path
base_path = os.path.dirname(__file__)

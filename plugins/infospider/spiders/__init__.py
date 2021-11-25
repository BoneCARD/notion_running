import aiohttp
import asyncio

sem = asyncio.Semaphore(10)  # 信号量，控制协程数，防止爬的过快

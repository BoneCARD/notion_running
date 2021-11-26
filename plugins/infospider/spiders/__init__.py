import aiohttp
import asyncio

sem = asyncio.Semaphore(10)  # 信号量，控制协程数，防止爬的过快
# 逛新闻网站的步骤
# 1、打开网站主页，找有价值的新闻
# 2、打开自己喜欢的分类，找有价值的新闻
# 巡视主站

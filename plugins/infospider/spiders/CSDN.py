import asyncio
import aiohttp
from bs4 import BeautifulSoup
from tomd import Tomd

from plugins.infospider.spiders.interfaces.i_spider import SpiderInterface


class csdn(SpiderInterface):

    @staticmethod
    async def download(url):
        async with aiohttp.ClientSession() as client:
            resp = await client.post(url)
            resp_text = await resp.text()
            page_info = str(BeautifulSoup(resp_text, 'html.parser').find("div", {"class":"blog-content-box"}))
            markdown = Tomd(page_info).markdown
            with open('make.md', 'w', encoding='utf-8') as file:
                file.write(markdown)
            with open("tmp.html", "w") as f:
                f.write(await resp.text())
            return resp.text()


asyncio.run(csdn.download("https://blog.csdn.net/weixin_54733110/article/details/117935299"))
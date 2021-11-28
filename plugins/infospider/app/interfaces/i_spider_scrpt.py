import re
import abc
import aiohttp
from tomd import Tomd


class SpiderInterface(abc.ABC):
    spider_name = None
    url_format = None

    @staticmethod
    def article_template():
        return {
            "link": "",
            "title": "",
            "description": "",
            "tags": [],
            "release_time": "",
            "author": "",
            "spider_object": "",
            "content": ""
        }

    @staticmethod
    async def request(url, method="get"):
        """
        下载文章的信息
        :param url:
        :param method:
        :return: None
        """
        async with aiohttp.ClientSession() as client:
            if method == "get":
                resp = await client.get(url)
            if method == "post":
                resp = await client.post(url)
            return await resp.text()

    @staticmethod
    def test_html_to_markdown(article_content):
        markdown = Tomd(article_content).markdown
        with open('make.md', 'w', encoding='utf-8') as file:
            file.write(markdown)

    def check_url(self, url):
        """
        检查url是否与爬虫匹配
        :return: bool
        """
        if re.match(self.url_format, url):
            return True
        return False

    async def get_article(self, url):
        """
        下载文章的信息
        :param url:
        :return: None
        """

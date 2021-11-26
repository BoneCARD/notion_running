import abc
from tomd import Tomd


class SpiderInterface(abc.ABC):
    @staticmethod
    def article_template():
        return {
            "link": "",
            "title": "",
            "tags": [],
            "release_time": "",
            "author": "",
            "spider_object": "",
            "content": ""
        }

    @staticmethod
    async def download(url):
        """
        下载文章的信息
        :param url:
        :return: None
        """
        pass

    @staticmethod
    def test_html_to_markdown(article_content):
        markdown = Tomd(article_content).markdown
        with open('make.md', 'w', encoding='utf-8') as file:
            file.write(markdown)

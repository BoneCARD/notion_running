import asyncio
from bs4 import BeautifulSoup

from plugins.infospider.app.interfaces.i_spider_scrpt import SpiderInterface


class spider(SpiderInterface):
    spider_name = "csdn"
    url_format = "https://blog.csdn.net/"

    async def get_article(self, url):
        _resp = BeautifulSoup(await self.request(url, "post"), 'html.parser')
        _article = self.article_template()
        _article["url"] = str(url)
        raw_article = _resp.find("div", {"class": "blog-content-box"})
        _article["title"] = str(raw_article.find("div", {"class": "article-title-box"}).text)
        _article["description"] = ""
        _article["tags"] = [_.text for _ in raw_article.find_all("a", {"class": "tag-link"})]
        _article["release_time"] = str(raw_article.find("span", {"class": "time"}).text).strip()
        _article["author"] = str(_resp.find("div", {"class": "profile-intro-name-boxTop"}).a.text).strip()
        _article["spider_object"] = self.spider_name
        _article["content"] = str(raw_article.article)
        return _article

    # async def get_news(self, ):


if __name__ == '__main__':
    asyncio.run(spider.get_article(spider, "https://blog.csdn.net/weixin_54733110/article/details/117935299"))
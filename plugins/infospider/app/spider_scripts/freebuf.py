import json
import asyncio
from bs4 import BeautifulSoup

from plugins.infospider.app.interfaces.i_spider_scrpt import SpiderInterface


class spider(SpiderInterface):
    spider_name = "freebuf"
    url_format = "https://www.freebuf.com/"

    async def get_article(self, url):
        try:
            article_id = url.split(".html")[0].split("/")[-1]
        except IndexError:
            raise Exception("link can't support to spider -- %s" % self.spider_name)
        api_resp = json.loads(await self.request("https://www.freebuf.com/fapi/frontend/post/info?id=%s" % article_id))
        _resp = BeautifulSoup(await self.request(url), 'html.parser')
        _article = self.article_template()
        _article["url"] = str(url)
        _article["title"] = str(_resp.find("div", {"class": "title"}).text)
        _article["description"] = ""
        _article["tags"] = [str(_.text).replace("#", "").strip() for _ in _resp.find_all("span", {"class": "tag"})]
        _article["release_time"] = str(_resp.find("span", {"class": "date"}).text).strip()
        _article["author"] = api_resp["data"]["post_author"]["username"]
        _article["spider_object"] = self.spider_name
        _article["content"] = api_resp["data"]["post_content"]
        return _article


if __name__ == '__main__':
    asyncio.run(spider.get_article(spider, "https://www.freebuf.com/news/306208.html"))

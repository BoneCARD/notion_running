import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup

from plugins.infospider.app.interfaces.i_spider import SpiderInterface

# 逛新闻网站的步骤
# 1、打开网站主页，找有价值的新闻
# 2、打开自己喜欢的分类，找有价值的新闻
# 巡视主站

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
sem = asyncio.Semaphore(10)  # 信号量，控制协程数，防止爬的过快


class spider_csdn(SpiderInterface):
    spider_name = "csdn"

    async def run(self, url):
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


class spider_wechat(SpiderInterface):
    spider_name = "wechat"

    async def run(self, url):
        _resp = BeautifulSoup(await self.request(url), 'html.parser')
        # 判断是否为文章
        if not str(_resp.find("meta", {"property": "og:type"}).attrs["content"]) == "article":
            raise Exception("link can't support to spider -- %s" % self.spider_name)
        _article = self.article_template()
        _article["url"] = str(url)
        # raw_article = _resp.find("div", {"class": "rich_media_inner"})
        _article["title"] = str(_resp.find("meta", {"property": "twitter:title"}).attrs["content"])
        _article["description"] = str(_resp.find("meta", {"property": "og:description"}).attrs["content"])
        _article["tags"] = []
        # 获取时间的思路：时间只存在script里面，首先找到script特有的id，再便利所有的script中含有'var ct = '元素的进行逐行便利便利
        script_id = _resp.script.attrs["nonce"]
        special_script = [str(_) for _ in _resp.find_all("script", {"nonce": str(script_id)}) if 'var ct = ' in str(_)][
            0]
        _article["release_time"] = special_script.split("var ct = \"")[1].split("\";")[0]
        _article["spider_object"] = self.spider_name
        author = str(_resp.find("meta", {"property": "twitter:creator"}).attrs["content"])  # 作者
        account = str(_resp.find("a", {"id": "js_name"}).text).strip()  # 公众号
        _article["author"] = account + ": " + author
        _article["content"] = str(_resp.find("div", {"class": "rich_media_content"}))
        print(_article["title"])
        return _article


class spider_freebuf(SpiderInterface):
    spider_name = "freebuf"

    async def get_(self, url):
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
    # asyncio.run(spider_csdn.run(spider_csdn, "https://blog.csdn.net/weixin_54733110/article/details/117935299"))
    # asyncio.run(spider_wechat.run(spider_wechat, "https://mp.weixin.qq.com/s?src=11&timestamp=1637913889&ver=3459&signature=Qobz6hHLmszqs8qgW0Y*N4smq96BMYtMKQG3-H2oWaJfs63mXcTCcO9X2OZZ0mO*SJtsUKnFKJdKkYMp0VxW1Sx8E2HPBDvRLfXUIYh8VebewOEn3dsm9SltmyXyhmV2&new=1"))
    # asyncio.run(spider_freebuf.run(spider_freebuf, "https://www.freebuf.com/news/306208.html"))
    pass

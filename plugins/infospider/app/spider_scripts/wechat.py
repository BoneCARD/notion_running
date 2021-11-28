import asyncio
from bs4 import BeautifulSoup

from plugins.infospider.app.interfaces.i_spider_scrpt import SpiderInterface


class spider(SpiderInterface):
    spider_name = "wechat"
    url_format = "https://mp.weixin.qq.com/"

    async def get_article(self, url):
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
        return _article


if __name__ == '__main__':
    asyncio.run(spider.get_article(spider, "https://mp.weixin.qq.com/s?src=11&timestamp=1637913889&ver=3459&signature=Qobz6hHLmszqs8qgW0Y*N4smq96BMYtMKQG3-H2oWaJfs63mXcTCcO9X2OZZ0mO*SJtsUKnFKJdKkYMp0VxW1Sx8E2HPBDvRLfXUIYh8VebewOEn3dsm9SltmyXyhmV2&new=1"))

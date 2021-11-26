import asyncio
import aiohttp
from bs4 import BeautifulSoup


from notion_running.plugins.infospider.app.interfaces.i_spider import SpiderInterface


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
sem = asyncio.Semaphore(10)  # 信号量，控制协程数，防止爬的过快


class spider_csdn(SpiderInterface):
    @staticmethod
    async def download(url):
        async with aiohttp.ClientSession() as client:
            resp = await client.post(url)
            return await resp.text()

    async def run(self, url):
        _resp = BeautifulSoup(await self.download(url), 'html.parser')
        _article = self.article_template()
        _article["url"] = str(url)
        raw_article = _resp.find("div", {"class": "blog-content-box"})
        _article["title"] = str(raw_article.find("div", {"class": "article-title-box"}).text)
        _article["content"] = str(raw_article.article)
        _article["tags"] = [_.text for _ in raw_article.find_all("a", {"class": "tag-link"})]
        _article["release_time"] = str(raw_article.find("span", {"class": "time"}).text).strip()
        _article["author"] = str(_resp.find("div", {"class": "profile-intro-name-boxTop"}).a.text).strip()
        return _article


class spider_wechat(SpiderInterface):
    @staticmethod
    async def download(url):
        async with aiohttp.ClientSession() as client:
            resp = await client.get(url)
            # print(await resp.text())
            return await resp.text()

    async def run(self, url):
        _resp = BeautifulSoup(await self.download(url), 'html.parser')
        _article = self.article_template()
        _article["url"] = str(url)
        raw_article = _resp.find("div", {"class": "rich_media_inner"})
        _article["title"] = str(raw_article.find("h1", {"id": "activity-name"}).text).strip()
        _article["content"] = str(raw_article.find("div", {"class": "rich_media_content"}))
        _article["tags"] = []
        _article["release_time"] = str(_resp.find("em", {"class": "rich_media_meta rich_media_meta_text"}).text).strip()
        # _article["author"] = str(_resp.find("div", {"class": "profile-intro-name-boxTop"}).a.text).strip()
        print(_article["release_time"])
        return _article


if __name__ == '__main__':
    # asyncio.run(spider_csdn.run(spider_csdn, "https://blog.csdn.net/weixin_54733110/article/details/117935299"))
    asyncio.run(spider_wechat.run(spider_wechat, "https://mp.weixin.qq.com/s?src=11&timestamp=1637913889&ver=3459&signature=Qobz6hHLmszqs8qgW0Y*N4smq96BMYtMKQG3-H2oWaJfs63mXcTCcO9X2OZZ0mO*SJtsUKnFKJdKkYMp0VxW1Sx8E2HPBDvRLfXUIYh8VebewOEn3dsm9SltmyXyhmV2&new=1"))

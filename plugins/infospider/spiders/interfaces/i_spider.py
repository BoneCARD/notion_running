import abc


class SpiderInterface(abc.ABC):

    async def download(self, url):
        """
        下载文章的信息
        :param url:
        :return: None
        """
        pass

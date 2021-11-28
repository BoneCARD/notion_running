from plugins.infospider.app.spider_svc import SpiderService


name = 'infospider'
description = '爬取网上新闻的插件'
address = None


async def enable(services):
    app = services.get('app_svc')
    spider_svc = SpiderService(services)
    await spider_svc.initiative_look()

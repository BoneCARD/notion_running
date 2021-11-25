from plugins.test.app.app_test import Apptest
from plugins.test.app.data_test import Datatest
from plugins.test.app.notionapi_test import Notionapitest

name = 'test'
description = '测试用'
address = None


async def enable(services):
    # 新增计划任务
    # app_test = Apptest(services=services)
    # app_test.add_task()

    # 数据库增删改查
    # data_test = Datatest(services=services)
    # await data_test.save_test()
    # await data_test.find_test()
    # await data_test.delete_test()

    # notion新增数据查看数据
    # notionapi_test = Notionapitest(services=services)
    # await notionapi_test.show_info()
    # await notionapi_test.querry_page()
    # await notionapi_test.add_page()
    # await notionapi_test.delete_page()
    pass

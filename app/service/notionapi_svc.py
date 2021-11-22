from abc import ABC
from notion_client import Client
from notion_client import AsyncClient

from app.service.interfaces.i_notionapi_svc import NotionAPIServiceInterface
from app.utility.base_service import BaseService
from app.utility.base_world import BaseWorld


class NotionAPIService(NotionAPIServiceInterface, BaseService, ABC):
    def __init__(self):
        # self.notion = AsyncClient(auth=BaseWorld.get_config("NOTION_TOKEN")).databases.create()
        self.notion = Client(auth=BaseWorld.get_config("NOTION_TOKEN"))
        self.log = self.add_service('notionapi_svc', self)

    async def list_api_users(self):
        return await self.notion.users.list()

    async def get_all_database_info(self):
        return await self.notion.databases.list()

    async def database_add_page(self, database_id, properties: dict, children: list):
        """
        :param database_id: 数据库的ID
        :param properties: 新Page的属性，demo_property_XXX有关的数据结构
            模板：
                demo = notionapi_svc.demo_property_Title("Name", "Yes")
                demo.update(notionapi_svc.demo_property_Checkbox("Check", True))
        :param children: 新Page的内容，demo_block_XXX有关的内容
        """
        self.notion.pages.create(parent={"database_id": database_id}, properties=properties, children=children)

    async def database_querry_page(self, database_id):
        """
        :param database_id:
        :return : list
        """
        # import json
        # print(json.dumps(self.notion.databases.query(database_id), indent=4))
        return self.notion.databases.query(database_id)["results"]


if __name__ == '__main__':
    from pprint import pprint

    BaseWorld.apply_config('main', BaseWorld.strip_yml("../../conf/default.yml")[0])
    notionapi_svc = NotionAPIService()
    import asyncio

    loop = asyncio.get_event_loop()

    demo = notionapi_svc.demo_property_Title("Name", "Yes")
    demo.update(notionapi_svc.demo_property_Checkbox("Check", True))
    demo.update(notionapi_svc.demo_property_URL("URL", "http://qq.com"))
    # loop.run_until_complete(notionapi_svc.database_add_page("85ca43b94ff24816bc2852209a00b5a4",
    #                                                         properties=demo,
    #                                                         children=[
    #                                                             notionapi_svc.demo_block_Paragraph([notionapi_svc.demo_Text("yes you are")])
    #                                                         ]))
    loop.run_until_complete(notionapi_svc.database_querry_page("85ca43b94ff24816bc2852209a00b5a4"))

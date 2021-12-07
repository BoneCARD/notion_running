from abc import ABC

import httpcore
from notion_client import Client
from notion_client import AsyncClient

from app.service.interfaces.i_notionapi_svc import NotionAPIServiceInterface
from app.utility.base_service import BaseService
from app.utility.base_world import BaseWorld


class NotionAPIService(NotionAPIServiceInterface, BaseService, ABC):
    def __init__(self):
        self.notion = AsyncClient(auth=BaseWorld.get_config("NOTION_TOKEN"))
        self.root_block_id = BaseWorld.get_config("NOTION_ROOT_ID")
        # self.notion = Client(auth=BaseWorld.get_config("NOTION_TOKEN"))
        self.log = self.add_service('notionapi_svc', self)

    async def list_api_users(self):
        return await self.notion.users.list()

    async def get_all_database_info(self):
        return await self.notion.databases.list()

    async def add_blocks(self, page_id, children: list = []):
        await self.notion.blocks.children.append(page_id, children=children)

    async def database_add_page(self, database_id, properties: dict, children: list = []):
        """
        在database数据库中添加page
        :param database_id: 数据库的ID
        :param properties: 新Page的属性，demo_property_XXX有关的数据结构
            模板：
                demo = notionapi_svc.demo_property_Title("Name", "Yes")
                demo.update(notionapi_svc.demo_property_Checkbox("Check", True))
        :param children: 新Page的内容，demo_block_XXX有关的内容
            模板：
                demo = [notionapi_svc.demo_block_Code("ip a", "bash")]
                demo.append(notionapi_svc.demo_block_Code("ip a", "bash"))
        """
        await self.notion.pages.create(parent={"database_id": database_id}, properties=properties, children=children)

    async def database_query_page(self, database_id):
        """
        在database数据库中查询page数据的信息
        :param database_id:
        :return : list
        """
        _ = await self.notion.databases.query(database_id)
        return _["results"]

    async def delete_page(self, page_id):
        await self.notion.blocks.delete(page_id)

    async def query_page(self, page_id):
        """
        查询page中的数据信息（但是官方并不是说page，说的是block）
        :param page_id:
        :return : list
        """
        return await self.notion.blocks.children.list(page_id)


if __name__ == '__main__':
    pass

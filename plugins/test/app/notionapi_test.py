import json

from app.utility.base_service import BaseService


class Notionapitest(BaseService):
    def __init__(self, services):
        self.log = self.create_logger('notionapiest_svc')
        self.notionapi_svc = services.get('notionapi_svc')
        self.page_id = "85ca43b9-4ff2-4816-bc28-52209a00b5a4"

    async def show_info(self):
        print(await self.notionapi_svc.list_api_users())
        print(await self.notionapi_svc.get_all_database_info())

    async def querry_page(self):
        firstdatabase = await self.notionapi_svc.database_querry_page(self.page_id)
        # database的列表信息
        print(json.dumps(firstdatabase, indent=5))
        # 查询database中第二个page的信息
        print(json.dumps(await self.notionapi_svc.querry_page(firstdatabase[1]["id"]), indent=5))

    async def add_page(self):
        # 设置page的属性信息
        properties = self.notionapi_svc.demo_property_Title("Name", "gogoog")
        properties.update(self.notionapi_svc.demo_property_URL("URL", "https://123.cc"))
        properties.update(self.notionapi_svc.demo_property_Checkbox("Check", True))
        # 设置子页中信息
        sub_page = [self.notionapi_svc.demo_block_Code("ip a", "bash")]
        # 在database中添加page
        await self.notionapi_svc.database_add_page(self.page_id, properties, sub_page)
        # 在page中添加信息

    async def delete_page(self):
        firstdatabase = await self.notionapi_svc.database_querry_page(self.page_id)
        delete_ids = []
        for _page in firstdatabase:
            for _property in _page["properties"]:
                if _page["properties"][_property]["type"] == "url" and _page["properties"][_property]["url"] == "https://123.cc":
                    if _page["id"] not in delete_ids:
                        delete_ids.append(_page["id"])
        for _id in delete_ids:
            await self.notionapi_svc.delete_page(_id)


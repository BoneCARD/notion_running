import json

from app.utility.base_service import BaseService


class Notionapitest(BaseService):
    def __init__(self, services):
        self.log = self.create_logger('notionapiest_svc')
        self.notionapi_svc = services.get('notionapi_svc')
        # self.page_id = "85ca43b9-4ff2-4816-bc28-52209a00b5a4"
        self.test_page_id = "eb0a9c339ee64692a3a64025bd05a397"

    async def show_info(self):
        print(await self.notionapi_svc.list_api_users())
        print(await self.notionapi_svc.get_all_database_info())

    async def querry_page(self):
        firstdatabase = await self.notionapi_svc.database_querry_page(self.test_page_id)
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
        await self.notionapi_svc.database_add_page(self.test_page_id, properties, sub_page)
        # 在page中添加信息

    async def delete_page(self):
        firstdatabase = await self.notionapi_svc.database_querry_page(self.test_page_id)
        delete_ids = []
        for _page in firstdatabase:
            for _property in _page["properties"]:
                if _page["properties"][_property]["type"] == "url" and _page["properties"][_property]["url"] == "https://123.cc":
                    if _page["id"] not in delete_ids:
                        delete_ids.append(_page["id"])
        for _id in delete_ids:
            await self.notionapi_svc.delete_page(_id)

    async def add_block(self):
        sub_page = [
            self.notionapi_svc.demo_text_block("code", [self.notionapi_svc.demo_Text("ip addr\nifconfig")], language="bash"),
            self.notionapi_svc.demo_text_block("heading_1", [self.notionapi_svc.demo_Text("head")]),
            self.notionapi_svc.demo_text_block("paragraph", [self.notionapi_svc.demo_Text("123123")], [self.notionapi_svc.demo_text_block("paragraph", [self.notionapi_svc.demo_Text("123123")])]),
            self.notionapi_svc.demo_text_block("bulleted_list_item", [self.notionapi_svc.demo_Text("123123")]),
            self.notionapi_svc.demo_text_block("to_do", [self.notionapi_svc.demo_Text("123123")]),
            # self.notionapi_svc.demo_external_block("image", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/The_Earth_seen_from_Apollo_17.jpg/1024px-The_Earth_seen_from_Apollo_17.jpg"),
            self.notionapi_svc.demo_external_block("image", "https://mmbiz.qpic.cn/mmbiz_gif/qq5rfBadR38Tm7G07JF6t0KtSAuSbyWtgFA8ywcatrPPlURJ9sDvFMNwRT0vpKpQ14qrYwN2eibp43uDENdXxgg/640?wx_fmt=gif"),
            self.notionapi_svc.demo_simple_block("divider")
        ]
        await self.notionapi_svc.add_blocks(self.test_page_id, sub_page)

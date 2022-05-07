import os
import json
import uuid
from datetime import datetime
import jieba.analyse
import jieba.posseg as p_seg
import pandas

from app.utility.base_service import BaseService
from app.utility.base_service import BaseWorld

special_word_list = ["", "+", "|", ":", "："]


class autorun_task(BaseService):
    def __init__(self, services, time_database_id, local_work_path):
        self.log = self.create_logger('autorun_task')
        self.app = services.get('app_svc')
        self.notionapi = services.get('notionapi_svc')
        self.time_database_id = time_database_id
        self.db_dir = os.path.join(local_work_path, "db")
        self.local_db_path = None
        self.N_Algorithm_info = [
            {
                "name": "算法1",
                "db": None,
                "generate": lambda _name: _name,
                "rate": 0.15
            },
            {
                "name": "算法2",
                "db": None,
                "generate": lambda _name: self._sort(self._cut(_name)),
                "rate": 0.3
            },
            {
                "name": "算法3",
                "db": None,
                "generate": lambda _name: self._sort(jieba.analyse.extract_tags(_name, 20, allowPOS=['ns', 'n', 'vn', 'v', 'nr'], withFlag=False)),
                "rate": 0.3
            },
        ]

    async def calculate_cost_time(self):
        """
        自动计算柳比歇夫时间统计法数据库中的事件花费时长
        :return:
        """
        # 获取柳比歇夫时间统计法的事件列表
        page_size = 10
        new_pages = await self.notionapi.database_query_page(self.time_database_id, page_size=page_size + 1)
        # 查看前10项是否有未填花费的时间的事件，计算并填入花费的时间
        for _index in range(page_size):
            if not new_pages[_index]["properties"]["汇总花费时长"]["formula"]["number"]:
                # 计算花费时长
                cost_min_time = (self.convert_ISO_8601(
                    new_pages[_index]["properties"]["自动创建日期"]["created_time"]) - self.convert_ISO_8601(
                    new_pages[_index + 1]["properties"]["自动创建日期"]["created_time"])).seconds / 60
                # 填入花费时长
                properties = self.notionapi.demo_property_normal("计算花费时长(auto)", cost_min_time, "number")
                await self.notionapi.database_update_page(new_pages[_index]["id"], properties)
                self.log.info(
                    f'{new_pages[_index]["properties"]["事件名称"]["title"][0]["plain_text"] + ":" + cost_min_time.__str__()}')

    @staticmethod
    def convert_ISO_8601(raw):
        return datetime.strptime(raw.split(".")[0], '%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def time_event_struct(a=None, b=None, c=None, d=None, e=None, f=None):
        return {
            "事件名称": a,
            "顺便做": b,
            "🎰大类-维度": c,
            "👣小类行为": d,
            "创建时间": e,
            "汇总花费时长": f
        }

    async def generate_db_path(self):
        """
        生成本周采集数据的数据库文件路径
        :return:
        """
        # 判断本周数据是否在数据库中
        _judge_list = [_ for _ in BaseWorld.getfile(self.db_dir) if self.local_week().split("(")[0] in _]
        if len(_judge_list) == 0:
            # 新周更新
            self.local_db_path = await self.transfo_training_set()
            # await self.Algorithm_1_generate_db()
            for _ in self.N_Algorithm_info:
                _["db"] = await self.Algorithm_generate_db1(_["generate"])
        if len(_judge_list) == 1:
            self.local_db_path = [_ for _ in BaseWorld.getfile(self.db_dir) if self.local_week().split("(")[0] in _][0]
        if len(_judge_list) > 1:
            raise Exception("[!]异常 有多个在同周生成的数据库数据，请检查数据库数据")

    async def transfo_training_set(self):
        """
        转化训练集
        :return:
        """
        # 获取柳比歇夫时间统计法数据库中的所有事件
        time_event_db = []
        start_cursor = None
        while True:
            raw_pages = await self.notionapi.database_query_page(self.time_database_id, start_cursor=start_cursor,
                                                                 complete_resp=True)
            # 提取事件名称、大类、小类、创建时间、花费时长
            for page in raw_pages["results"]:
                raw_event = self.time_event_struct(
                    page["properties"]["事件名称"]["title"][0]["plain_text"],
                    "" if not page["properties"]["顺便做"]["rich_text"] else page["properties"]["顺便做"]["rich_text"][0][
                        "plain_text"],
                    page["properties"]["🎰大类-维度"]["select"],
                    page["properties"]["👣小类行为"]["select"],
                    page["properties"]["创建时间"]["formula"]["string"],
                    page["properties"]["汇总花费时长"]["formula"]["number"],
                )
                # 去除不完整的事件
                if len([_ for _ in raw_event.values() if _ is None]) > 0:
                    # print(raw_event.values())
                    continue
                time_event_db.append(raw_event)
            if "has_more" not in raw_pages:
                raise Exception("[!]miss has_more")
            if not raw_pages["has_more"]:
                break
            else:
                start_cursor = raw_pages["next_cursor"]
        raw_db = json.dumps(time_event_db, indent=4, ensure_ascii=False)
        db_path = os.path.join(self.db_dir, "{}_{}.json".format(self.local_week(), uuid.uuid4().__str__()))
        with open(db_path, "w", encoding="utf-8") as f:
            print(len(raw_db))
            f.write(raw_db)
        return db_path

    @staticmethod
    def local_week():
        return str(datetime.now().strftime('%Y-%W(%m-%d)'))

    # async def generate_training_model(self):
    #     """
    #     生成机器学习模型
    #     :return:
    #     """
    #     await self.generate_db_path()
    #     # 读取本周数据，并转化为pandas格式
    #     with open(self.local_db_path, 'r', encoding="utf-8") as f:
    #         raw_db = f.read()
    #         json_db = json.loads(raw_db)
    #         panda_db = pandas.json_normalize(json_db)
    #         print(panda_db.groupby("事件名称").size())

    # @staticmethod
    # def parsing_eventName_meaning(sentence, single_cut=False, single_extract_tags=False, cut_flag=False,
    #                               single_extract_flag=False):
    #     """
    #     解析title 事件名称词义
    #     :return:
    #     """
    #     words = p_seg.cut(sentence)
    #     words_list = list([_.word for _ in words if _.word.strip() not in ["", "+", "|", ":", "："]])
    #     if single_cut:
    #         return words_list
    #     core_words = jieba.analyse.extract_tags(sentence, 20, allowPOS=['ns', 'n', 'vn', 'v', 'nr'], withFlag=True)
    #     # core_words_list = list([_.word for _ in core_words if _.word.strip() not in ["", "+", "|", ":", "："]])
    #     # if single_extract_tags:
    #     #     return core_words_list

    async def update_notion_select(self, page_id, small_OR_big, _uuid):
        """
        更新notion页面的大类小类标签
        :param page_id:
        :param small_OR_big:
        :param _uuid:
        :return:
        """
        if small_OR_big == 0:
            small_OR_big = "👣小类行为"
        elif small_OR_big == 1:
            small_OR_big = "🎰大类-维度"
        else:
            raise Exception("[!]update_notion_select()未输入有效的大类小类")

        # 填入标签选项
        properties = self.notionapi.demo_property_normal(small_OR_big, {"id": _uuid}, "select")
        await self.notionapi.database_update_page(page_id, properties)

    async def update_notion_autolog(self, page_id, Algorithm_name, rate):
        """
        更新notion页面的自动化记录
        :param page_id:
        :param Algorithm_name:
        :param rate:
        :return:
        """
        properties = self.notionapi.demo_property_text("rich_text", "自动化记录", "{}：{}".format(Algorithm_name, rate))
        await self.notionapi.database_update_page(page_id, properties)

    async def Algorithm_generate_db1(self, _generate):
        """
        完全匹配的场景:统计“事件名称”的比率统计
        :return:
        """
        Algorithm_statistics_db = {}
        with open(self.local_db_path, 'r', encoding="utf-8") as f:
            raw_db = f.read()
            json_db = json.loads(raw_db)
            for _cell in json_db:
                db_cell_name = _generate(_cell["事件名称"])
                # 数据库中以大类、小类uuid的组合作为唯一标识，这也是db1数据库的匹配标识
                sum_uuid = "{} {}".format(str(_cell["🎰大类-维度"]["id"]), str(_cell["👣小类行为"]["id"]))
                # _list列表用于下方for循环，加循环的目的是为了对有冒号:：的事件名称做分割提取，提取冒号前面的字段加入的数据库中做统计
                _list = [db_cell_name]
                [_list.append(db_cell_name.split(_)[0]) for _ in [_ for _ in [":", "："] if _ in db_cell_name]]
                for range_index in range(2 if len(_list) >= 2 else 1):
                    # 判断字段是否在数据库中，如果在字段值加一，不在则新增该字段到数据库中
                    if _list[range_index] in Algorithm_statistics_db:
                        if sum_uuid in Algorithm_statistics_db[_list[range_index]]:
                            Algorithm_statistics_db[_list[range_index]][sum_uuid] += 1
                        else:
                            Algorithm_statistics_db[_list[range_index]].update({sum_uuid: 1})
                    else:
                        Algorithm_statistics_db.update({_list[range_index]: {sum_uuid: 1}})

            Algorithm_db = {}
            for _key, _value in Algorithm_statistics_db.items():
                # 统计所有单元的数量总和（单元就是上面的db_cell_name）
                all_num = 0
                # 记录单元中最高的数量（每个单元都有自己数量）
                _max_num = 0
                # 记录最大数量的单元uuid
                _max_uuid = None
                for _uuid, _uuid_num in _value.items():
                    all_num = all_num + _uuid_num
                    if _uuid_num > _max_num:
                        _max_num = _uuid_num
                        _max_uuid = _uuid
                Algorithm_db.update({_key: [_max_uuid, _max_num / all_num]})
            # print(json.dumps(Algorithm_db, indent=4, ensure_ascii=False))
            return Algorithm_db

    # async def Algorithm_generate_db2(self, _generate):
    #     """
    #
    #     :param _generate:
    #     :return:
    #     """
    #     Algorithm_statistics_db = {}
    #     with open(self.local_db_path, 'r', encoding="utf-8") as f:
    #         raw_db = f.read()
    #         json_db = json.loads(raw_db)
    #         for _cell in json_db:
    #             db_cell_name_list = _generate(_cell["事件名称"])
    #             sum_uuid = "{} {}".format(str(_cell["🎰大类-维度"]["id"]), str(_cell["👣小类行为"]["id"]))
    #             _list = [db_cell_name]
    #             [_list.append(db_cell_name.split(_)[0]) for _ in [_ for _ in [":", "："] if _ in db_cell_name]]
    #             for range_index in range(2 if len(_list) >= 2 else 1):
    #                 if _list[range_index] in Algorithm_statistics_db:
    #                     if sum_uuid in Algorithm_statistics_db[_list[range_index]]:
    #                         Algorithm_statistics_db[_list[range_index]][sum_uuid] += 1
    #                     else:
    #                         Algorithm_statistics_db[_list[range_index]].update({sum_uuid: 1})
    #                 else:
    #                     Algorithm_statistics_db.update({_list[range_index]: {sum_uuid: 1}})
    #
    #         Algorithm_db = {}
    #         for _key, _value in Algorithm_statistics_db.items():
    #             all_num = 0
    #             _max_num = 0
    #             _max_uuid = None
    #             for _uuid, _uuid_num in _value.items():
    #                 all_num = all_num + _uuid_num
    #                 if _uuid_num > _max_num:
    #                     _max_num = _uuid_num
    #                     _max_uuid = _uuid
    #             Algorithm_db.update({_key: [_max_uuid, _max_num / all_num]})
    #         # print(json.dumps(Algorithm_db, indent=4, ensure_ascii=False))
    #         return Algorithm_db

    async def Algorithm_run(self):
        """
        完全匹配的场景:统计“事件名称”的运行
        :return:
        """
        await self.generate_db_path()
        for _ in self.N_Algorithm_info:
            if not _["db"]:
                _["db"] = await self.Algorithm_generate_db1(_["generate"])
        # 获取柳比歇夫时间统计法的事件列表，获取未标记标签的事件
        page_size = 20
        _filter = {
            "and": [
                {
                    "or": [
                        {
                            "property": "🎰大类-维度",
                            "select": {
                                "is_empty": True
                            }
                        },
                        {
                            "property": "👣小类行为",
                            "select": {
                                "is_empty": True
                            }
                        },
                    ],
                },
                {
                    "property": "自动化记录",
                    "rich_text": {
                        "is_empty": True
                    }
                },
            ]
        }
        new_pages = await self.notionapi.database_query_page(self.time_database_id, _filter=_filter, page_size=page_size)
        # 查看前10项是否有未填花费的时间的事件，计算并填入花费的时间
        for _index in range(len(new_pages)):
            N_flag = False
            for _ in self.N_Algorithm_info:
                page_name = new_pages[_index]["properties"]["事件名称"]["title"][0]["plain_text"]
                compare_data = _["generate"](page_name)
                # 根据事件名称在数据库中进行匹配
                if compare_data in _["db"] and _["db"][compare_data][1] > _["rate"]:
                    # 更新命中的匹配结果到notion中
                    _uuid_list = _["db"][compare_data][0].split(" ")
                    # 填入标签选项
                    await self.update_notion_select(new_pages[_index]["id"], 1, _uuid_list[0])
                    await self.update_notion_select(new_pages[_index]["id"], 0, _uuid_list[1])
                    # 填入自动化记录
                    await self.update_notion_autolog(new_pages[_index]["id"], _["name"], _["db"][compare_data][1])
                    N_flag = True
                    break

    @staticmethod
    def _sort(_list):
        list(set(_list)).sort()
        return _list.__str__()

    @staticmethod
    def _cut(sentence, withFlag=False):
        if not withFlag:
            _data = []
            [_data.append(_.word) for _ in p_seg.cut(sentence) if _.word.strip() not in special_word_list]
        else:
            _data = {}
            [_data.update({_.word: _.flag}) for _ in p_seg.cut(sentence) if _.word.strip() not in special_word_list]
        return _data

    async def run(self):
        scheduler = self.app.get_scheduler()
        scheduler.add_job(self.calculate_cost_time, 'interval', seconds=600)
        scheduler.add_job(self.Algorithm_run, 'interval', seconds=600)
        scheduler.add_job(self.transfo_training_set, 'cron', day_of_week=1, hour=11)
        # await self.transfo_training_set()
        # await self.Algorithm_run()


if __name__ == '__main__':
    pass

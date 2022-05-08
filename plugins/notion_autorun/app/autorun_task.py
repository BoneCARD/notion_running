import os
import json
import uuid
import logging
from datetime import datetime
import jieba.analyse
import jieba.posseg as p_seg

from app.utility.base_service import BaseService
from app.utility.base_service import BaseWorld

special_word_list = ["", "+", "|", ":", "："]
jieba.setLogLevel(logging.INFO)


class autorun_task(BaseService):
    def __init__(self, services, time_database_id, local_work_path):
        self.log = self.add_service('autorun_task', self)
        self.app = services.get('app_svc')
        self.notionapi = services.get('notionapi_svc')
        self.time_database_id = time_database_id
        self.db_dir = os.path.join(local_work_path, "db")
        self.local_db_path = None
        self.select_uuid_db = {}
        self.N_Algorithm_info = [
            {
                "name": "[1]",
                "db": None,
                "key_generate": lambda _name: _name,
                # "statistics_value_generate": lambda big_value, small_value: str(big_value)+" "+str(small_value),
                "rate": 0.15
            },
            {
                "name": "[2]",
                "db": None,
                "key_generate": lambda _name: self._sort(self._cut(_name)),
                # "statistics_value_generate": lambda big_value, small_value: str(big_value) + " " + str(small_value),
                "rate": 0.3
            },
            {
                "name": "[3]",
                "db": None,
                "key_generate": lambda _name: self._sort(jieba.analyse.extract_tags(_name, 20, allowPOS=['ns', 'n', 'vn', 'v', 'nr'], withFlag=False)),
                # "statistics_value_generate": lambda big_value, small_value: str(big_value) + " " + str(small_value),
                "rate": 0.3
            },
        ]
        self.S_Algorithm_info = [
            {
                "name": "[5]",
                "db": None,
                "key_generate": lambda _name: self._sort(self._cut(_name), False),
                "rate": 0.4
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
                self.log.info(f'计算用时 {new_pages[_index]["properties"]["事件名称"]["title"][0]["plain_text"] + ":" + cost_min_time.__str__()}')

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
        if len(_judge_list) == 1:
            self.local_db_path = [_ for _ in BaseWorld.getfile(self.db_dir) if self.local_week().split("(")[0] in _][0]
        if len(_judge_list) > 1:
            raise Exception("[!]异常 有多个在同周生成的数据库数据，请检查数据库数据")
        await self.Algorithm_db_update()

    async def transfo_training_set(self):
        """
        转化训练集
        :return:
        """
        # 获取柳比歇夫时间统计法数据库中的所有事件
        time_event_db = []
        start_cursor = None
        while True:
            raw_pages = await self.notionapi.database_query_page(self.time_database_id, start_cursor=start_cursor, complete_resp=True)
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
            # print(len(raw_db))
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

    async def update_notion_select(self, page_id, small_OR_big, _uuid, page_name):
        """
        更新notion页面的大类小类标签
        :param page_id:
        :param small_OR_big:
        :param _uuid:
        :param page_name:
        :return:
        """
        if small_OR_big == 0:
            small_OR_big = "👣小类行为"
        elif small_OR_big == 1:
            small_OR_big = "🎰大类-维度"
        else:
            raise Exception("[!]update_notion_select()未输入有效的大类小类")

        # 填入标签选项
        self.log.info(f"更新[{page_name}]的[{small_OR_big}]标签:{self.select_uuid_db[_uuid]}")
        properties = self.notionapi.demo_property_normal(small_OR_big, {"id": _uuid}, "select")
        await self.notionapi.database_update_page(page_id, properties)

    async def update_notion_autolog(self, page_id, Algorithm_name, rate, page_name):
        """
        更新notion页面的自动化记录
        :param page_id:
        :param Algorithm_name:
        :param rate:
        :param page_name:
        :return:
        """
        content = "{}：{}".format(Algorithm_name, rate)
        self.log.info(f"更新[{page_name}]的[自动化记录]:{content}")
        properties = self.notionapi.demo_property_text("rich_text", "自动化记录", content)
        await self.notionapi.database_update_page(page_id, properties)

    async def Algorithm_generate_db1(self, _generate):
        """
        完全匹配的场景:统计“事件名称”的比率统计
        :return:
        """
        Algorithm_statistics_db = self.Algorithm_generate_statistics_db(
            self.local_db_path,
            _generate,
            lambda big_value, small_value: str(big_value)+" "+str(small_value),
        )
        return self.Algorithm_generate_rate_db(Algorithm_statistics_db)

    async def Algorithm_generate_db2(self, _generate):
        """

        :param _generate:
        :return:
        """
        big_Algorithm_statistics_db = self.Algorithm_generate_statistics_db(
            self.local_db_path, _generate,
            lambda big_value, small_value: str(big_value),
        )
        small_Algorithm_statistics_db = self.Algorithm_generate_statistics_db(
            self.local_db_path, _generate,
            lambda big_value, small_value: str(small_value),
        )
        big_Algorithm_db = self.Algorithm_generate_rate_db(big_Algorithm_statistics_db)
        small_Algorithm_db = self.Algorithm_generate_rate_db(small_Algorithm_statistics_db)
        # print(json.dumps(big_Algorithm_db, indent=4, ensure_ascii=False))
        # print(json.dumps(small_Algorithm_db, indent=4, ensure_ascii=False))
        return {"big": big_Algorithm_db, "small": small_Algorithm_db}

    def Algorithm_generate_statistics_db(self, local_db_path, key_generate, value_generate):
        with open(local_db_path, 'r', encoding="utf-8") as f:
            _db = {}
            raw_db = f.read()
            json_db = json.loads(raw_db)
            for _cell in json_db:
                # 提取大类小类的uuid与值
                for _ in ["🎰大类-维度", "👣小类行为"]:
                    select_uuid = _cell[_]["id"]
                    select_name = _cell[_]["name"]
                    if select_uuid not in self.select_uuid_db:
                        self.select_uuid_db.update({select_uuid: select_name})
                # 识别传入
                _key = key_generate(_cell["事件名称"])
                if type(_key) is str:
                    db_cell_name_list = [_key]
                elif type(_key) is list:
                    db_cell_name_list = _key
                else:
                    raise Exception("[!]Algorithm_generate_statistics_db()方法传入了奇怪的生成器和名字数据，生成的类型："+str(type(key_generate(_cell["事件名称"]))))
                for range_index in range(len(db_cell_name_list)):
                    _uuid = value_generate(str(_cell["🎰大类-维度"]["id"]), str(_cell["👣小类行为"]["id"]))
                    if db_cell_name_list[range_index] in _db:
                        if _uuid in _db[db_cell_name_list[range_index]]:
                            _db[db_cell_name_list[range_index]][_uuid] += 1
                        else:
                            _db[db_cell_name_list[range_index]].update({_uuid: 1})
                    else:
                        _db.update({db_cell_name_list[range_index]: {_uuid: 1}})
            return _db

    @staticmethod
    def Algorithm_generate_rate_db(_statistics_db):
        Algorithm_db = {}
        for _key, _value in _statistics_db.items():
            # 统计该字段所有uuid的数量值
            all_num = 0
            # 记录uuid中最高的数量值
            _max_num = 0
            # 记录最高数量值的uuid
            _max_uuid = None
            for _uuid, _uuid_num in _value.items():
                all_num = all_num + _uuid_num
                if _uuid_num > _max_num:
                    _max_num = _uuid_num
                    _max_uuid = _uuid
            if all_num <= 2:
                continue
            # 更新数据库: 最高数量值的uuid， 最高数量值uuid的比率， 最高数量值uuid的的数量值， 所有uuid的数量值总和
            Algorithm_db.update({_key: [_max_uuid, _max_num / all_num, _max_num, all_num, _key]})
        return Algorithm_db

    async def Algorithm_db_update(self):
        for _ in self.N_Algorithm_info:
            _["db"] = await self.Algorithm_generate_db1(_["key_generate"])
        self.S_Algorithm_info[0]["db"] = await self.Algorithm_generate_db2(self.S_Algorithm_info[0]["key_generate"])

    async def Algorithm_run(self):
        """
        完全匹配的场景:统计“事件名称”的运行
        :return:
        """
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
            page_name = new_pages[_index]["properties"]["事件名称"]["title"][0]["plain_text"]
            N_flag = False
            for _ in self.N_Algorithm_info:
                compare_data = _["key_generate"](page_name)
                # 根据事件名称在数据库中进行匹配
                if compare_data in _["db"] and _["db"][compare_data][1] > _["rate"]:
                    # 更新命中的匹配结果到notion中
                    _uuid_list = _["db"][compare_data][0].split(" ")
                    # 填入标签选项
                    await self.update_notion_select(new_pages[_index]["id"], 1, _uuid_list[0], page_name)
                    await self.update_notion_select(new_pages[_index]["id"], 0, _uuid_list[1], page_name)
                    # 填入自动化记录
                    await self.update_notion_autolog(new_pages[_index]["id"], _["name"], "%.2f"%float(_["db"][compare_data][1]), page_name)
                    N_flag = True
                    break
            # 算法5
            if not N_flag:
                big_log = await self.Algorithm_1_extend_1_run(page_name, new_pages[_index]["id"])
                small_log = await self.Algorithm_5_extend_1_run(page_name, new_pages[_index]["id"], "small")
                if not big_log:
                    big_uuid, big_log = await self.Algorithm_5_run(page_name, "big")
                    if big_uuid:
                        await self.update_notion_select(new_pages[_index]["id"], 1, big_uuid, page_name)
                if not small_log:
                    small_uuid, small_log = await self.Algorithm_5_run(page_name, "small")
                    if small_uuid:
                        await self.update_notion_select(new_pages[_index]["id"], 0, small_uuid, page_name)
                if small_log or big_log:
                    await self.update_notion_autolog(new_pages[_index]["id"], f"{big_log[0]}+{small_log[0]}", f"{big_log[1]}+{small_log[1]}", page_name)

    async def Algorithm_1_extend_1_run(self, page_name, page_id):
        """
        算法1的扩展算法，识别事件名称是否有冒号的特殊字符进行切割，取第一个作为大类的判别元素，并在算法1数据库中寻找结果
        :param page_name:
        :param page_id:
        :return:
        """
        split_words = [_ for _ in [":", "："] if _ in page_name]
        if len(split_words) > 0:
            page_name_0 = page_name.split(split_words[0])[0]
            Algorithm_1 = self.N_Algorithm_info[0]
            if page_name_0 in Algorithm_1["db"] and Algorithm_1["db"][page_name_0][1] > Algorithm_1["rate"]:
                _uuid_0 = Algorithm_1["db"][page_name_0][0].split(" ")[0]
                await self.update_notion_select(page_id, 1, _uuid_0, page_name)
                return [f"[1.1](big)", f"{page_name_0} {'%.2f'%Algorithm_1['db'][page_name_0][1]}"]
        return []

    async def Algorithm_5_extend_1_run(self, page_name, page_id, _type):
        """
        算法1的扩展算法，识别事件名称是否有冒号的特殊字符进行切割，取第一个作为大类的判别元素，并在算法1数据库中寻找结果
        :param page_name:
        :param page_id:
        :param _type:
        :return:
        """
        split_words = [_ for _ in [":", "："] if _ in page_name]
        if len(split_words) > 0:
            page_name_1 = page_name.split(split_words[0])[1]
            max_uuid, _log = await self.Algorithm_5_run(page_name_1, _type)
            if max_uuid:
                await self.update_notion_select(page_id, 0, max_uuid, page_name)
                _log[0] = f"[5.1]({_type})"
                return _log
        return []

    async def Algorithm_5_run(self, page_name, _type):
        # 分词
        Algorithm_5 = self.S_Algorithm_info[0]
        words_list = Algorithm_5["key_generate"](page_name)
        hit_list = []
        for word in words_list:
            if word in Algorithm_5["db"][_type] and Algorithm_5["db"][_type][word][1] >= Algorithm_5["rate"]:
                hit_list.append(Algorithm_5["db"][_type][word])
        max_uuid = None
        max_num = 0
        max_key = None
        for _ in hit_list:
            if _[2] > max_num:
                max_num = _[2]
                max_uuid = _[0]
                max_key = _[-1]
        if max_uuid:
            return max_uuid, [f"{Algorithm_5['name']}({_type})", f"{max_key} {str(max_num)}"]
        return "", []

    @staticmethod
    def _sort(_list, _str=True):
        list(set(_list)).sort()
        if _str:
            return _list.__str__()
        else:
            return _list

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
        await self.generate_db_path()
        await self.Algorithm_run()
        await self.calculate_cost_time()
        scheduler.add_job(self.calculate_cost_time, 'interval', seconds=600)
        scheduler.add_job(self.Algorithm_run, 'interval', seconds=600)
        scheduler.add_job(self.generate_db_path, 'cron', day_of_week=1, hour=11)


if __name__ == '__main__':
    pass

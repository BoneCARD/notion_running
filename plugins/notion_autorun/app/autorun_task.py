import os
import json
import uuid
from pyhanlp import *
from datetime import datetime
import jieba.analyse
import jieba.posseg as pseg
import pandas

from app.utility.base_service import BaseService
from app.utility.base_service import BaseWorld


class autorun_task(BaseService):
    def __init__(self, services, time_database_id, local_work_path):
        self.log = self.create_logger('autorun_task')
        self.app = services.get('app_svc')
        self.notionapi = services.get('notionapi_svc')
        self.time_database_id = time_database_id
        self.db_dir = os.path.join(local_work_path, "db")

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
    def time_event_struct(a=None, b=None, c=None, d=None, e=None, f=None, g: list = None, h: list = None):
        return {
            "事件名称": a,
            "顺便做": b,
            "大类": c,
            "小类": d,
            "创建时间": e,
            "汇总花费时长": f,
            "事件名称词义分析": g,
            "顺便做词义分析": h,
        }

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
                # print(json.dumps(page["properties"], indent=4, ensure_ascii=False))
                # return
                raw_event = self.time_event_struct(
                    page["properties"]["事件名称"]["title"][0]["plain_text"],
                    "" if not page["properties"]["顺便做"]["rich_text"] else page["properties"]["顺便做"]["rich_text"][0]["plain_text"],
                    page["properties"]["大类"]["select"],
                    page["properties"]["小类"]["select"],
                    page["properties"]["创建时间"]["formula"]["string"],
                    page["properties"]["汇总花费时长"]["formula"]["number"],
                    # 对事件名称依据+做切割，并分析每个时间的语义组成
                    self.parsing_eventName_meaning(page["properties"]["事件名称"]["title"][0]["plain_text"])
                )
                # 去除不完整的事件
                if len([_ for _ in raw_event.values() if _ is None]) > 0:
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
            f.write(raw_db)
        return db_path

    @staticmethod
    def local_week():
        return str(datetime.now().strftime('%Y-%W(%m-%d)'))

    async def generate_training_model(self):
        """
        生成机器学习模型
        :return:
        """
        # 判断本周数据是否在数据库中
        _judge_list = [_ for _ in BaseWorld.getfile(self.db_dir) if self.local_week().split("(")[0] in _]
        if len(_judge_list) == 0:
            local_web_db_path = await self.transfo_training_set()
        if len(_judge_list) == 1:
            local_web_db_path = [_ for _ in BaseWorld.getfile(self.db_dir) if self.local_week().split("(")[0] in _][0]
        if len(_judge_list) > 1:
            raise Exception("[!]异常 有多个在同周生成的数据库数据，请检查数据库数据")
        # 读取本周数据，并转化为pandas格式
        with open(local_web_db_path, 'r', encoding="utf-8") as f:
            raw_db = f.read()
            json_db = json.loads(raw_db)
            panda_db = pandas.json_normalize(json_db)
            print(panda_db.groupby("事件名称").size())

    @staticmethod
    def parsing_eventName_meaning(sentence):
        """
        解析title 事件名称词义
        :return:
        """
        words = pseg.cut(sentence)
        core_words = jieba.analyse.extract_tags(sentence, 20)
        words_list = list(words)
        for _ in core_words:
            flag = False
            for __ in words_list:
                if _ == __.word:
                    flag = True
                    print(_, __.flag)
            if not flag:
                print("[!]", "error", _)
        return list(HanLP.extractKeyword(sentence, 20))

    async def identify_label(self):
        """
        识别柳比歇夫时间统计法数据库中的事件标签
        :return:
        """
        # 使用模型识别事件的大类、小类

    async def run(self):
        scheduler = self.app.get_scheduler()
        scheduler.add_job(self.calculate_cost_time, 'interval', seconds=600)
        # scheduler.add_job(self.transfo_training_set, 'cron', day_of_week=1, hour=11)
        # await self.transfo_training_set()
        await self.generate_training_model()


if __name__ == '__main__':
    pass

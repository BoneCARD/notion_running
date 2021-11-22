import time
import copy
import asyncio
from abc import ABC
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.service.interfaces.i_event_svc import EventServiceInterface
from app.utility.base_service import BaseService


class EventService(EventServiceInterface, BaseService, ABC):
    def __init__(self):
        # 事件需要有触发条件，发生时间，结果处理，事件关闭
        self.log = self.add_service('even_svc', self)
        self.loop = None
        self.scheduler = AsyncIOScheduler()
        # self.projects_queue = []
        # self.projects_index = []

    # _projectStates = {
    #     "init": -1, # 计划还未被解析
    #     "running": 0, # 计划正在执行或正在循环
    #     "completed": 1, # 计划已经运行完成
    #     "missed": 2, # 错过执行时间
    #     "exception": 10
    # }
    # _projectType = {
    #     "loop": {
    #         "type": "loop",
    #         "frequency": None,  # 运行频率
    #     }, # 相隔固定时间循环执行，类似秒表计时，半小时执行一次
    #     "schedule": {
    #         "type": "schedule",
    #         "startTime": None,  # 开始时间
    #         "frequency": None,  # 运行频率
    #         "runTimes": None,  # 执行次数
    #     }, # 指定某个时间定时执行，类似与闹钟固定每天某个时间执行，又或者就某天某时间执行
    # }
    # _projectTemplate = {
    #     "name": None,  # 计划的主题和子主题，用 "/" 隔开;（唯一标识）
    #     "type": None,   # 相隔时间类型和定时定点执行两种类型
    #     "runProperty": {
    #         "type": None,
    #     },
    #     "_state": _projectStates["init"],  # 状态
    #     "_durationTime": None,  # 总共运行的时长
    #     "_lastTime": None,  # 最后一次运行的时间
    #     "_createTime": BaseService.get_current_timestamp(),  # 创建时间
    #     "callbackObject": None,  # 回调函数（方法）
    #     "callbackKwargs": {},
    #     "_handle": None
    # }

    def get_projectTemplate(self):
        return copy.deepcopy(self._projectTemplate)

    @staticmethod
    def get_frequency(unit, weight):
        _unit_list = {
            "month": 1 * 60 * 60 * 24 * 7 * 30,
            "week": 1 * 60 * 60 * 24 * 7,
            "day": 1 * 60 * 60 * 24,
            "hour": 1 * 60 * 60,
            "minute": 1 * 60,
            "second": 1
        }
        if unit not in _unit_list:
            raise Exception("超出了频率设定的单元方式")
        return _unit_list[unit] * weight

    def create_project(self, name, callbackObject, callbackKwargs, frequency=None, startTime=None, runTimes=None):
        _T = self.get_projectTemplate()
        _T["name"] = name
        _T["callbackObject"] = callbackObject
        _T["callbackKwargs"] = callbackKwargs
        _T["frequency"] = frequency
        if startTime:
            _T["startTime"] = startTime
        if runTimes:
            _T["runTimes"] = runTimes
        return _T

    def get_loop(self):
        if not self.loop:
            self.loop = asyncio.get_event_loop()
        return self.loop

    def run_forever(self):
        try:
            self.log.info('All systems ready.')
            self.get_loop().run_forever()
        except KeyboardInterrupt:
            pass
            # self.get_loop().run_until_complete(services.get('app_svc').teardown(main_config_file=args.environment))

    def project_observe(self, newProject):
        """
        注册一个计划
        :param newProject:
        :return bool:
        """
        try:
            BaseService.template_matching(newProject, self.get_projectTemplate())
            self._add_project(newProject)
            return True
        except Exception as E:
            self.log.logger.exception("[EXCEPTION] %s" % E)
            return False

    def project_resolver(self, _project):
        """
        解析一个计划
        :param _project: 一个格式化的计划单元
        :return: int
        """

        return

    async def project_loader(self):
        while True:
            for _project in self.projects_queue:
                _later = self.project_resolver(_project)
                if _later is None:
                    continue
                elif _later == 0:
                    self.loop.call_soon(_project["callback"], **_project["callbackKwargs"])
                elif _later > 0 and _later <= self.cyclingTime:
                    self.loop.call_later(_later, _project["callback"], **_project["callbackKwargs"])
            await asyncio.sleep(self.cyclingTime)

    '''private'''

    def _add_project(self, newProject):
        if newProject["name"] in self.projects_index:
            raise Exception("禁止传入重复名字的计划进列队")
        self.projects_index.append(newProject["name"])
        self.projects_queue.append(newProject)


if __name__ == '__main__':
    pass

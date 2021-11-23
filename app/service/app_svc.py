import time
import copy
import asyncio
from abc import ABC
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.service.interfaces.i_event_svc import EventServiceInterface
from app.utility.base_service import BaseService


class ApplicationService(EventServiceInterface, BaseService, ABC):
    def __init__(self):
        # 事件需要有触发条件，发生时间，结果处理，事件关闭
        self.log = self.add_service('app_svc', self)
        self.loop = asyncio.get_event_loop()
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self._loaded_plugins = []

    def get_loop(self):
        return self.loop
    
    def get_scheduler(self):
        return self.scheduler
        
    def run_forever(self):
        try:
            self.log.info('All systems ready.')
            self.get_loop().run_forever()
        except KeyboardInterrupt:
            pass
            # self.get_loop().run_until_complete(services.get('app_svc').teardown(main_config_file=args.environment))


if __name__ == '__main__':
    pass

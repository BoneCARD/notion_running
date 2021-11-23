import os
import asyncio

from abc import ABC
import aiohttp_jinja2
import jinja2
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.objects.c_plugin import Plugin
from app.service.interfaces.i_app_svc import ApplicationServiceInterface
from app.utility.base_service import BaseService


class ApplicationService(ApplicationServiceInterface, BaseService, ABC):
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

    async def load_plugins(self, plugins):
        def trim(p):
            if p.startswith('.'):
                return False
            return True

        async def load(p):
            plugin = Plugin(name=p)
            if plugin.load_plugin():
                await self.get_service('data_svc').store(plugin)
                self._loaded_plugins.append(plugin)

            if plugin.name in self.get_config('plugins'):
                await plugin.enable(self.get_services())
                self.log.info('Enabled plugin: %s' % plugin.name)

        for plug in filter(trim, plugins):
            if not os.path.isdir('plugins/%s' % plug) or not os.path.isfile('plugins/%s/hook.py' % plug):
                self.log.error('Problem locating the "%s" plugin. Ensure code base was cloned recursively.' % plug)
                exit(0)
            asyncio.get_event_loop().create_task(load(plug))

        templates = ['plugins/%s/templates' % p.lower() for p in self.get_config('plugins')]
        templates.append('templates')
        aiohttp_jinja2.setup(self.application, loader=jinja2.FileSystemLoader(templates))


if __name__ == '__main__':
    pass

import os

from app.utility.base_world import BaseWorld
from plugins.notion_autorun.app.autorun_task import autorun_task


name = 'notion_autorun'
description = 'notion时间管理自动化'
address = None
local_path = os.path.dirname(__file__)


async def enable(services):
    conf_path = os.path.join(local_path, "conf", "conf.yml")
    conf_dict = BaseWorld.strip_yml(conf_path)
    autorun = autorun_task(services, conf_dict[0]["notion_database_id"]["柳比歇夫时间统计法"], local_path)
    await autorun.run()

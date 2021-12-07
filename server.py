# -*- coding: utf-8 -*
import logging
import argparse
from aiohttp import web

from app.service.data_svc import DataService
from app.service.app_svc import ApplicationService
from app.service.notionapi_svc import NotionAPIService
from app.utility.base_world import BaseWorld


def setup_logger(level=logging.DEBUG):
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(levelname)-5s (%(filename)s:%(lineno)s %(funcName)s) %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    for logger_name in logging.root.manager.loggerDict.keys():
        if logger_name in ('aiohttp.server', 'asyncio'):
            continue
        else:
            logging.getLogger(logger_name).setLevel(100)
    logging.captureWarnings(True)


async def start_server():
    # await auth_svc.apply(app_svc.application, BaseWorld.get_config('users'))
    runner = web.AppRunner(app_svc.application)
    await runner.setup()
    await web.TCPSite(runner, BaseWorld.get_config('host'), BaseWorld.get_config('port')).start()


def run_tasks(services):
    loop = app_svc.get_loop()
    plugins = BaseWorld.strip_yml(plugins_config_path)[0]["plugins"]
    loop.run_until_complete(app_svc.load_plugins(plugins))
    loop.run_until_complete(start_server())

    try:
        logging.info('All systems ready.')
        loop.run_forever()
    except (KeyboardInterrupt, SystemError):
        loop.run_until_complete(services.get('app_svc').teardown(main_config_file=args.environment))


if __name__ == '__main__':
    # 接收命令行输入的参数
    parser = argparse.ArgumentParser('Welcome to the system')
    parser.add_argument('-E', '--environment', required=False, default='local', help='Select an env. file to use')
    parser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level", default='INFO')
    args = parser.parse_args()

    setup_logger(getattr(logging, args.logLevel))

    # 设置配置文件路径
    main_config_path = 'conf/%s.yml' % args.environment
    plugins_config_path = 'conf/plugins.yml'
    BaseWorld.apply_config('main', BaseWorld.strip_yml(main_config_path)[0])

    # 启动公共服务
    data_svc = DataService()
    # app_svc = ApplicationService()
    app_svc = ApplicationService(application=web.Application(client_max_size=5120 ** 2))
    notionapi_svc = NotionAPIService()

    run_tasks(app_svc.get_services())

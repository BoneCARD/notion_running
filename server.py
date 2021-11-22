import argparse
import asyncio
import logging

from app.service.data_svc import DataService
from app.service.event_svc import EventService
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


def run_tasks(services):
    loop = asyncio.get_event_loop()
    # loop.create_task()
    # loop.run_until_complete(data_svc.)

    # try:
    #     logging.info('All systems ready.')
    #     loop.run_forever()
    # except KeyboardInterrupt:
    #     loop.run_until_complete(services.get('app_svc').teardown(main_config_file=args.environment))


if __name__ == '__main__':
    # Receive command line arguments
    parser = argparse.ArgumentParser('Welcome to the system')
    parser.add_argument('-E', '--environment', required=False, default='default', help='Select an env. file to use')
    parser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level", default='INFO')
    args = parser.parse_args()

    setup_logger(getattr(logging, args.logLevel))

    main_config_path = 'conf/%s.yml' % args.environment
    BaseWorld.apply_config('main', BaseWorld.strip_yml(main_config_path)[0])
    #
    data_svc = DataService()
    event_svc = EventService()
    notionapi_svc = NotionAPIService()

    run_tasks(notionapi_svc.get_services())

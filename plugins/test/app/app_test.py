from app.utility.base_service import BaseService


class Apptest(BaseService):
    def __init__(self, services):
        self.log = self.create_logger('apptest_svc')
        self.app_svc = services.get('app_svc')

    @staticmethod
    def do():
        print("[new task]")

    def add_task(self):
        scheduler = self.app_svc.get_scheduler()
        scheduler.add_job(self.do, 'interval', seconds=3)


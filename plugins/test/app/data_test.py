from app.utility.base_service import BaseService


class Datatest(BaseService):
    def __init__(self, services):
        self.log = self.create_logger('datatest_svc')
        self.data_svc = services.get('data_svc')
        self.col = "test"

    async def save_test(self):
        demo = self.data_svc.dbStructure.document[self.col]
        demo["link"] = "https://11.com"
        demo["source"] = "go"
        demo["description"] = "a test"
        self.data_svc.update_document(self.col, demo)

    async def find_test(self):
        print(self.data_svc.search_document(self.col, **{"link": "https://11.com"}))

    async def delete_test(self):
        id = self.data_svc.search_document(self.col, **{"link": "https://11.com"})["id"]
        self.data_svc.delete_document(self.col, id)


import gridfs
import pymongo
from abc import ABC
from bson import ObjectId
from datetime import datetime
from pymongo import ASCENDING, DESCENDING

from app.utility.base_world import BaseWorld
from app.utility.base_service import BaseService
from app.service.interfaces.i_data_svc import DataServiceInterface


class DataService(DataServiceInterface, BaseService, ABC):
    """
    数据服务
    """

    def __init__(self):
        self.log = self.add_service('data_svc', self)
        mongo_conf = BaseWorld.get_config("mongodb")
        self.client = pymongo.MongoClient(mongo_conf["host"], mongo_conf["port"])
        if mongo_conf["auth"]:
            self.client[mongo_conf["authbase"]].authenticate(mongo_conf["username"], mongo_conf["password"])
        if mongo_conf["savebase"] not in self.client.list_database_names():
            self.log.info("INFO[data_svc] %s no exits." % mongo_conf["savebase"])
        self.client = self.client[mongo_conf["savebase"]]
        self._init_db(mongo_conf["savebase"])

    def _init_db(self, db):
        """
        初始化数据库
        :return: None
        """
        for _c in self.dbStructure.collection:
            if _c not in self.client.list_collection_names():
                self.client.create_collection(_c)
                self.log.info("INFO[data_svc] Create %s-collection in %s-db." % (_c, db))
            for _i in self.dbStructure.index[_c]:
                if _i not in self.client[_c].index_information():
                    self.client[_c].create_index(**self.dbStructure.index[_c][_i])
                    self.log.info("INFO[data_svc] Create %s-index %s-collection in %s-db." % (_i, _c, db))

    def create_collection(self, name):
        """
        数据库新增集合
        :param name: 集合的名字
        :return: None
        """
        self.client.create_collection(name)

    def update_document(self, collection, document: dict):
        """
        数据库新增文档内容，根据document中的id为标识进行数据新增，如果已有则更新数据
        :param collection: 文档存放的集合名
        :param document: 文档内容
        :return: None
        """
        self.client[collection].replace_one({"id": document["id"]}, document, upsert=True)

    def delete_document(self, collection, _uuid):
        """
        删除文档
        :param collection: 文档存放的集合名
        :param _uuid: 更新文档的uuid
        :return: None
        """
        self.client[collection].delete_one({"id": _uuid})

    def search_document(self, collection, **filter_):
        """
        单个文档的精准查询
        :param collection: 文档存放的集合名
        :param filter_: 查询规则
        :return: dict
        """
        return self.client[collection].find_one(filter_, {"_id": 0})

    def search_documents(self, collection, **filter_):
        """
        多个文档的查询
        :param collection: 文档存放的集合名
        :param filter_: 查询规则
        :return: dict
        """
        # if filter_.get("name"):
        #     filter_.update({"name": {"$regex": filter_.pop("name"), "$options": "i"}})
        return list(self.client[collection].find(filter_, {"_id": 0}).sort("_id", -1))

    ''' 文件管理 '''

    async def upload_payload_indexer(self, params, file_data):
        """
        上传文件
        :param params:
        :param file_data:
        :return:
        """
        if params.get("filename"):
            filter_dict = {"name": params["filename"]}
            if self.client["core_payload"].find_one(filter_dict):
                raise Exception("【{}】 文件名与已有 payload 文件重复".format(params["filename"]))
            else:
                file_id = gridfs.GridFS(self.client, "core_payload").put(file_data, filename=params["filename"])
                insert_dict = {
                    "file_id": str(file_id),
                    "name": params.get("filename"),
                    "create_time": datetime.now().replace(microsecond=0),
                    "update_time": datetime.now().replace(microsecond=0),
                    "is_deleted": 0,
                }
            self.client["core_payload"].insert_one(insert_dict)
            return True
        return False

    async def modify_payload_indexer(self, payload_id, payload_name, payload_data):
        """
        编辑 payload 数据库操作
        :param payload_id:
        :param payload_name:
        :param payload_data:
        :return:
        """
        # 先删除后存储
        gridfs.GridFS(self.client, "core_payload").delete({"_id": ObjectId(payload_id)})
        file_id = gridfs.GridFS(self.client, "core_payload").put(payload_data.encode(), filename=payload_name)
        filter_dict = {"file_id": payload_id}
        update_dict = {
            "$set": {
                "file_id": str(file_id),
                "update_time": datetime.now().replace(microsecond=0)
            }
        }
        self.client["core_payload"].update_one(filter_dict, update_dict)

    def payload_specific_indexer(self, file_id):
        """
        获取具体的 payload 数据
        :param file_id:
        :return:
        """
        file = gridfs.GridFS(self.client, "core_payload").find_one({"_id": ObjectId(file_id)})
        if not file:
            return b''
        return file.read()

    def get_payload(self, filename):
        """
        获取 payload
        :param filename:
        :return:
        """
        file = gridfs.GridFS(self.client, "core_payload").find_one({"filename": filename})
        if not file:
            return b''
        return file.read()

    def get_payloads(self):
        """
        获取所有 payload 信息列表
        :return:
        """
        payloads = []
        for payload in self.client["core_payload"].find({}).sort("update_time", -1):
            payloads.append({"name": payload.get("name"), "creator": payload.get("creator")})
        return payloads

    class dbStructure:
        collection = ["news"]
        index = {
            # DESCENDING 降序 -1
            # ASCENDING 升序 1
            # "news": {
            #     "link_-1_source_1": { # index索引名字命名的方式是根据输入keys与值做拼接的
            #         "keys": [("link",DESCENDING), ("source",ASCENDING)],
            #         "unique": True
            #     }
            # },
            "news": {
                "link_-1": {
                    "keys": [("link", DESCENDING)],
                    "unique": True
                }
            }
        }
        document = {
            "news": {
                "link": "",
                "type": [],
                "collect": {
                    "title": "",
                    "content": "",
                    "property": {},
                    "_collect time": BaseWorld.get_current_timestamp(),
                    "release time": "",
                    "other": None
                },
                "extract": {},
                "translate": {},
                "source": "",
                "plugin object": "",
                "feedback": {
                    "read confirm": False,
                    "valuable confirm": False,
                    "classify": {},
                    "interested in": [],
                    "uninterested in": []
                }

            }
        }

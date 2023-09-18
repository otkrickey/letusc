from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from letusc.URLManager import URLManager
from letusc.util import env_bool

__all__ = [
    "MongoManager",
]


class MongoManager:
    _client: AsyncIOMotorClient

    @staticmethod
    def get_client() -> AsyncIOMotorClient:
        if not hasattr(MongoManager, "_client"):
            MongoManager._client = AsyncIOMotorClient(URLManager.getMongo())
        return MongoManager._client

    @staticmethod
    def get_db(database_name: str) -> AsyncIOMotorDatabase:
        return MongoManager.get_client()[database_name]

    @staticmethod
    def get_collection(
        database_name: str, collection_name: str
    ) -> AsyncIOMotorCollection:
        return MongoManager.get_db(database_name)[collection_name]

    @staticmethod
    def close():
        if hasattr(MongoManager, "_client"):
            MongoManager._client.close()

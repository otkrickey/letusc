from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from .url import URLManager

__all__ = [
    "DBManager",
]


class DBManager:
    _client: AsyncIOMotorClient

    @staticmethod
    def get_client() -> AsyncIOMotorClient:
        if not hasattr(DBManager, "_client"):
            DBManager._client = AsyncIOMotorClient(URLManager.getMongo())
        return DBManager._client

    @staticmethod
    def get_db(database_name: str) -> AsyncIOMotorDatabase:
        return DBManager.get_client()[database_name]

    @staticmethod
    def get_collection(
        database_name: str, collection_name: str
    ) -> AsyncIOMotorCollection:
        return DBManager.get_db(database_name)[collection_name]

    @staticmethod
    def close():
        if hasattr(DBManager, "_client"):
            DBManager._client.close()

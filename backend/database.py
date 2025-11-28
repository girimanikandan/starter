"""
MongoDB Database Connection
----------------------------
Handles connection to MongoDB
Provides database and collection access
"""

from motor.motor_asyncio import AsyncIOMotorClient
from config import get_settings

settings = get_settings()

class Database:
    """
    MongoDB Database Manager
    Singleton pattern for database connection
    """
    
    client: AsyncIOMotorClient = None # type: ignore
    
    @classmethod
    async def connect_db(cls):
        """
        Connect to MongoDB
        Called when application starts
        """
        try:
            cls.client = AsyncIOMotorClient(settings.mongodb_uri)
            # Test connection
            await cls.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {settings.mongodb_uri}")
            print(f"📊 Database: {settings.database_name}")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            raise
    
    @classmethod
    async def close_db(cls):
        """
        Close MongoDB connection
        Called when application shuts down
        """
        if cls.client:
            cls.client.close()
            print("🔌 MongoDB connection closed")
    
    @classmethod
    def get_database(cls):
        """
        Get database instance
        Returns: AsyncIOMotorDatabase
        """
        return cls.client[settings.database_name]
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """
        Get specific collection
        Args:
            collection_name: Name of the collection
        Returns: AsyncIOMotorCollection
        """
        db = cls.get_database()
        return db[collection_name]

# Collection name
VALIDATIONS_COLLECTION = "validations"
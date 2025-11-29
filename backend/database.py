"""
MongoDB Database Connection
----------------------------
Handles connection to MongoDB Atlas using certifi for stable SSL connection.
"""
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi 
# Removed: import ssl (no longer needed)
from config import get_settings

settings = get_settings()

class Database:
    """
    MongoDB Database Manager
    """
    
    client: AsyncIOMotorClient = None # type: ignore
    
    @classmethod
    async def connect_db(cls):
        print("Attempting to connect to MongoDB Atlas...")
        
        try:
            # FIX: Removed unsupported 'ssl_context' argument and its associated code. 
            # We rely on ServerApi and tlsCAFile (certifi.where()) which are supported.
            cls.client = AsyncIOMotorClient(
                settings.mongodb_uri, 
                serverSelectionTimeoutMS=5000,
                server_api=ServerApi('1'),     # Enforce modern protocol
                tlsCAFile=certifi.where(),      # Use reliable certificate store (Supported)
            )
            
            # Test connection
            await cls.client.admin.command('ping')
            
            print(f"✅ Connected to MongoDB: {settings.mongodb_uri[:30]}...")
            print(f"📊 Database: {settings.database_name}")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """
        Close MongoDB connection
        """
        if cls.client:
            cls.client.close()
            print("🔌 MongoDB connection closed")
    
    @classmethod
    def get_database(cls):
        return cls.client[settings.database_name]
    
    @classmethod
    def get_collection(cls, collection_name: str):
        db = cls.get_database()
        return db[collection_name]

# Collection name
VALIDATIONS_COLLECTION = "validations"
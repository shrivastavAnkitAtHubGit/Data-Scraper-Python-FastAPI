from typing import List, Dict
from app.storage.storage_strategy import StorageStrategy


class NOSQLStorageStrategy(StorageStrategy):
    def __init__(self, database_url: str):
        print("initialization")

    def save(self, data: List[Dict[str, any]]):
       print("Implement NoSQL Save Function")

    def load(self) -> List[Dict[str, any]]:
       print("Implement NoSQL Load Function")
        

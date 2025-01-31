from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

from app.notification.console_notification import ConsoleNotificationStrategy
from app.notification.sms_notification import SMSNotificationStrategy
from app.storage.json_strategy import JSONStorageStrategy
from app.storage.sql_strategy import SQLStorageStrategy
from app.storage.nosql_strategy import NOSQLStorageStrategy
from .models import Settings, Product
from .scraper import WebScraper
from .configs import NOTIFICATION_METHOD, STATIC_TOKEN, DATABASE_FILE, STORAGE_METHOD

app = FastAPI()

security = HTTPBearer()

# Dependency to verify the provided token
def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != STATIC_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return credentials.credentials

# Endpoint to trigger the scraping process
@app.post("/start-scraping", dependencies=[Depends(validate_token)])
def initiate_scraping(setting: Settings):
    if STORAGE_METHOD == "json":
        storageStrategy = JSONStorageStrategy(DATABASE_FILE)
    elif STORAGE_METHOD == "sql":
        storageStrategy = SQLStorageStrategy("sqlite:///products.db")
    elif STORAGE_METHOD == "nosql":
        storageStrategy = NOSQLStorageStrategy("nosqldb:///products.db")
    else:
        raise HTTPException(status_code=400, detail="Unsupported storage method")

    if NOTIFICATION_METHOD == "console":
        notificationStrategy = ConsoleNotificationStrategy()
    elif NOTIFICATION_METHOD == "sms":
        notificationStrategy = SMSNotificationStrategy()
    elif NOTIFICATION_METHOD == "email":
        notificationStrategy = SMSNotificationStrategy()
    else:
        raise HTTPException(status_code=400, detail="Unsupported notification method")

    scraper = WebScraper(setting, storageStrategy, notificationStrategy)
    scraper.start_scraping()
    total_Scraped_Product_Count = len(scraper.scraped_products)
    updated_count = scraper.cache_and_update_storage()
    return {
        "message": f"Scraping Complete. Total Scraped Product Count: {total_Scraped_Product_Count}. Updated Products Count: {updated_count}."
    }

# Endpoint to fetch scraped data
@app.get("/scraped-data", response_model=List[Product], dependencies=[Depends(validate_token)])
def get_scraped_data():
    """Fetch the scraped data from the storage."""
    # Assuming storage strategy can load data from the relevant storage type (json, sql, or nosql)
    if STORAGE_METHOD == "json":
        storageStrategy = JSONStorageStrategy(DATABASE_FILE)
    elif STORAGE_METHOD == "sql":
        storageStrategy = SQLStorageStrategy("sqlite:///products.db")
    elif STORAGE_METHOD == "nosql":
        storageStrategy = NOSQLStorageStrategy("mongodb:///products.db")
    else:
        raise HTTPException(status_code=400, detail="Unsupported storage method")

    scraped_data = storageStrategy.load()
    if not scraped_data:
        raise HTTPException(status_code=404, detail="No scraped data found")
    return scraped_data
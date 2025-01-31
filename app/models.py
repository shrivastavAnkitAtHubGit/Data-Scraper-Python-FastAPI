from pydantic import BaseModel, Field
from typing import Optional

class Settings(BaseModel):
    limit: Optional[int] = Field(None, description="Maximum number of pages to scrape (optional). If not provided, all pages will be scraped.")
    proxy: Optional[str] = Field(None, description="Proxy server URL to route the scraping requests through (optional).")

class Product(BaseModel):
    product_title: str
    product_price: float
    path_to_image: str

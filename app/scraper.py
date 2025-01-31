from bs4 import BeautifulSoup
import requests
import time
import redis
from pydantic import ValidationError

from app.notification.notification_strategy import NotificationStrategy
from app.configs import IMAGE_FOLDER, REDIS_DB, REDIS_HOST, REDIS_PORT, RETRY_LIMIT, RETRY_WAIT_TIME
from app.storage.storage_strategy import StorageStrategy
from .models import Settings, Product
from .utils import fetch_image

class WebScraper:
    def __init__(self, setting: Settings, storageStrategy: StorageStrategy, notificationStrategy: NotificationStrategy):
        self.setting = setting
        self.storageStrategy = storageStrategy
        self.notificationStrategy = notificationStrategy
        self.base_url = "https://dentalstall.com/shop/"
        self.scraped_products = []
        self.redis_connection = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    def start_scraping(self):
        page_number = 1
        skipped_count = 0
        while True:
            if self.setting.limit and page_number > self.setting.limit:
                break

            page_url = f"{self.base_url}?page={page_number}"
            print(f"Fetching page: {page_url}")
            page_response = self.fetch_page(page_url)
            if not page_response:
                break

            soup = BeautifulSoup(page_response.text, 'html.parser')
            product_items = soup.select("li.product")
            if not product_items:
                print(f"No products found on page {page_number}.")
                break

            page_skipped = 0
            for item in product_items:
                title_element = item.select_one(".woo-loop-product__title a")
                price_element = item.select_one(".price .woocommerce-Price-amount bdi")
                image_element = item.select_one(".mf-product-thumbnail img")

                if not title_element or not price_element or not image_element:
                    print(f"Skipping product on page {page_number}. Missing fields. Title: {bool(title_element)}, Price: {bool(price_element)}, Image: {bool(image_element)}")
                    page_skipped += 1
                    continue

                title = title_element.text.strip()
                try:
                    price = float(price_element.text.strip().replace('₹', '').replace(',', ''))
                except ValueError:
                    print(f"Skipping product on page {page_number}. Invalid price format. Title: {title}")
                    page_skipped += 1
                    continue

                image_url = image_element.get("data-lazy-src") or image_element.get("src")
                if not image_url:
                    print(f"Skipping product on page {page_number}. Missing image URL. Title: {title}")
                    page_skipped += 1
                    continue

                image_path = fetch_image(image_url, IMAGE_FOLDER)

                try:
                    product = Product(product_title=title, product_price=price, path_to_image=image_path)
                    self.scraped_products.append(product)
                except ValidationError as e:
                    print(f"Skipping product on page {page_number}. Validation error: {e}")
                    page_skipped += 1

            skipped_count += page_skipped
            print(f"Page {page_number} summary: Total products: {len(product_items)}, Skipped: {page_skipped}")
            page_number += 1

        final_message = f"Scraping completed. Total products scraped: {len(self.scraped_products)}, Total skipped: {skipped_count}"
        self.notificationStrategy.send_notification(final_message)

    def fetch_page(self, url: str):
        for attempt in range(RETRY_LIMIT):
            try:
                proxies = {"http": self.setting.proxy, "https": self.setting.proxy} if self.setting.proxy else None
                response = requests.get(url, proxies=proxies)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                print(f"Failed to fetch (attempt {attempt + 1}/{RETRY_LIMIT}): {e}. Retrying...")
                time.sleep(RETRY_WAIT_TIME)
        print(f"Failed to retrieve page after {RETRY_LIMIT} attempts: {url}")
        return None

    def cache_and_update_storage(self) -> int:
        current_products = self.storageStrategy.load()
        existing_titles = {product["product_title"]: product for product in current_products}

        updated_products_count = 0
        for product in self.scraped_products:
            cached_price = self.redis_connection.get(product.product_title)
            if cached_price and float(cached_price) == product.product_price:
                continue

            self.redis_connection.set(product.product_title, product.product_price)
            if product.product_title in existing_titles:
                if existing_titles[product.product_title]["product_price"] != product.product_price:
                    existing_titles[product.product_title] = product.dict()
                    updated_products_count += 1
            else:
                existing_titles[product.product_title] = product.dict()
                updated_products_count += 1

        self.storageStrategy.save(list(existing_titles.values()))
        return updated_products_count

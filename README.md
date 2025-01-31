# Scraper Project

This project is a web scraping tool designed to extract product data from a specified website. The scraped data can be stored in various formats, including JSON files or SQL databases. Additionally, the project includes notification functionality to keep stakeholders updated on the scraping status via console messages, SMS, or email. Built using FastAPI and BeautifulSoup, the project leverages the Strategy Design Pattern for flexible and easy-to-modify storage and notification options.

## Features

- Extracts product data, including title, price, and image, from a given website.
- Supports storing scraped data in JSON files or SQL databases.
- Provides status notifications through different channels: console, SMS, or email.
- Implements the Strategy Design Pattern for extensible storage and notification strategies.
- Uses Pydantic for data validation and integrity checks.
- Includes a retry mechanism to handle temporary server-related issues.
- Additionally, it provides an endpoint to fetch the scraped data.

## Prerequisites

- Python 3.8 or higher
- Redis server (for caching product prices)

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/scraper-project.git
    <!-- cd scraper-project -->
    ```

2. **Create and activate a virtual environment:**
    ```sh
    python3 -m venv scraper_env
    source scraper_env/bin/activate  # On Windows: scraper_env\Scripts\activate
    ```

3. **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Configure Redis:**
    Ensure Redis is installed and running on your machine. You can install Redis using the following commands
    - **Windows:**
      Download and install Redis from [Redis for Windows](https://github.com/microsoftarchive/redis/releases).

    - **macOS:**
      ```sh
      brew install redis
      brew services start redis
      ```

## Configuration

1. **Update configuration settings:**
    Modify the `app/settings.py` file to configure the database file path, static token, image folder location, Retry parameters and Redis connection parameters.

2. **Configure notification strategies:**
    - **SMS Notification:** Update the `sms_notification.py` with Implementation.
    - **Email Notification:** Update the `email_notification.py` with Implementation.

## Running the Application

1. **Start the FastAPI application:**
    ```sh
    python run.py
    ```

2. **Send the API request to start scraping:**
    - Using cURL (without proxy):
    ```sh
    curl --location "http://127.0.0.1:8000/start-scraping" ^
    --header "accept: application/json" ^
    --header "Content-Type: application/json" ^
    --header "Authorization: Bearer your_static_token" ^
    --data "{\"limit\": 2}"
    ```


3. **Check the output:**

    - Console notifications will display the scraping status directly in the terminal.
    - For SMS notifications (not implemented), ensure your phone number and SMS API settings are correctly configured.
    - For email notifications (not implemented), ensure that SMTP server settings and email addresses are properly set up.

## Additional Feature
1. **Send the API request to fetch scraped data:**
    - Using cURL:
    ```sh
    curl --location "http://127.0.0.1:8000/scraped-data" ^
    --header "accept: application/json" ^
    --header "Authorization: Bearer your_static_token"
    ```
## Extending the Project

    To add new storage or notification strategies:
    - Create a new class that implements the appropriate strategy interface (StorageStrategy or NotificationStrategy).
    - Update the main application to incorporate the new strategy.


"""
AuraGold Live Price Scraper
Monitors live gold and silver prices from auragold.in
Designed to be hosted on Render/Vercel
"""

import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | Gold: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Custom formatter for dual price logging
class PriceFormatter(logging.Formatter):
    def format(self, record):
        return f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {record.msg}"

# Update logger with custom formatter
for handler in logger.handlers:
    handler.setFormatter(PriceFormatter())

# Website URL
URL = "https://auragold.in"

# Refresh interval in seconds (1 minute)
REFRESH_INTERVAL = 60


def setup_driver():
    """Setup Chrome driver with headless options for hosting environments"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # For Render/Vercel hosting - use system Chrome if available
    chrome_binary = os.environ.get("CHROME_BIN")
    if chrome_binary:
        chrome_options.binary_location = chrome_binary
    
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
    if chromedriver_path:
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    
    return driver


def extract_prices(driver):
    """
    Extract gold and silver prices from the page.
    Both prices are in elements with class 'live__price__container' containing span with class 'price'
    First container = Gold, Second container = Silver
    """
    try:
        # Wait for the page to load and JavaScript to render
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "live__price__container"))
        )
        
        # Give extra time for JavaScript to fully render dynamic content
        time.sleep(2)
        
        # Find all live price containers
        price_containers = driver.find_elements(By.CLASS_NAME, "live__price__container")
        
        if len(price_containers) < 2:
            logger.error(f"Expected 2 price containers, found {len(price_containers)}")
            return None, None
        
        # Extract gold price (first container)
        gold_container = price_containers[0]
        gold_price_element = gold_container.find_element(By.CLASS_NAME, "price")
        gold_price = gold_price_element.text.strip()
        
        # Extract silver price (second container)
        silver_container = price_containers[1]
        silver_price_element = silver_container.find_element(By.CLASS_NAME, "price")
        silver_price = silver_price_element.text.strip()
        
        return gold_price, silver_price
        
    except TimeoutException:
        logger.error("Timeout waiting for price elements to load")
        return None, None
    except NoSuchElementException as e:
        logger.error(f"Could not find price element: {e}")
        return None, None
    except Exception as e:
        logger.error(f"Error extracting prices: {e}")
        return None, None


def log_prices(gold_price, silver_price):
    """Log prices with timestamp"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{current_time} | Gold: {gold_price} | Silver: {silver_price}")


def run_scraper():
    """Main scraper function that runs continuously"""
    print("=" * 60)
    print("AuraGold Live Price Monitor")
    print("=" * 60)
    print(f"Monitoring URL: {URL}")
    print(f"Refresh Interval: {REFRESH_INTERVAL} seconds")
    print("=" * 60)
    print()
    
    driver = None
    
    try:
        print("Initializing browser...")
        driver = setup_driver()
        print("Browser initialized successfully!")
        print()
        print("Starting price monitoring...")
        print("-" * 60)
        
        while True:
            try:
                # Navigate to the page
                driver.get(URL)
                
                # Extract prices
                gold_price, silver_price = extract_prices(driver)
                
                if gold_price and silver_price:
                    log_prices(gold_price, silver_price)
                else:
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"{current_time} | ERROR: Could not fetch prices")
                
                # Wait for the next refresh
                time.sleep(REFRESH_INTERVAL)
                
            except Exception as e:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"{current_time} | ERROR: {str(e)}")
                time.sleep(REFRESH_INTERVAL)
                
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("Scraper stopped by user")
        print("=" * 60)
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        if driver:
            driver.quit()
            print("Browser closed.")


if __name__ == "__main__":
    run_scraper()

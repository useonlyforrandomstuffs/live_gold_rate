"""
Flask Web Server for AuraGold Price Monitor
This provides a web interface and API endpoint for the scraper
Suitable for hosting on Render/Vercel
"""

from flask import Flask, jsonify, render_template_string
from datetime import datetime
import threading
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
from dotenv import load_dotenv
from email_sender import GmailSender

app = Flask(__name__)

isSent_gold = False
isSent_silver = False

load_dotenv()

# Global storage for prices
price_data = {
    "gold_price": "Loading...",
    "silver_price": "Loading...",
    "last_updated": None,
    "status": "initializing"
}

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
        
    except (TimeoutException, NoSuchElementException, Exception) as e:
        print(f"Error extracting prices: {e}")
        return None, None


def price_monitor():
    """Background thread that continuously monitors prices"""
    global price_data
    global isSent_silver
    global isSent_gold
    driver = None
    
    try:
        print("Initializing browser for price monitoring...")
        driver = setup_driver()
        print("Browser initialized successfully!")
        
        while True:
            try:
                driver.get(URL)
                gold_price, silver_price = extract_prices(driver)
                
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if gold_price and silver_price:
                    price_data = {
                        "gold_price": gold_price,
                        "silver_price": silver_price,
                        "last_updated": current_time,
                        "status": "success"
                    }
                    
                    if(not(isSent_gold) and (price_data['gold_price'] < int(os.getenv('THRESHOLD_GOLD')))):
                        sender = GmailSender()
                        html_content = f"""
                        <html>
                            <body>
                                <h2>Gold Price Update</h2>
                                <p>Current gold price: <strong>₹{price_data['gold_price']}</strong></p>
                            </body>
                        </html>
                        """
                        sender.send_email(
                            to_email="nitishm.23it@kongu.edu",
                            subject="Gold Price Dropped!!",
                            body=html_content,
                            is_html=True
                        )
                        isSent_gold = True
                        print("Gold price mail sent successfully!")
                        
                    
                    if(not(isSent_silver) and (price_data['silver_price'] < int(os.getenv('THRESHOLD_SILVER')))):
                        sender = GmailSender()
                        html_content = f"""
                        <html>
                            <body>
                                <h2>Silver Price Update</h2>
                                <p>Current silver price: <strong>₹{price_data['silver_price']}</strong></p>
                            </body>
                        </html>
                        """
                        sender.send_email(
                            to_email="nitishm.23it@kongu.edu",
                            subject="Silver Price Dropped!!",
                            body=html_content,
                            is_html=True
                        )
                        isSent_silver = True
                        print("Silver price mail sent successfully!")
                    
                    print(f"{current_time} | Gold: {gold_price} | Silver: {silver_price}")
                else:
                    price_data["status"] = "error"
                    print(f"{current_time} | ERROR: Could not fetch prices")
                
                time.sleep(REFRESH_INTERVAL)
                
            except Exception as e:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                price_data["status"] = "error"
                print(f"{current_time} | ERROR: {str(e)}")
                time.sleep(REFRESH_INTERVAL)
                
    except Exception as e:
        print(f"Fatal error in price monitor: {e}")
        price_data["status"] = "fatal_error"
    finally:
        if driver:
            driver.quit()


# HTML template for web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AuraGold Live Prices</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        h1 {
            color: #ffd700;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2rem;
        }
        .price-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .price-card.gold {
            border-left: 4px solid #ffd700;
        }
        .price-card.silver {
            border-left: 4px solid #c0c0c0;
        }
        .price-label {
            color: #888;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }
        .price-value {
            font-size: 1.8rem;
            font-weight: bold;
            transition: transform 0.3s ease;
        }
        .price-card.gold .price-value {
            color: #ffd700;
        }
        .price-card.silver .price-value {
            color: #c0c0c0;
        }
        .status {
            text-align: center;
            color: #666;
            font-size: 0.85rem;
            margin-top: 20px;
        }
        .status span {
            color: #4ade80;
        }
        .live-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #4ade80;
            border-radius: 50%;
            margin-right: 5px;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .refresh-info {
            text-align: center;
            color: #666;
            font-size: 0.8rem;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 AuraGold Live Prices</h1>
        
        <div class="price-card gold">
            <div class="price-label">Live Gold Price</div>
            <div class="price-value" id="gold-price">{{ gold_price }}</div>
        </div>
        
        <div class="price-card silver">
            <div class="price-label">Live Silver Price</div>
            <div class="price-value" id="silver-price">{{ silver_price }}</div>
        </div>
        
        <div class="status">
            <span class="live-indicator"></span>
            <span>Live</span> | Last updated: <span id="last-updated">{{ last_updated }}</span>
        </div>
        
        <div class="refresh-info">
            Auto-refreshes every 60 seconds
        </div>
    </div>
    
    <script>
        let lastUpdate = '{{ last_updated }}';
        
        // Fetch latest prices via API every 5 seconds
        setInterval(async function() {
            try {
                const response = await fetch('/api/prices');
                const data = await response.json();
                
                // Check if data has been updated
                if (data.last_updated && data.last_updated !== lastUpdate) {
                    // Update the prices with animation
                    const goldElement = document.getElementById('gold-price');
                    const silverElement = document.getElementById('silver-price');
                    
                    goldElement.style.transform = 'scale(1.1)';
                    silverElement.style.transform = 'scale(1.1)';
                    
                    setTimeout(() => {
                        goldElement.textContent = data.gold_price;
                        silverElement.textContent = data.silver_price;
                        document.getElementById('last-updated').textContent = data.last_updated || 'N/A';
                        
                        goldElement.style.transform = 'scale(1)';
                        silverElement.style.transform = 'scale(1)';
                    }, 150);
                    
                    lastUpdate = data.last_updated;
                }
            } catch (error) {
                console.error('Failed to fetch prices:', error);
            }
        }, 5000); // Poll every 5 seconds
    </script>
</body>
</html>
"""


@app.route('/')
def home():
    """Render the main page with current prices"""
    return render_template_string(
        HTML_TEMPLATE,
        gold_price=price_data["gold_price"],
        silver_price=price_data["silver_price"],
        last_updated=price_data["last_updated"] or "Loading..."
    )


@app.route('/api/prices')
def get_prices():
    """API endpoint to get current prices as JSON"""
    return jsonify(price_data)


@app.route('/health')
def health():
    """Health check endpoint for hosting platforms"""
    return jsonify({
        "status": "healthy",
        "scraper_status": price_data["status"],
        "timestamp": datetime.now().isoformat()
    })


def start_background_monitor():
    """Start the price monitor in a background thread"""
    monitor_thread = threading.Thread(target=price_monitor, daemon=True)
    monitor_thread.start()
    print("Background price monitor started!")


# Start the background monitor when the app starts
start_background_monitor()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

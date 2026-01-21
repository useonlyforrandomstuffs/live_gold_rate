# AuraGold Live Price Scraper

A Python web scraper that continuously monitors live gold and silver prices from [auragold.in](https://auragold.in). The application refreshes every 1 minute and logs the prices with timestamps.

## Features

- 🔄 Automatically scrapes live gold and silver prices every 60 seconds
- 🌐 Web interface to view current prices
- 📡 REST API endpoint for programmatic access
- 🐳 Docker support for easy deployment
- ☁️ Ready for deployment on Render/Vercel

## Files

| File | Description |
|------|-------------|
| `scraper.py` | Standalone console scraper - runs continuously and logs to console |
| `app.py` | Flask web application with web UI and API |
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Docker configuration for containerized deployment |
| `build.sh` | Build script for Render deployment |
| `render.yaml` | Render deployment configuration |

## Local Development

### Prerequisites

- Python 3.9+
- Google Chrome browser
- ChromeDriver (matching your Chrome version)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd auragold_webScarpping
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running Locally

#### Console Scraper (Logs to Console)
```bash
python scraper.py
```

Output:
```
============================================================
AuraGold Live Price Monitor
============================================================
Monitoring URL: https://auragold.in
Refresh Interval: 60 seconds
============================================================

Initializing browser...
Browser initialized successfully!

Starting price monitoring...
------------------------------------------------------------
2026-01-21 10:00:00 | Gold: ₹15621.84/gm | Silver: ₹323.35/gm
2026-01-21 10:01:00 | Gold: ₹15625.50/gm | Silver: ₹324.10/gm
...
```

#### Web Application
```bash
python app.py
```

Then open http://localhost:5000 in your browser.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface with live prices |
| `/api/prices` | GET | JSON response with current prices |
| `/health` | GET | Health check endpoint |

### Sample API Response

```json
{
  "gold_price": "₹15621.84/gm",
  "silver_price": "₹323.35/gm",
  "last_updated": "2026-01-21 10:00:00",
  "status": "success"
}
```

## Deployment

### Deploy to Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Use the following settings:
   - **Environment**: Docker
   - **Docker Command**: (leave default)
   - **Health Check Path**: `/health`

Or use the `render.yaml` blueprint for automatic configuration.

### Deploy with Docker

```bash
# Build the image
docker build -t auragold-scraper .

# Run the container
docker run -p 5000:5000 auragold-scraper
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `5000` |
| `CHROME_BIN` | Path to Chrome binary | Auto-detected |
| `CHROMEDRIVER_PATH` | Path to ChromeDriver | Auto-detected |

## How It Works

1. The scraper uses Selenium with a headless Chrome browser to load the AuraGold website
2. It waits for JavaScript to render the dynamic price content
3. It extracts prices from elements with class `live__price__container`:
   - **First container**: Gold price (span with class `price`)
   - **Second container**: Silver price (span with class `price`)
4. Prices are logged to console and stored for API access
5. The process repeats every 60 seconds

## Troubleshooting

### Chrome/ChromeDriver Issues

If you encounter issues with Chrome or ChromeDriver:

1. Make sure Chrome is installed
2. Install the matching ChromeDriver version:
```bash
pip install webdriver-manager
```

The scraper will automatically manage ChromeDriver installation.

### Timeout Errors

If you see timeout errors, the website might be slow to load. You can increase the timeout in the code:

```python
WebDriverWait(driver, 30).until(...)  # Increase from 15 to 30 seconds
```

## License

MIT License

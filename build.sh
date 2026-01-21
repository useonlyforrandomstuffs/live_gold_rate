#!/usr/bin/env bash
# Build script for Render deployment

# Install Chrome
apt-get update
apt-get install -y wget gnupg

# Add Chrome repository
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

# Install Chrome
apt-get update
apt-get install -y google-chrome-stable

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f 3 | cut -d '.' -f 1)
wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}.0.6778.87/linux64/chromedriver-linux64.zip"
unzip chromedriver-linux64.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Set environment variables
export CHROME_BIN=/usr/bin/google-chrome
export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Install Python dependencies
pip install -r requirements.txt

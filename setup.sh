#!/bin/bash

echo "Updating system..."
sudo apt update

echo "Installing Python and pip..."
sudo apt install python3 python3-pip -y

echo "Installing Python packages..."
pip3 install python-telegram-bot python-dotenv playwright

echo "Installing Playwright browsers..."
python3 -m playwright install
python3 -m playwright install chromium
python3 -m playwright install-deps

echo "Removing yarn.list if exists..."
sudo rm -f /etc/apt/sources.list.d/yarn.list

echo "Installing required system dependencies..."
sudo apt install -y \
libatk1.0-0t64 \
libatk-bridge2.0-0t64 \
libgtk-3-0t64 \
libxcomposite1 \
libxdamage1 \
libxrandr2 \
libgbm1 \
libasound2t64 \
libpangocairo-1.0-0 \
libpango-1.0-0 \
libnss3 \
libxss1 \
libxtst6 \
fonts-liberation \
libappindicator3-1 \
libdrm2 \
libxkbcommon0

echo "Force installing Chromium via Playwright..."
python3 -m playwright install --force chromium

echo "Setup Completed Successfully ✅"

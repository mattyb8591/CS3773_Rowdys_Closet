#!/bin/bash
set -e

APP_DIR="/var/www/CS3773_Rowdys_Closet"
cd "$APP_DIR"

# Activate venv
source venv/bin/activate

# Pull latest code from GitHub
git pull origin main
git reset --hard origin/main

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Restart Flask service
sudo systemctl restart rowdys_closet

# Log deployment
echo "Deploy complete at $(date)" >> "$APP_DIR/deploy.log"

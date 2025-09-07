#!/bin/bash
set -e

REPO_URL="https://raw.githubusercontent.com/Isaac-Cooper/PteroScan/main"
INSTALL_DIR="/etc/pteroscan"

echo "📥 Installing PteroScan..."

# Create install directory
sudo mkdir -p $INSTALL_DIR

echo "📥 Downloading PteroScan script..."
sudo curl -sL $REPO_URL/pteroscan.py -o $INSTALL_DIR/pteroscan.py
sudo chmod +x $INSTALL_DIR/pteroscan.py

echo "📥 Downloading systemd service..."
sudo curl -sL $REPO_URL/pteroscan.service -o /etc/systemd/system/pteroscan.service

echo ""
echo "⚙️ Configuring PteroScan..."
read -p "🌐 Enter API URL: " api_url
read -p "🔑 Enter API Key: " api_key
read -p "⏳ Enter scan interval in seconds (default 300): " scan_interval
read -p "📂 Enter base path for server volumes (default /var/lib/pterodactyl/volumes): " base_path

# Apply defaults if empty
scan_interval=${scan_interval:-300}
base_path=${base_path:-/var/lib/pterodactyl/volumes}

# Write config.yml
sudo tee $INSTALL_DIR/config.yml > /dev/null <<EOL
api_url: "$api_url"
api_key: "$api_key"
scan_interval_seconds: $scan_interval
base_path: "$base_path"
EOL

sudo chmod 600 $INSTALL_DIR/config.yml

echo "⚙️ Setting up Python environment..."
cd $INSTALL_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install pyyaml requests
deactivate

echo "🔄 Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable pteroscan.service
sudo systemctl restart pteroscan.service

echo ""
echo "✅ PteroScan installation complete!"
echo "Check logs with: sudo journalctl -u pteroscan -f"

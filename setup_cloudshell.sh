#!/bin/bash

echo "========================================="
echo "  AI Infra Provisioner - Cloud Shell Setup "
echo "========================================="

# 1. Ensure Python 3.13 / Virtual Environment
echo "[+] Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# 2. Install Requirements
echo "[+] Installing Dependencies..."
pip install -r requirements.txt

# 3. Create .env file interactively
echo "[+] Configuring Environment Variables..."
touch .env

echo ""
read -p "Enter your current Google Cloud Project ID (e.g., my-demo-project-123): " GCP_PROJECT
read -p "Enter your Gemini API Key (Required for planning/governance): " GEMINI_KEY

# Overwrite .env with new values
cat <<EOL > .env
GOOGLE_CLOUD_PROJECT="${GCP_PROJECT}"
GOOGLE_API_KEY="${GEMINI_KEY}"
GOOGLE_GENAI_USE_VERTEXAI="false"
GOOGLE_CLOUD_LOCATION="us-central1"
EOL

echo ""
echo "========================================="
echo " Setup Complete! "
echo "========================================="
echo "To run the provisioner UI, make sure to activate the virtual environment and start Streamlit:"
echo "source .venv/bin/activate"
echo "streamlit run app.py"

#!/bin/bash

# Use the virtual environment's python
PYTHON_CMD="./.venv/bin/python3"

# List of pending test cases
TEST_CASES=(
    "Cloud SQL|Create a Cloud SQL for payment-prod in us-central1 --tier=db-f1-micro"
    "Redis|Provision a Redis cache for session-prod in us-central1"
    "Cloud Run|Deploy a Cloud Run service for web-dev"
    "VPC|Create a VPC network for core-stag"
)

# Main loop to run each case
for case in "${TEST_CASES[@]}"; do
    IFS="|" read -r resource request <<< "$case"
    
    echo "=========================================================="
    echo "TESTING RESOURCE TYPE: $resource"
    echo "REQUEST: $request"
    echo "=========================================================="
    
    $PYTHON_CMD main.py --request "$request"
    
    echo "Waiting 5 seconds to avoid API rate limits..."
    sleep 5
    
    echo -e "\n\n"
done

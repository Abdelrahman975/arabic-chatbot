#!/bin/bash
# Start the chatbot web server

# Activate the conda environment
conda activate arabic-chatbot

# Run the application
python app.py

echo "Server running! Access the chatbot at http://127.0.0.1:8000"
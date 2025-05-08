#!/bin/bash
# Process PDF and create vector database

# Activate the conda environment
conda activate arabic-chatbot

# Run the ingestion script
python ingest.py

echo "Ingestion complete! Now run ./run.sh to start the chatbot server."
#!/bin/bash
# Create and set up conda environment

# Create the conda environment
conda create -n arabic-chatbot python=3.10 -y

# Activate the environment
conda activate arabic-chatbot

# Install requirements
pip install -r requirements.txt

# Create necessary directories
mkdir -p data templates

# Copy PDF file to data directory (assumes PDF is in current directory)
echo "Please copy your Arabic FAQ PDF file to the data directory as 'FAQ-Arabic.pdf'"

echo "Setup complete! Now run ./ingest.sh to process the PDF file."
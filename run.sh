#!/bin/bash

# Activate the virtual environment
python -m venv venv
source venv/scripts/activate

# Upgrade pip
python.exe -m pip install --upgrade pip

# Install the required packages
pip install -r requirements.txt

# Run the main script
python quarter_hour_data.py
python correlation.py

deactivate

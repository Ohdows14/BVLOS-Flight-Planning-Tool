#!/bin/bash

# BVLOS Flight Planning Tool - Setup Script

echo "=================================="
echo "BVLOS Flight Planning Tool Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version=3.9

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo "❌ Python $required_version or higher required. You have $python_version"
    exit 1
else
    echo "✓ Python $python_version detected"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=================================="
echo "✓ Setup complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Add your data files to data/ folders"
echo "2. Activate environment: source venv/bin/activate"
echo "3. Run the app: streamlit run app.py"
echo ""

#!/bin/bash

echo "Starting Viel-AI setup and launch..."
echo ""

# Check if we're in the viel-ai directory, if not try to navigate there
if [ ! -f "main.py" ]; then
    if [ -d "viel-ai" ]; then
        cd viel-ai
    else
        echo "Error: viel-ai directory not found."
        echo "Please run the setup_viel_ai.sh script first to clone the repository."
        read -p "Press any key to continue..." -n1 -s
        echo ""
        exit 1
    fi
fi

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed."
    echo "Please run the setup_viel_ai.sh script first to install Python."
    read -p "Press any key to continue..." -n1 -s
    echo ""
    exit 1
fi

# Check if uv is installed in the virtual environment, if not install it
if ! command -v uv &> /dev/null; then
    echo "UV package installer not found. Installing UV..."
    pip install uv
    echo "UV installed successfully."
    echo ""
else
    echo "UV is already installed."
    echo ""
fi

# Set up virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating new virtual environment..."
    uv venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated."
echo ""

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing project requirements using UV..."
    uv pip install -r requirements.txt
    echo "Requirements installed successfully."
    echo ""
else
    echo "Warning: requirements.txt not found."
    echo "Attempting to identify package requirements from imports..."
    
    # If no requirements file exists, try to install common packages that might be needed
    echo "Installing potential requirements..."
    uv pip install numpy pandas torch tensorflow matplotlib pillow requests
    echo ""
fi

# Run the main.py file
echo "Starting Viel-AI application..."
echo ""
echo "---------------------------------------------"
echo "Running main.py"
echo "---------------------------------------------"
echo ""

python main.py

# Deactivate virtual environment when done
deactivate
echo "Virtual environment deactivated."

echo ""
echo "Application execution completed."
read -p "Press any key to continue..." -n1 -s
echo ""

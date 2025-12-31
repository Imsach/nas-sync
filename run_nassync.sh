#!/bin/bash
# NAS Auto Sync Manager - Linux/Mac Launcher
# Make executable with: chmod +x run_nassync.sh

echo "Starting NAS Auto Sync Manager..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 to run this application"
    exit 1
fi

# Check if tkinter is available
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: tkinter is not installed"
    echo ""
    echo "Install it with:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  Fedora: sudo dnf install python3-tkinter"
    echo "  Arch: sudo pacman -S tk"
    exit 1
fi

# Run the application
python3 nas_sync_app.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Failed to start the application"
    read -p "Press Enter to exit..."
fi

# NAS Auto Sync Manager - Files Overview

## Main Application Files

### `nas_sync_app.py` ⭐ MAIN FILE
**The main GUI application**
- Creates the user interface using tkinter
- Handles user interactions (buttons, file browsing, etc.)
- Manages sync operations and auto-sync scheduling
- Displays logs and progress
- Saves and loads configuration

**To start the application**: `python nas_sync_app.py`

### `sync_engine.py`
**The core sync logic**
- Handles file copying, updating, and deletion
- Implements include/exclude pattern matching
- Verifies files using MD5 hashing
- Manages recursive directory traversal
- Provides detailed statistics and error handling

### `config_manager.py`
**Configuration persistence**
- Saves settings to `~/.nassync/config.json`
- Loads settings on application start
- Stores: paths, sync mode, patterns, intervals, etc.

## Launcher Scripts

### `run_nassync.bat` (Windows)
**Windows launcher script**
- Double-click to start the application
- Checks for Python installation
- Shows error messages if something goes wrong

### `run_nassync.sh` (Linux/Mac)
**Linux/Mac launcher script**
- Checks for Python 3 and tkinter
- Provides installation instructions if missing
- Run with: `./run_nassync.sh`

## Documentation

### `README_NAS_SYNC.md` 📚
**Complete documentation**
- Detailed feature list
- Installation instructions
- Configuration guide
- NAS mounting instructions for Windows/Linux
- Troubleshooting guide
- Advanced usage (running as service)

### `QUICK_START.md` 🚀
**Get started in 5 minutes**
- Simple step-by-step setup
- Common use case examples
- Quick troubleshooting tips
- Perfect for first-time users

### `FILES_OVERVIEW.md` (this file)
**Project structure guide**
- Lists all files and their purposes
- Helps you understand the project organization

### `requirements.txt`
**Python dependencies**
- Lists required Python packages
- Note: This app uses only standard library (no pip install needed!)
- Includes tkinter installation instructions for Linux

## Configuration File

### `~/.nassync/config.json`
**Auto-generated configuration file**
- Created when you click "Save Settings"
- Location:
  - Windows: `C:\Users\YourName\.nassync\config.json`
  - Linux/Mac: `/home/yourname/.nassync/config.json`
- Contains: source path, destination path, sync settings, patterns, etc.

Example content:
```json
{
    "source": "C:\\Users\\John\\Documents",
    "destination": "\\\\NAS\\Backups\\Documents",
    "interval": 30,
    "mode": "mirror",
    "include": "*.jpg,*.png,*.docx",
    "exclude": "*.tmp,~*",
    "verify": true,
    "subfolders": true
}
```

## How The Files Work Together

```
nas_sync_app.py (Main GUI)
    ↓
    ├─→ config_manager.py (Load/Save settings)
    │       ↓
    │       └─→ ~/.nassync/config.json
    │
    └─→ sync_engine.py (Perform sync)
            ↓
            ├─→ Read files from Source folder
            ├─→ Compare with Destination folder
            ├─→ Copy/Update/Delete files
            └─→ Report progress back to GUI
```

## File Sizes

All files are small and efficient:
- `nas_sync_app.py`: ~15 KB (main GUI)
- `sync_engine.py`: ~9 KB (sync logic)
- `config_manager.py`: ~1 KB (config handling)
- `run_nassync.bat`: <1 KB (Windows launcher)
- `run_nassync.sh`: ~1 KB (Linux/Mac launcher)

**Total application size**: ~26 KB + documentation

## Where to Start

1. **First time users**: Read `QUICK_START.md`
2. **Need details**: Read `README_NAS_SYNC.md`
3. **Run the app**:
   - Windows: Double-click `run_nassync.bat`
   - Linux/Mac: Run `./run_nassync.sh`
   - Any OS: Run `python nas_sync_app.py`

## No Installation Required!

This application uses only Python standard library modules. Just:
1. Have Python 3.7+ installed
2. Have tkinter installed (usually included with Python)
3. Run `nas_sync_app.py`

That's it! No `pip install`, no dependencies, no setup.py, no virtual environments needed!

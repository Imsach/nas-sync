# Windows-Specific Features

Buffalo LinkStation Sync Manager includes powerful Windows-optimized features for seamless background operation.

## System Tray Icon

### Overview

The application integrates with the Windows system tray, allowing it to run quietly in the background while keeping you informed about sync status.

### Features

- **Status Indicators** - Color-coded icon shows current status:
  - Blue: Idle/Ready
  - Orange: Syncing in progress
  - Green: Last sync successful
  - Red: Last sync failed

- **Real-Time Progress** - Tooltip shows current sync progress percentage

- **Quick Actions** - Right-click menu provides:
  - Show Window (double-click icon)
  - Sync Now
  - Toggle Auto-Sync
  - View History
  - Open Logs
  - Exit

- **Notifications** - Native Windows notifications for:
  - Sync completion
  - Sync failures
  - Application status

- **Minimize to Tray** - Closing the window minimizes to tray instead of exiting

### Installation

Install the tray icon dependencies:

```bash
pip install pystray pillow
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### Usage

The system tray icon starts automatically when you launch the application. If the dependencies are not installed, the application will still work but without the tray icon.

**Quick Tips:**
- Double-click tray icon to show/hide window
- Right-click for quick menu
- Hover over icon to see sync progress
- Application continues syncing when minimized to tray

## Sync History Tracking

### Overview

Comprehensive history tracking system records every sync operation with detailed statistics.

### Features

- **Persistent Storage** - All sync history stored in `~/.nassync/history.json`
- **Detailed Records** - Each entry includes:
  - Timestamp
  - Source and destination paths
  - Success/failure status
  - Files copied, updated, deleted
  - Error count
  - Sync duration

- **Statistics Dashboard** - Overall metrics including:
  - Total syncs performed
  - Successful vs failed syncs
  - Success rate percentage
  - Last sync time

- **History Viewer** - Sortable table showing:
  - Date and time
  - Status (Success/Failed)
  - File operations
  - Duration

- **Export Capability** - Export history to text file for reporting

### Accessing History

1. Click the "History" tab in the application
2. View overall statistics at the top
3. Browse detailed sync records in the table below
4. Click "Refresh" to update the display
5. Click "Export History" to save to file
6. Click "Clear History" to remove all records

### History Storage

History is stored in:
- **Windows**: `C:\Users\YourName\.nassync\history.json`
- **Linux/Mac**: `/home/yourname/.nassync/history.json`

The system keeps the last 1000 sync operations automatically.

## Current Progress Tracking

### In Application

- **Dashboard Stats** - Real-time statistics cards showing:
  - Last sync time
  - Next scheduled sync
  - Total files synced
  - Current status

- **Progress Bar** - Visual progress indicator with percentage
- **Status Text** - Descriptive status messages
- **Live Logs** - Real-time activity feed on dashboard

### In System Tray

- **Icon Color** - Instant visual status
- **Tooltip Progress** - Shows percentage while syncing
- **Completion Notifications** - Pop-up alerts when syncs finish

### Sync Duration Tracking

Every sync records its duration:
- Visible in history table
- Used for performance monitoring
- Helps identify slow syncs

## Windows-Optimized Features

### Buffalo LinkStation Auto-Detection

- **Network Drive Detection** - Automatically finds mapped network drives
- **Quick Setup** - One-click application of detected drives
- **Connection Testing** - Built-in connectivity verification

### Mapped Drive Support

Full support for Windows mapped drives:
- Letter-based drives (Z:\, Y:\, etc.)
- UNC paths (\\NAS\share)
- Network locations

### Background Operation

- **Minimize to Tray** - Runs quietly in background
- **No Window Required** - Syncing continues when minimized
- **Auto-Start Ready** - Compatible with Windows startup

### Task Scheduler Integration

Run at Windows startup:

1. Open Task Scheduler
2. Create Basic Task → "Buffalo LinkStation Sync"
3. Trigger: "At log on"
4. Action: Start a program
   - Program: `pythonw.exe` (no console window)
   - Arguments: `"C:\path\to\nas_sync_app.py"`
5. Check "Run whether user is logged on or not"
6. Save

The application will:
- Start minimized to tray
- Resume auto-sync if it was enabled
- Show notification when ready

### Performance Optimizations

- **Bandwidth Throttling** - Prevents network congestion
- **Smart File Detection** - Only syncs changed files
- **Efficient Hashing** - Fast MD5 verification
- **Chunk-Based Copying** - Optimal for large files

## Installation Guide (Windows)

### Step 1: Install Python

Download Python 3.7+ from python.org

During installation:
- ✅ Check "Add Python to PATH"
- ✅ Check "Install pip"

### Step 2: Install Dependencies

Open Command Prompt and run:

```bash
cd path\to\buffalo-sync
pip install -r requirements.txt
```

### Step 3: Run the Application

Double-click `run_nassync.bat` or run:

```bash
python nas_sync_app.py
```

### Step 4: Configure

1. Application opens with system tray icon
2. Configure your Buffalo LinkStation connection
3. Set sync paths and options
4. Click "Save Configuration"
5. Start syncing!

## Troubleshooting

### Tray Icon Not Appearing

**Cause**: Missing dependencies

**Solution**:
```bash
pip install pystray pillow
```

Then restart the application.

### Application Doesn't Minimize to Tray

**Check**:
1. Tray icon dependencies installed?
2. Look for tray icon near clock
3. Check application logs for errors

### History Not Saving

**Check**:
1. Permissions on `C:\Users\YourName\.nassync\`
2. Disk space available
3. View logs for error messages

### Notifications Not Showing

**Windows 10/11**:
1. Open Settings → System → Notifications
2. Find "Python" or "pythonw"
3. Enable notifications

### Performance Issues

**For large syncs**:
- Enable bandwidth limiting
- Disable file verification temporarily
- Check Buffalo LinkStation performance
- Use wired connection, not WiFi

## Advanced Configuration

### Running as Windows Service

Use NSSM (Non-Sucking Service Manager):

1. Download NSSM from nssm.cc
2. Run: `nssm install BuffaloSync`
3. Set path to `pythonw.exe`
4. Set arguments: `"C:\path\to\nas_sync_app.py"`
5. Configure startup type
6. Start service

### Silent Mode

For completely silent operation:

1. Use `pythonw.exe` instead of `python.exe`
2. Enable minimize to tray
3. Disable email notifications if not needed
4. Tray icon only shows when hover/click

### Multiple Configurations

Run multiple instances:

1. Copy application to different folders
2. Each has its own `.nassync` config folder
3. Different source → destination mappings
4. Can run simultaneously

## Best Practices for Windows

1. **Map Network Drive** - Use drive letter for Buffalo LinkStation
2. **Enable Tray Icon** - Install pystray and pillow
3. **Auto-Start** - Use Task Scheduler for automatic startup
4. **Exclude from Antivirus** - Add application folder to exclusions
5. **Regular Monitoring** - Check history tab weekly
6. **Test Restores** - Verify backups can be restored
7. **Network Optimization** - Use Gigabit Ethernet when possible

## Keyboard Shortcuts

While application is focused:

- `Ctrl+S` - Sync Now (if implemented)
- `Ctrl+H` - View History Tab
- `Ctrl+L` - View Logs Tab
- `Alt+F4` - Minimize to Tray
- `Esc` - Minimize to Tray

## System Requirements

### Minimum
- Windows 7 or later
- Python 3.7+
- 512 MB RAM
- Network connection to Buffalo LinkStation

### Recommended
- Windows 10/11
- Python 3.9+
- 1 GB RAM
- Gigabit Ethernet
- Buffalo LinkStation LS200 with latest firmware

### For Tray Icon
- pystray 0.19.0+
- Pillow 10.0.0+
- Windows notification support

## FAQ

**Q: Can I run this on Windows 7?**
A: Yes, but some features like modern notifications may not work.

**Q: Does it work with Windows Server?**
A: Yes, fully compatible with Windows Server 2012+.

**Q: Can I sync to OneDrive/Dropbox?**
A: Yes, any accessible folder works (local or cloud).

**Q: Will it slow down my PC?**
A: No, uses minimal resources. Enable bandwidth limiting if needed.

**Q: Can I schedule syncs for specific times?**
A: Yes, use the "Scheduled Sync Times" feature in Advanced tab.

**Q: How do I backup the configuration?**
A: Copy `C:\Users\YourName\.nassync\` folder.

**Q: Can multiple users use it on one PC?**
A: Yes, each Windows user has separate configuration.

**Q: Is it safe for Buffalo LS200 Series?**
A: Yes, specifically optimized for Buffalo LinkStation LS200.

---

**Enjoy hassle-free Windows backups to your Buffalo LinkStation!**

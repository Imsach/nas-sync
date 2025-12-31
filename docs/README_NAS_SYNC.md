# NAS Auto Sync Manager

A comprehensive Python application with GUI for automatically syncing folders from your PC to your NAS (Network Attached Storage).

## Features

✅ **User-Friendly GUI** - Built with Tkinter for easy configuration
✅ **Automatic Syncing** - Set intervals for automatic background synchronization
✅ **Manual Sync** - Trigger syncs on demand with a single click
✅ **Two Sync Modes**:
   - **Mirror Mode** - Keeps destination identical to source (deletes extra files)
   - **Copy Mode** - Only copies/updates files (preserves extra files in destination)
✅ **File Filtering** - Include/exclude files using patterns (*.jpg, *.doc, etc.)
✅ **File Verification** - Optional MD5 hash verification after copying
✅ **Subfolder Support** - Recursively sync entire directory trees
✅ **Progress Tracking** - Real-time progress bar and detailed logging
✅ **Persistent Settings** - Configuration automatically saved and restored
✅ **Error Handling** - Robust error handling with detailed logs
✅ **Safe Operations** - Stops gracefully and handles permission errors

## Requirements

- Python 3.7 or higher
- tkinter (usually comes with Python)

### Installing tkinter (if needed)

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install python3-tk
```

**Linux (Fedora)**:
```bash
sudo dnf install python3-tkinter
```

**Linux (Arch)**:
```bash
sudo pacman -S tk
```

**Windows/macOS**: tkinter is included with Python

## Installation

1. Download all three Python files to the same folder:
   - `nas_sync_app.py` (main application)
   - `sync_engine.py` (sync logic)
   - `config_manager.py` (settings management)

2. No additional packages required - uses only Python standard library!

## Usage

### Starting the Application

```bash
python nas_sync_app.py
```

Or double-click `nas_sync_app.py` if your system is configured to run Python files.

### Configuration

1. **Source Folder**: Click "Browse" to select the folder on your PC you want to backup
2. **Destination Folder**: Click "Browse" to select the destination folder on your NAS
   - This can be a network drive (e.g., `\\NAS\backups` on Windows or `/mnt/nas/backups` on Linux)
   - Make sure the NAS is mounted/accessible before syncing

3. **Sync Options**:
   - **Auto-Sync Interval**: How often to automatically sync (in minutes)
   - **Sync Mode**: Choose between Mirror or Copy mode
   - **Include Patterns**: File patterns to include (e.g., `*.jpg,*.png,*.docx`)
   - **Exclude Patterns**: File patterns to exclude (e.g., `*.tmp,~*,.git`)
   - **Verify files**: Enable to verify files using MD5 hash (slower but safer)
   - **Include subfolders**: Enable to sync subdirectories recursively

4. Click "Save Settings" to persist your configuration

### Syncing

**Manual Sync**:
- Click "Sync Now" to start an immediate sync operation

**Automatic Sync**:
- Click "Start Auto-Sync" to begin automatic syncing at the configured interval
- Click "Stop Auto-Sync" to disable automatic syncing

**Stop Sync**:
- Click "Stop" to gracefully stop an in-progress sync operation

### File Patterns

**Include patterns** (comma-separated):
- `*` - All files (default)
- `*.jpg,*.png` - Only image files
- `*.doc*` - All Word documents (doc, docx)
- `report_*` - Files starting with "report_"

**Exclude patterns** (comma-separated):
- `*.tmp` - Exclude temporary files
- `~*` - Exclude backup files
- `.git,.svn` - Exclude version control folders
- `*.log,*.cache` - Exclude log and cache files

### Mounting NAS on Windows

To mount your NAS as a network drive:
1. Open File Explorer
2. Click "This PC" → "Map network drive"
3. Choose a drive letter and enter your NAS path (e.g., `\\192.168.1.100\share`)
4. Check "Reconnect at sign-in" for automatic mounting
5. Use the mapped drive letter in the application (e.g., `Z:\backups`)

### Mounting NAS on Linux

To mount your NAS:

**Using CIFS/SMB (Windows shares)**:
```bash
sudo mkdir -p /mnt/nas
sudo mount -t cifs //192.168.1.100/share /mnt/nas -o username=youruser,password=yourpass
```

**Using NFS**:
```bash
sudo mkdir -p /mnt/nas
sudo mount -t nfs 192.168.1.100:/share /mnt/nas
```

**Permanent mount** (add to `/etc/fstab`):
```
//192.168.1.100/share /mnt/nas cifs username=youruser,password=yourpass 0 0
```

Then use `/mnt/nas` as your destination path.

## Sync Modes Explained

### Mirror Mode
- Keeps the destination **identical** to the source
- Copies new files, updates modified files
- **Deletes files** from destination that don't exist in source
- Perfect for exact backups where you want destination to match source exactly

### Copy Mode
- Only **copies and updates** files
- Never deletes files from destination
- Useful when multiple sources sync to same destination
- Good for incremental backups where you want to keep historical files

## Logs and Configuration

- **Logs**: Displayed in the application window in real-time
- **Configuration**: Stored in `~/.nassync/config.json` (user home directory)
  - Windows: `C:\Users\YourName\.nassync\config.json`
  - Linux/Mac: `/home/yourname/.nassync/config.json`

## Troubleshooting

### "Permission denied" errors
- Ensure you have read access to source folder
- Ensure you have write access to destination folder
- On Linux, check folder permissions: `ls -la`
- For NAS, verify your user has proper permissions

### NAS not accessible
- Verify NAS is powered on and connected to network
- Check if you can access NAS through file browser
- Verify mount point (Linux) or mapped drive (Windows)
- Test network connectivity: `ping <nas-ip-address>`

### Files not syncing
- Check include/exclude patterns - they may be filtering out your files
- Verify "Include subfolders" is enabled if files are in subdirectories
- Check logs for specific error messages

### Sync is slow
- Disable "Verify files" option for faster sync (trades speed for safety)
- Use include patterns to sync only necessary files
- Check network speed to NAS
- Large files take time - be patient

## Running as a Background Service

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., "At startup" or "At log on")
4. Action: Start a program
5. Program: `pythonw.exe` (note the 'w' - no console window)
6. Arguments: `"C:\path\to\nas_sync_app.py"`

### Linux (systemd)
Create `/etc/systemd/system/nassync.service`:
```ini
[Unit]
Description=NAS Auto Sync
After=network.target

[Service]
Type=simple
User=youruser
ExecStart=/usr/bin/python3 /path/to/nas_sync_app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable nassync
sudo systemctl start nassync
```

## Safety Notes

⚠️ **Important**:
- Always test with non-critical data first
- In Mirror mode, files deleted from source will be deleted from destination
- Keep backups of important data
- Verify your include/exclude patterns before syncing
- Start with manual syncs before enabling auto-sync

## License

This software is provided as-is for personal and commercial use.

## Support

For issues or questions:
1. Check the logs in the application window
2. Verify your configuration and patterns
3. Test with a small folder first
4. Ensure NAS is accessible from your PC

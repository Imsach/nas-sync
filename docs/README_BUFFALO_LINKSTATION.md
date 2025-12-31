# Buffalo LinkStation Sync Manager

Professional-grade automated backup solution specifically optimized for Buffalo LinkStation NAS devices. Features an elegant modern interface with enterprise-level capabilities.

## Features

### Core Functionality
- **Automatic & Manual Sync** - Schedule automatic syncing or trigger on-demand
- **Two Sync Modes**:
  - **Mirror Mode** - Keeps destination identical to source (exact backup)
  - **Copy Mode** - Only copies/updates files (preserves extra files)
- **Smart File Detection** - Only syncs changed files to save time and bandwidth
- **MD5 Verification** - Optional cryptographic verification after copying
- **Recursive Syncing** - Handles entire directory trees with subfolders

### Buffalo LinkStation Integration
- **Auto-Detection** - Automatically detects mapped Buffalo LinkStation drives
- **Quick Setup** - One-click preset for Buffalo LinkStation configuration
- **Connection Testing** - Test NAS connectivity before syncing
- **Real-Time Status** - Visual indicator showing Buffalo LinkStation connection status
- **Optimized Performance** - Tuned for Buffalo LinkStation network performance

### Advanced Features
- **Bandwidth Control** - Limit transfer speed to prevent network congestion (1-1000 MB/s)
- **Retention Policy** - Automatically delete old backups (1-365 days)
- **Email Notifications** - Get notified when syncs complete or fail
- **Scheduled Sync Times** - Run syncs only at specific times (e.g., 9 AM, 6 PM)
- **File Filtering** - Include/exclude files using patterns (*.jpg, *.tmp, etc.)
- **Export Logs** - Save detailed sync logs for troubleshooting

### Modern Interface
- **Dashboard View** - Quick stats showing last sync, next sync, files synced, and status
- **Tabbed Interface** - Organized into Dashboard, Configuration, Advanced, and Logs tabs
- **Real-Time Progress** - Live progress bar with percentage completion
- **Color-Coded Logs** - Easy-to-read logs with color-coded message levels
- **Stat Cards** - At-a-glance view of sync statistics
- **Professional Design** - Clean, modern UI with proper spacing and typography

## Requirements

- Python 3.7 or higher
- tkinter (usually comes with Python)
- Buffalo LinkStation LS200 or compatible NAS device
- Network connection to your NAS

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

## Quick Start

### 1. Set Up Your Buffalo LinkStation

**Windows - Map Network Drive**:
1. Open File Explorer
2. Right-click "This PC" → "Map network drive"
3. Choose drive letter (e.g., Z:)
4. Enter Buffalo LinkStation path: `\\LINKSTATION\share`
5. Check "Reconnect at sign-in"
6. Click "Finish"

**Linux - Mount Buffalo LinkStation**:
```bash
sudo mkdir -p /mnt/linkstation
sudo mount -t cifs //LINKSTATION-IP/share /mnt/linkstation -o username=youruser
```

**Permanent mount** (add to `/etc/fstab`):
```
//LINKSTATION-IP/share /mnt/linkstation cifs username=youruser,password=yourpass 0 0
```

### 2. Start the Application

```bash
python3 nas_sync_app.py
```

Or use the launcher:
- Windows: Double-click `run_nassync.bat`
- Linux/Mac: `./run_nassync.sh`

### 3. Configure Buffalo LinkStation Sync

**Dashboard Tab**:
- View sync statistics and status
- Use "Sync Now" for immediate sync
- Use "Start Auto-Sync" for scheduled syncing
- Test your Buffalo LinkStation connection

**Configuration Tab**:
1. **Quick Setup**: Select your Buffalo LinkStation from the dropdown and click "Apply"
2. **Source Folder**: Browse to the folder you want to backup
3. **Sync Options**: Set interval and mode (Mirror recommended for backups)
4. **File Filters**:
   - Include: `*` (all files) or specific patterns like `*.jpg,*.docx`
   - Exclude: `*.tmp,~*,.DS_Store,Thumbs.db` (recommended defaults)
5. Click "Save Configuration"

**Advanced Tab**:
- **Bandwidth Control**: Enable if you need to limit network usage
- **Retention Policy**: Enable to automatically clean up old backups
- **Email Notifications**: Configure SMTP to get email alerts
- **Scheduled Times**: Set specific sync times (e.g., 09:00, 18:00)

### 4. Start Syncing

Click "Sync Now" for an immediate sync, or "Start Auto-Sync" to enable automatic syncing at your configured interval.

## Configuration Examples

### Daily Document Backup to Buffalo LinkStation
```
Source: C:\Users\YourName\Documents
Destination: Z:\Backups\Documents (Buffalo LinkStation)
Mode: Mirror
Interval: 60 minutes
Include: *
Exclude: *.tmp,~*,.DS_Store,Thumbs.db
Verify: Enabled
Retention: 30 days
```

### Photo Archive to Buffalo LinkStation
```
Source: C:\Users\YourName\Pictures
Destination: Z:\Photos (Buffalo LinkStation)
Mode: Copy Only
Interval: 120 minutes
Include: *.jpg,*.png,*.raw,*.nef,*.cr2
Exclude: .thumbnails,cache
Verify: Enabled
Bandwidth Limit: 20 MB/s
```

### Project Backup (excluding build files)
```
Source: C:\Projects\MyApp
Destination: Z:\ProjectBackups\MyApp (Buffalo LinkStation)
Mode: Mirror
Scheduled Times: 09:00,13:00,18:00
Include: *
Exclude: node_modules,dist,build,*.log,.git,__pycache__
Verify: Enabled
Email Notifications: Enabled
```

## Advanced Features Guide

### Bandwidth Control

Prevents sync operations from consuming all available network bandwidth. Useful when:
- Syncing large files during work hours
- Using Buffalo LinkStation over WiFi
- Sharing network with other users/devices

Set limit based on your network speed:
- Home WiFi: 5-10 MB/s
- Gigabit LAN: 50-100 MB/s
- Fast NAS connection: 100+ MB/s

### Retention Policy

Automatically deletes backups older than specified days. Perfect for:
- Managing Buffalo LinkStation storage space
- Compliance requirements (keep data for X days)
- Preventing storage from filling up

Example: Set to 30 days to keep last month's backups only.

### Email Notifications

Get alerts when syncs complete or fail. Useful for:
- Monitoring unattended backup operations
- Catching sync failures immediately
- Tracking Buffalo LinkStation backup status remotely

Supports any SMTP server:
- Gmail: `smtp.gmail.com:587` (use app-specific password)
- Outlook: `smtp-mail.outlook.com:587`
- Office 365: `smtp.office365.com:587`

### Scheduled Sync Times

Instead of interval-based syncing, run at specific times:
- `09:00,18:00` - Morning and evening syncs
- `00:00,06:00,12:00,18:00` - Four times daily
- `22:00` - Late night when Buffalo LinkStation is idle

Uses 24-hour format, comma-separated.

## File Patterns Guide

### Include Patterns

Examples:
- `*` - All files (default)
- `*.jpg,*.png,*.gif` - Only images
- `*.doc*` - Word documents (doc, docx)
- `2024_*` - Files starting with "2024_"
- `*.pdf,*.xlsx` - PDFs and Excel files

### Exclude Patterns

Common exclusions:
- `*.tmp,*.cache` - Temporary files
- `~*,*.bak` - Backup files
- `.git,.svn` - Version control
- `node_modules,__pycache__` - Dependencies
- `.DS_Store,Thumbs.db,desktop.ini` - System files
- `*.log` - Log files

## Buffalo LinkStation Tips

### Optimal Settings for LS200

1. **Enable Jumbo Frames**: On LS200, enable jumbo frames for better performance
2. **Use Wired Connection**: Ethernet is much faster than WiFi for backups
3. **RAID Configuration**: Use RAID 1 for data protection
4. **Regular Maintenance**: Keep LS200 firmware updated
5. **NAS Power Schedule**: Configure LS200 to stay on during sync times

### Troubleshooting Buffalo LinkStation Issues

**Connection Test Fails**:
1. Ping Buffalo LinkStation: `ping LINKSTATION-IP`
2. Check if drive is mapped (Windows) or mounted (Linux)
3. Verify network cable connection
4. Try accessing Buffalo LinkStation through web interface
5. Check firewall settings

**Slow Transfer Speeds**:
1. Use wired connection instead of WiFi
2. Enable bandwidth limiting to steady the transfer rate
3. Disable file verification for faster syncs
4. Check Buffalo LinkStation disk health
5. Verify no other heavy network activity

**Permission Errors**:
1. Check Buffalo LinkStation share permissions
2. Verify username/password for network share
3. On Linux, mount with proper user credentials
4. Ensure write permissions on Buffalo LinkStation folder

**Drive Not Detected**:
- Windows: Re-map network drive
- Linux: Check mount status with `mount | grep linkstation`
- Verify Buffalo LinkStation is powered on
- Check network connectivity

## Logs and Configuration

- **Configuration**: Stored in `~/.nassync/config.json`
  - Windows: `C:\Users\YourName\.nassync\config.json`
  - Linux/Mac: `/home/yourname/.nassync/config.json`
- **Logs**: Displayed in application, exportable to text file
- **Dashboard**: Real-time statistics and recent activity

## Running as Background Service

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task → "Buffalo LinkStation Sync"
3. Trigger: At startup or At log on
4. Action: Start a program
5. Program: `pythonw.exe` (hidden window)
6. Arguments: `"C:\path\to\nas_sync_app.py"`
7. Save and enable

### Linux (systemd)

Create `/etc/systemd/system/buffalo-sync.service`:
```ini
[Unit]
Description=Buffalo LinkStation Sync Manager
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=youruser
ExecStart=/usr/bin/python3 /path/to/nas_sync_app.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable buffalo-sync
sudo systemctl start buffalo-sync
sudo systemctl status buffalo-sync
```

## Safety & Best Practices

### Before First Sync

1. Test with a small folder first
2. Use "Test NAS Connection" button
3. Review include/exclude patterns
4. Verify Buffalo LinkStation has enough space
5. Run one manual sync before enabling auto-sync

### Regular Maintenance

1. Check logs weekly for errors
2. Verify Buffalo LinkStation connection monthly
3. Test email notifications (if enabled)
4. Review retention policy effectiveness
5. Monitor Buffalo LinkStation disk space

### Data Safety

- **Mirror Mode Warning**: Files deleted from source will be deleted from Buffalo LinkStation
- **Test Restores**: Periodically verify backups can be restored
- **Multiple Backups**: Consider 3-2-1 rule (3 copies, 2 media types, 1 offsite)
- **Verify Enabled**: Always enable verification for important data
- **Monitor Logs**: Check for sync errors regularly

## Performance Optimization

### For Large Files (Videos, ISOs)
- Disable file verification (faster)
- Enable bandwidth limiting (steadier)
- Use Copy mode instead of Mirror
- Sync during off-hours

### For Many Small Files (Documents, Photos)
- Keep verification enabled
- No bandwidth limit needed
- Use Mirror mode
- Consider shorter sync intervals

### For Buffalo LinkStation LS200 Specifically
- Optimal chunk size: 1 MB (default)
- Recommended bandwidth limit: 20-50 MB/s
- Best sync times: Early morning or late night
- Use wired Gigabit Ethernet connection

## Troubleshooting

### General Issues

**Application won't start**:
```bash
python3 test_environment.py
```
This will check for missing dependencies.

**Sync hangs or freezes**:
1. Click "Stop" button
2. Check Buffalo LinkStation is responsive
3. Review logs for specific error
4. Test with smaller folder first

**High CPU/Memory usage**:
- Enable bandwidth limiting
- Increase sync interval
- Reduce number of files to sync
- Check for file verification overhead

### Buffalo LinkStation Specific

**LS200 goes to sleep during sync**:
- Disable sleep mode in LS200 settings
- Access web UI: `http://LINKSTATION-IP`
- System → Power Settings → Disable sleep

**Transfer speeds slower than expected**:
- Check network cable (use Cat6 or better)
- Verify Gigabit connection (not 100 Mbps)
- Disable other network activity
- Check Buffalo LinkStation disk performance

## System Requirements

### Minimum
- Python 3.7+
- 512 MB RAM
- Network connection to Buffalo LinkStation
- 50 MB free disk space

### Recommended
- Python 3.9+
- 1 GB RAM
- Gigabit Ethernet to Buffalo LinkStation
- 100 MB free disk space
- Buffalo LinkStation LS200 with latest firmware

## Support

### Getting Help

1. Check logs in the application
2. Export logs for detailed analysis
3. Test Buffalo LinkStation connection
4. Review this documentation
5. Run `test_environment.py` to check system

### Common Error Messages

- **"Permission denied"**: Check folder/NAS permissions
- **"Path not accessible"**: Verify Buffalo LinkStation is online
- **"Connection test failed"**: Check network connectivity
- **"Sync completed with errors"**: Review logs for specific files

## License

This software is provided as-is for personal and commercial use.

## Changelog

### Version 2.0 - Buffalo LinkStation Edition
- Added Buffalo LinkStation auto-detection
- New modern tabbed interface
- Dashboard with real-time statistics
- Bandwidth control feature
- Retention policy system
- Email notifications
- Scheduled sync times
- Connection testing
- Export logs functionality
- Enhanced error handling
- Professional color-coded interface

### Version 1.0 - Initial Release
- Basic sync functionality
- Mirror and Copy modes
- File filtering
- MD5 verification
- Auto-sync capability

---

**Enjoy hassle-free backups to your Buffalo LinkStation!**

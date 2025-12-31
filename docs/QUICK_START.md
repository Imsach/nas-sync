# Quick Start Guide - NAS Auto Sync Manager

## 5-Minute Setup

### Step 1: Run the Application

**Windows**:
- Double-click `run_nassync.bat`

**Linux/Mac**:
```bash
chmod +x run_nassync.sh
./run_nassync.sh
```

Or directly:
```bash
python3 nas_sync_app.py
```

### Step 2: Configure Paths

1. Click **Browse** next to "Source Folder" → Select the folder you want to backup
2. Click **Browse** next to "Destination" → Select your NAS folder

**Windows NAS Path Examples**:
- Mapped drive: `Z:\Backups\MyFolder`
- UNC path: `\\192.168.1.100\Backups\MyFolder`

**Linux/Mac NAS Path Examples**:
- Mounted NAS: `/mnt/nas/Backups/MyFolder`
- Network path: `/media/user/NAS/Backups/MyFolder`

### Step 3: Choose Sync Mode

**Mirror Mode** (Recommended for backups):
- Keeps destination identical to source
- Deletes files from NAS that aren't in source
- Perfect for creating exact copies

**Copy Mode** (Recommended for archiving):
- Only copies new/updated files
- Never deletes anything from NAS
- Good for accumulating files from multiple sources

### Step 4: Set Auto-Sync Interval

- Default: 30 minutes
- Adjust based on your needs (e.g., 60 for hourly, 1440 for daily)

### Step 5: Start Syncing

**For immediate sync**:
- Click **Sync Now**

**For automatic syncing**:
- Click **Start Auto-Sync**
- Application will sync every X minutes automatically

### Step 6: Save Your Settings

- Click **Save Settings** to remember your configuration
- Settings are restored automatically when you restart the app

## Common Use Cases

### Daily Document Backup
```
Source: C:\Users\YourName\Documents
Destination: \\NAS\Backups\Documents
Mode: Mirror
Interval: 60 minutes
Include: *
Exclude: *.tmp,~*
```

### Photo Archive
```
Source: C:\Users\YourName\Pictures
Destination: Z:\PhotoArchive
Mode: Copy
Interval: 30 minutes
Include: *.jpg,*.png,*.raw,*.nef
Exclude: .thumbnails,cache
```

### Project Backup
```
Source: C:\Projects\MyApp
Destination: \\NAS\ProjectBackups\MyApp
Mode: Mirror
Interval: 15 minutes
Include: *
Exclude: node_modules,*.log,.git,dist,build
```

### Music Library Sync
```
Source: C:\Music
Destination: /mnt/nas/Music
Mode: Mirror
Interval: 120 minutes
Include: *.mp3,*.flac,*.m4a
Exclude: *.tmp,.DS_Store
```

## Tips

✅ **Test First**: Start with a small test folder before syncing important data
✅ **Check Logs**: Watch the log window to see what's happening
✅ **Network Drive**: Make sure your NAS is mounted before starting
✅ **Mirror Mode Warning**: Files deleted from source will be deleted from destination!
✅ **Patterns**: Use `*` to include all files, or specify extensions like `*.jpg,*.pdf`

## Troubleshooting

**Can't see my NAS?**
- Windows: Map network drive first (File Explorer → Map Network Drive)
- Linux: Mount NAS first (`sudo mount -t cifs //nas-ip/share /mnt/nas`)

**Permission errors?**
- Ensure you have read access to source folder
- Ensure you have write access to destination folder
- Check NAS user permissions

**Nothing syncing?**
- Check include/exclude patterns
- Enable "Include subfolders" if files are in subdirectories
- Look at the log window for error messages

**Need help?**
- See full documentation in `README_NAS_SYNC.md`

import os
import shutil
import hashlib
from pathlib import Path
from fnmatch import fnmatch
import time
from datetime import datetime, timedelta

class SyncEngine:
    def __init__(self, config, log_callback, progress_callback):
        self.config = config
        self.log = log_callback
        self.update_progress = progress_callback
        self.should_stop = False

        self.source = Path(config['source'])
        self.destination = Path(config['destination'])
        self.mode = config['mode']
        self.verify = config['verify']
        self.subfolders = config['subfolders']

        # Bandwidth limiting
        self.bandwidth_limit = config.get('bandwidth_limit', False)
        self.bandwidth_value = config.get('bandwidth_value', None)
        self.bytes_transferred = 0
        self.transfer_start_time = None

        # Retention policy
        self.retention_enabled = config.get('retention_enabled', False)
        self.retention_days = config.get('retention_days', 30)

        # Parse include/exclude patterns
        self.include_patterns = [p.strip() for p in config['include'].split(',') if p.strip()]
        self.exclude_patterns = [p.strip() for p in config['exclude'].split(',') if p.strip()]

        self.stats = {
            'copied': 0,
            'updated': 0,
            'deleted': 0,
            'errors': 0,
            'skipped': 0,
            'bytes_transferred': 0
        }

    def stop(self):
        self.should_stop = True

    def should_include_file(self, file_path):
        """Check if file matches include/exclude patterns"""
        file_name = file_path.name

        # Check exclude patterns first
        for pattern in self.exclude_patterns:
            if fnmatch(file_name, pattern) or fnmatch(str(file_path), f"*{pattern}*"):
                return False

        # If no include patterns, include all (that aren't excluded)
        if not self.include_patterns or self.include_patterns == ['*']:
            return True

        # Check include patterns
        for pattern in self.include_patterns:
            if fnmatch(file_name, pattern):
                return True

        return False

    def get_file_hash(self, file_path):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.log(f"Error hashing {file_path}: {e}", "ERROR")
            return None

    def files_are_different(self, source_file, dest_file):
        """Check if two files are different"""
        if not dest_file.exists():
            return True

        # Compare file sizes first (faster)
        if source_file.stat().st_size != dest_file.stat().st_size:
            return True

        # Compare modification times
        source_mtime = source_file.stat().st_mtime
        dest_mtime = dest_file.stat().st_mtime

        # If dest is older, update it
        if dest_mtime < source_mtime - 2:  # 2 second tolerance
            return True

        # If verification is enabled, compare hashes
        if self.verify:
            source_hash = self.get_file_hash(source_file)
            dest_hash = self.get_file_hash(dest_file)
            return source_hash != dest_hash

        return False

    def throttle_bandwidth(self, bytes_copied):
        """Throttle bandwidth if limit is enabled"""
        if not self.bandwidth_limit or not self.bandwidth_value:
            return

        self.bytes_transferred += bytes_copied

        if self.transfer_start_time is None:
            self.transfer_start_time = time.time()
            return

        elapsed_time = time.time() - self.transfer_start_time
        if elapsed_time <= 0:
            return

        current_speed = self.bytes_transferred / elapsed_time / (1024 * 1024)
        max_speed = self.bandwidth_value

        if current_speed > max_speed:
            sleep_time = (self.bytes_transferred / (max_speed * 1024 * 1024)) - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)

    def copy_file(self, source_file, dest_file):
        """Copy a single file from source to destination with bandwidth throttling"""
        try:
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            is_update = dest_file.exists()

            if is_update and not self.files_are_different(source_file, dest_file):
                self.stats['skipped'] += 1
                return True

            file_size = source_file.stat().st_size

            if self.bandwidth_limit and self.bandwidth_value:
                with open(source_file, 'rb') as src, open(dest_file, 'wb') as dst:
                    chunk_size = 1024 * 1024
                    while True:
                        chunk = src.read(chunk_size)
                        if not chunk:
                            break
                        dst.write(chunk)
                        self.throttle_bandwidth(len(chunk))

                shutil.copystat(source_file, dest_file)
            else:
                shutil.copy2(source_file, dest_file)

            self.stats['bytes_transferred'] += file_size

            if self.verify:
                source_hash = self.get_file_hash(source_file)
                dest_hash = self.get_file_hash(dest_file)

                if source_hash != dest_hash:
                    self.log(f"Verification failed for {source_file.name}", "ERROR")
                    self.stats['errors'] += 1
                    return False

            if is_update:
                self.log(f"Updated: {source_file.name}")
                self.stats['updated'] += 1
            else:
                self.log(f"Copied: {source_file.name}")
                self.stats['copied'] += 1

            return True

        except PermissionError:
            self.log(f"Permission denied: {source_file}", "ERROR")
            self.stats['errors'] += 1
            return False
        except Exception as e:
            self.log(f"Error copying {source_file}: {str(e)}", "ERROR")
            self.stats['errors'] += 1
            return False

    def get_all_files(self, directory):
        """Get all files in directory"""
        files = []
        try:
            if self.subfolders:
                for root, dirs, filenames in os.walk(directory):
                    # Filter out excluded directories
                    dirs[:] = [d for d in dirs if not any(
                        fnmatch(d, pattern) for pattern in self.exclude_patterns
                    )]

                    for filename in filenames:
                        file_path = Path(root) / filename
                        if self.should_include_file(file_path):
                            files.append(file_path)
            else:
                for item in directory.iterdir():
                    if item.is_file() and self.should_include_file(item):
                        files.append(item)
        except PermissionError:
            self.log(f"Permission denied accessing: {directory}", "ERROR")
        except Exception as e:
            self.log(f"Error reading directory {directory}: {str(e)}", "ERROR")

        return files

    def delete_extra_files(self, source_files_rel, dest_files):
        """Delete files in destination that don't exist in source (mirror mode)"""
        if self.mode != 'mirror':
            return

        for dest_file in dest_files:
            if self.should_stop:
                break

            try:
                rel_path = dest_file.relative_to(self.destination)

                if rel_path not in source_files_rel:
                    dest_file.unlink()
                    self.log(f"Deleted: {dest_file.name}")
                    self.stats['deleted'] += 1

            except Exception as e:
                self.log(f"Error deleting {dest_file}: {str(e)}", "ERROR")
                self.stats['errors'] += 1

        # Remove empty directories
        if self.subfolders:
            self.remove_empty_dirs(self.destination)

    def remove_empty_dirs(self, directory):
        """Remove empty directories recursively"""
        try:
            for item in directory.iterdir():
                if item.is_dir():
                    self.remove_empty_dirs(item)
                    try:
                        item.rmdir()
                    except OSError:
                        pass
        except Exception:
            pass

    def apply_retention_policy(self):
        """Delete files older than retention period"""
        if not self.retention_enabled:
            return

        cutoff_time = datetime.now() - timedelta(days=self.retention_days)
        cutoff_timestamp = cutoff_time.timestamp()

        self.log(f"Applying retention policy: keeping files newer than {self.retention_days} days", "INFO")

        try:
            dest_files = self.get_all_files(self.destination)
            cleaned_count = 0

            for dest_file in dest_files:
                if self.should_stop:
                    break

                try:
                    file_mtime = dest_file.stat().st_mtime

                    if file_mtime < cutoff_timestamp:
                        dest_file.unlink()
                        self.log(f"Retention cleanup: Deleted {dest_file.name}", "INFO")
                        cleaned_count += 1

                except Exception as e:
                    self.log(f"Error applying retention to {dest_file}: {str(e)}", "ERROR")

            if cleaned_count > 0:
                self.log(f"Retention policy: Cleaned {cleaned_count} old files", "SUCCESS")
                self.remove_empty_dirs(self.destination)

        except Exception as e:
            self.log(f"Error applying retention policy: {str(e)}", "ERROR")

    def sync(self):
        """Main sync function"""
        self.should_stop = False
        self.log(f"Syncing from {self.source} to {self.destination}")
        self.log(f"Mode: {self.mode}, Verify: {self.verify}, Subfolders: {self.subfolders}")

        try:
            # Get all source files
            source_files = self.get_all_files(self.source)
            total_files = len(source_files)

            if total_files == 0:
                self.log("No files to sync (check your include/exclude patterns)", "WARNING")
                return {
                    'success': True,
                    'copied': 0,
                    'updated': 0,
                    'deleted': 0,
                    'errors': 0
                }

            self.log(f"Found {total_files} files to process")

            # Create destination directory if it doesn't exist
            self.destination.mkdir(parents=True, exist_ok=True)

            # Copy/update files
            for i, source_file in enumerate(source_files):
                if self.should_stop:
                    self.log("Sync stopped by user", "WARNING")
                    break

                rel_path = source_file.relative_to(self.source)
                dest_file = self.destination / rel_path

                self.copy_file(source_file, dest_file)

                # Update progress
                progress = ((i + 1) / total_files) * 100
                self.update_progress(progress)

            # Handle deletions in mirror mode
            if self.mode == 'mirror' and not self.should_stop:
                dest_files = self.get_all_files(self.destination)
                source_files_rel = {f.relative_to(self.source) for f in source_files}
                self.delete_extra_files(source_files_rel, dest_files)

            # Apply retention policy if enabled
            if not self.should_stop:
                self.apply_retention_policy()

            success = self.stats['errors'] == 0

            bytes_mb = self.stats['bytes_transferred'] / (1024 * 1024)
            self.log(f"Total data transferred: {bytes_mb:.2f} MB", "INFO")

            return {
                'success': success,
                'copied': self.stats['copied'],
                'updated': self.stats['updated'],
                'deleted': self.stats['deleted'],
                'errors': self.stats['errors'],
                'skipped': self.stats['skipped']
            }

        except Exception as e:
            self.log(f"Sync failed: {str(e)}", "ERROR")
            return {
                'success': False,
                'copied': self.stats['copied'],
                'updated': self.stats['updated'],
                'deleted': self.stats['deleted'],
                'errors': self.stats['errors'] + 1,
                'skipped': self.stats['skipped']
            }

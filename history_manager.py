import json
import os
from datetime import datetime
from pathlib import Path

class HistoryManager:
    """Manage sync history records"""

    def __init__(self):
        self.history_dir = Path.home() / '.nassync'
        self.history_file = self.history_dir / 'history.json'
        self.history_dir.mkdir(exist_ok=True)

        self.max_history_entries = 1000

    def add_entry(self, source, destination, result):
        """Add a sync history entry"""
        history = self.load_history()

        entry = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'destination': destination,
            'success': result.get('success', False),
            'copied': result.get('copied', 0),
            'updated': result.get('updated', 0),
            'deleted': result.get('deleted', 0),
            'errors': result.get('errors', 0),
            'skipped': result.get('skipped', 0),
            'duration': result.get('duration', 0)
        }

        history.insert(0, entry)

        if len(history) > self.max_history_entries:
            history = history[:self.max_history_entries]

        self.save_history(history)

    def load_history(self):
        """Load sync history from file"""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            return []

    def save_history(self, history):
        """Save sync history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def get_recent_entries(self, count=10):
        """Get most recent history entries"""
        history = self.load_history()
        return history[:count]

    def get_statistics(self):
        """Get overall sync statistics"""
        history = self.load_history()

        if not history:
            return {
                'total_syncs': 0,
                'successful_syncs': 0,
                'failed_syncs': 0,
                'total_files_copied': 0,
                'total_files_updated': 0,
                'total_files_deleted': 0,
                'last_sync': None,
                'success_rate': 0
            }

        total_syncs = len(history)
        successful_syncs = sum(1 for e in history if e.get('success'))
        failed_syncs = total_syncs - successful_syncs

        stats = {
            'total_syncs': total_syncs,
            'successful_syncs': successful_syncs,
            'failed_syncs': failed_syncs,
            'total_files_copied': sum(e.get('copied', 0) for e in history),
            'total_files_updated': sum(e.get('updated', 0) for e in history),
            'total_files_deleted': sum(e.get('deleted', 0) for e in history),
            'last_sync': history[0].get('timestamp') if history else None,
            'success_rate': (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
        }

        return stats

    def clear_history(self):
        """Clear all history"""
        self.save_history([])

    def export_history(self, filepath):
        """Export history to file"""
        history = self.load_history()

        try:
            with open(filepath, 'w') as f:
                f.write("Buffalo LinkStation Sync History\n")
                f.write("=" * 80 + "\n\n")

                for entry in history:
                    f.write(f"Timestamp: {entry['timestamp']}\n")
                    f.write(f"Source: {entry['source']}\n")
                    f.write(f"Destination: {entry['destination']}\n")
                    f.write(f"Status: {'Success' if entry['success'] else 'Failed'}\n")
                    f.write(f"Copied: {entry['copied']}, Updated: {entry['updated']}, "
                           f"Deleted: {entry['deleted']}, Errors: {entry['errors']}\n")
                    f.write(f"Duration: {entry.get('duration', 0):.1f} seconds\n")
                    f.write("-" * 80 + "\n\n")

            return True
        except Exception as e:
            print(f"Error exporting history: {e}")
            return False

    def get_filtered_history(self, start_date=None, end_date=None, success_only=False):
        """Get filtered history entries"""
        history = self.load_history()
        filtered = []

        for entry in history:
            try:
                entry_date = datetime.fromisoformat(entry['timestamp'])

                if start_date and entry_date < start_date:
                    continue

                if end_date and entry_date > end_date:
                    continue

                if success_only and not entry.get('success'):
                    continue

                filtered.append(entry)
            except:
                continue

        return filtered

import json
import os
from pathlib import Path

class ConfigManager:
    def __init__(self):
        # Store config in user's home directory
        self.config_dir = Path.home() / '.nassync'
        self.config_file = self.config_dir / 'config.json'

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)

    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def load_config(self):
        """Load configuration from file"""
        if not self.config_file.exists():
            return None

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return None

    def get_config_path(self):
        """Get the path to the config file"""
        return str(self.config_file)

import sys
import os
from pathlib import Path

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("Warning: pystray/PIL not installed. Tray icon disabled.")
    print("Install with: pip install pystray pillow")

class TrayIcon:
    """System tray icon manager for Windows"""

    def __init__(self, app_instance):
        self.app = app_instance
        self.icon = None
        self.is_running = False

        if not TRAY_AVAILABLE:
            return

    def create_icon_image(self, color="blue"):
        """Create a simple icon image"""
        width = 64
        height = 64

        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)

        if color == "blue":
            fill_color = (14, 165, 233)
        elif color == "green":
            fill_color = (16, 185, 129)
        elif color == "orange":
            fill_color = (245, 158, 11)
        elif color == "red":
            fill_color = (239, 68, 68)
        else:
            fill_color = (14, 165, 233)

        draw.ellipse([8, 8, 56, 56], fill=fill_color, outline='white')

        draw.rectangle([20, 28, 44, 36], fill='white')
        draw.rectangle([28, 20, 36, 44], fill='white')

        return image

    def create_menu(self):
        """Create tray icon menu"""
        if not TRAY_AVAILABLE:
            return None

        return pystray.Menu(
            pystray.MenuItem("Show Window", self.show_window, default=True),
            pystray.MenuItem("Sync Now", self.sync_now),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Auto-Sync", self.toggle_auto_sync, checked=lambda item: self.app.auto_sync_active),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("View History", self.show_history),
            pystray.MenuItem("Open Logs", self.open_logs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.exit_app)
        )

    def show_window(self, icon=None, item=None):
        """Show the main window"""
        self.app.root.after(0, self.app.root.deiconify)
        self.app.root.after(0, self.app.root.lift)
        self.app.root.after(0, self.app.root.focus_force)

    def sync_now(self, icon=None, item=None):
        """Trigger sync from tray"""
        self.app.root.after(0, self.app.sync_now)

    def toggle_auto_sync(self, icon=None, item=None):
        """Toggle auto-sync from tray"""
        self.app.root.after(0, self.app.toggle_auto_sync)

    def show_history(self, icon=None, item=None):
        """Show history window"""
        self.app.root.after(0, lambda: self.app.notebook.select(4))
        self.show_window()

    def open_logs(self, icon=None, item=None):
        """Open logs tab"""
        self.app.root.after(0, lambda: self.app.notebook.select(3))
        self.show_window()

    def exit_app(self, icon=None, item=None):
        """Exit application"""
        if self.icon:
            self.icon.stop()
        self.app.root.after(0, self.app.quit_app)

    def update_icon(self, status="idle"):
        """Update tray icon based on status"""
        if not TRAY_AVAILABLE or not self.icon:
            return

        color_map = {
            "idle": "blue",
            "syncing": "orange",
            "success": "green",
            "error": "red"
        }

        color = color_map.get(status, "blue")
        new_image = self.create_icon_image(color)

        try:
            self.icon.icon = new_image
        except:
            pass

    def update_tooltip(self, text):
        """Update tray icon tooltip"""
        if not TRAY_AVAILABLE or not self.icon:
            return

        try:
            self.icon.title = f"Buffalo LinkStation Sync\n{text}"
        except:
            pass

    def show_notification(self, title, message):
        """Show system tray notification"""
        if not TRAY_AVAILABLE or not self.icon:
            return

        try:
            self.icon.notify(message, title)
        except:
            pass

    def start(self):
        """Start the tray icon"""
        if not TRAY_AVAILABLE:
            return

        self.is_running = True
        icon_image = self.create_icon_image("blue")

        self.icon = pystray.Icon(
            "buffalo_sync",
            icon_image,
            "Buffalo LinkStation Sync Manager",
            menu=self.create_menu()
        )

        import threading
        tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        tray_thread.start()

    def stop(self):
        """Stop the tray icon"""
        if self.icon and TRAY_AVAILABLE:
            self.icon.stop()
            self.is_running = False

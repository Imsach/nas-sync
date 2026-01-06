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
        self.base_icon = None 

        if not TRAY_AVAILABLE:
            return

        self._load_base_icon()



    def _load_base_icon(self):
        """Load nassync.ico (preferred on Windows)"""
        icon_path = Path(__file__).parent / "nassync.ico"

        try:
            if icon_path.exists():
                self.base_icon = Image.open(icon_path)
        except Exception as e:
            print(f"[TrayIcon] Failed to load nassync.ico: {e}")
            self.base_icon = None

    def create_icon_image(self, color="blue"):
        """
        Fallback icon generator.
        Used ONLY if ICO is missing.
        """
        width = 64
        height = 64

        image = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(image)

        color_map = {
            "blue": (14, 165, 233),
            "green": (16, 185, 129),
            "orange": (245, 158, 11),
            "red": (239, 68, 68),
        }

        fill_color = color_map.get(color, (14, 165, 233))

        draw.ellipse([8, 8, 56, 56], fill=fill_color, outline="white")
        draw.rectangle([20, 28, 44, 36], fill="white")
        draw.rectangle([28, 20, 36, 44], fill="white")

        return image



    def create_menu(self):
        if not TRAY_AVAILABLE:
            return None

        return pystray.Menu(
            pystray.MenuItem("Show Window", self.show_window, default=True),
            pystray.MenuItem("Sync Now", self.sync_now),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Auto-Sync",
                self.toggle_auto_sync,
                checked=lambda item: self.app.auto_sync_active,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("View History", self.show_history),
            pystray.MenuItem("Open Logs", self.open_logs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.exit_app),
        )


    def show_window(self, icon=None, item=None):
        self.app.root.after(0, self.app.root.deiconify)
        self.app.root.after(0, self.app.root.lift)
        self.app.root.after(0, self.app.root.focus_force)

    def sync_now(self, icon=None, item=None):
        self.app.root.after(0, self.app.sync_now)

    def toggle_auto_sync(self, icon=None, item=None):
        self.app.root.after(0, self.app.toggle_auto_sync)

    def show_history(self, icon=None, item=None):
        self.app.root.after(0, lambda: self.app.notebook.select(4))
        self.show_window()

    def open_logs(self, icon=None, item=None):
        self.app.root.after(0, lambda: self.app.notebook.select(3))
        self.show_window()

    def exit_app(self, icon=None, item=None):
        if self.icon:
            self.icon.stop()
        self.app.root.after(0, self.app.quit_app)



    def update_icon(self, status="idle"):
        """
        Preserve original API.
        ICO stays static (Windows tray stability).
        """
        if not TRAY_AVAILABLE or not self.icon:
            return

        # If ICO exists → do nothing (prevents Windows cache issues)
        if self.base_icon:
            return

        # Fallback dynamic icon
        color_map = {
            "idle": "blue",
            "syncing": "orange",
            "success": "green",
            "error": "red",
        }

        new_image = self.create_icon_image(color_map.get(status, "blue"))
        try:
            self.icon.icon = new_image
        except Exception:
            pass

    def update_tooltip(self, text):
        if not TRAY_AVAILABLE or not self.icon:
            return

        try:
            self.icon.title = f"NAS Sync\n{text}"
        except Exception:
            pass

    def show_notification(self, title, message):
        if not TRAY_AVAILABLE or not self.icon:
            return

        try:
            self.icon.notify(message, title)
        except Exception:
            pass


    def start(self):
        if not TRAY_AVAILABLE:
            return

        self.is_running = True

        icon_image = self.base_icon or self.create_icon_image("blue")

        self.icon = pystray.Icon(
            "NAS_sync", 
            icon_image,
            "NAS Sync Manager",
            menu=self.create_menu(),
        )

        import threading

        tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        tray_thread.start()

    def stop(self):
        if self.icon and TRAY_AVAILABLE:
            self.icon.stop()
            self.is_running = False

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
from datetime import datetime, timedelta
import os
import sys
from sync_engine import SyncEngine
from config_manager import ConfigManager
from history_manager import HistoryManager
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from tray_icon import TrayIcon, TRAY_AVAILABLE
except ImportError:
    TRAY_AVAILABLE = False
    TrayIcon = None
    print("Tray icon not available - install pystray and pillow for tray support")

class ModernTheme:
    """Modern color theme for elegant UI"""
    BG_PRIMARY = "#FFFFFF"
    BG_SECONDARY = "#F8FAFB"
    BG_ACCENT = "#E8F4F8"

    TEXT_PRIMARY = "#1A202C"
    TEXT_SECONDARY = "#4A5568"
    TEXT_MUTED = "#718096"

    ACCENT_PRIMARY = "#0EA5E9"
    ACCENT_HOVER = "#0284C7"
    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"

    BORDER = "#E2E8F0"
    SHADOW = "#00000010"

class NASyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Buffalo LinkStation Sync Manager")
        self.root.geometry("1100x750")
        self.root.minsize(1000, 650)

        self.config_manager = ConfigManager()
        self.history_manager = HistoryManager()
        self.sync_engine = None
        self.sync_thread = None
        self.is_syncing = False
        self.auto_sync_active = False
        self.last_sync_time = None
        self.next_sync_time = None
        self.sync_start_time = None
        self.minimize_to_tray = True

        self.tray_icon = None
        if TRAY_AVAILABLE and TrayIcon:
            self.tray_icon = TrayIcon(self)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.setup_styles()
        self.setup_ui()
        self.load_config()
        self.update_stats()

        if self.tray_icon and TRAY_AVAILABLE:
            self.tray_icon.start()
            self.log("System tray icon enabled", "INFO")

    def setup_styles(self):
        """Configure modern styling"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        self.root.configure(bg=ModernTheme.BG_SECONDARY)

        # Frame styles
        style.configure('Main.TFrame', background=ModernTheme.BG_SECONDARY)
        style.configure('Card.TFrame', background=ModernTheme.BG_PRIMARY,
                       relief='flat', borderwidth=0)

        # Label styles
        style.configure('Title.TLabel', background=ModernTheme.BG_SECONDARY,
                       foreground=ModernTheme.TEXT_PRIMARY, font=('Segoe UI', 20, 'bold'))
        style.configure('Subtitle.TLabel', background=ModernTheme.BG_PRIMARY,
                       foreground=ModernTheme.TEXT_SECONDARY, font=('Segoe UI', 10))
        style.configure('Card.TLabel', background=ModernTheme.BG_PRIMARY,
                       foreground=ModernTheme.TEXT_PRIMARY, font=('Segoe UI', 9))
        style.configure('Stat.TLabel', background=ModernTheme.BG_PRIMARY,
                       foreground=ModernTheme.ACCENT_PRIMARY, font=('Segoe UI', 16, 'bold'))

        # LabelFrame style
        style.configure('Card.TLabelframe', background=ModernTheme.BG_PRIMARY,
                       foreground=ModernTheme.TEXT_PRIMARY, borderwidth=1,
                       relief='solid')
        style.configure('Card.TLabelframe.Label', background=ModernTheme.BG_PRIMARY,
                       foreground=ModernTheme.TEXT_PRIMARY, font=('Segoe UI', 10, 'bold'))

        # Button styles
        style.configure('Primary.TButton', font=('Segoe UI', 9), padding=8)
        style.map('Primary.TButton',
                 background=[('active', ModernTheme.ACCENT_HOVER),
                           ('!active', ModernTheme.ACCENT_PRIMARY)],
                 foreground=[('active', 'white'), ('!active', 'white')])

        # Entry style
        style.configure('Modern.TEntry', fieldbackground='white',
                       borderwidth=1, relief='solid')

    def setup_ui(self):
        """Create the modern UI layout"""
        # Main container
        main_container = ttk.Frame(self.root, style='Main.TFrame', padding="15")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # Header
        header_frame = ttk.Frame(main_container, style='Main.TFrame')
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        title = ttk.Label(header_frame, text="Buffalo LinkStation Sync Manager",
                         style='Title.TLabel')
        title.pack(side=tk.LEFT)

        # Connection status indicator
        self.connection_frame = ttk.Frame(header_frame, style='Main.TFrame')
        self.connection_frame.pack(side=tk.RIGHT)
        self.connection_indicator = tk.Canvas(self.connection_frame, width=12, height=12,
                                             bg=ModernTheme.BG_SECONDARY, highlightthickness=0)
        self.connection_indicator.pack(side=tk.LEFT, padx=(0, 5))
        self.connection_label = ttk.Label(self.connection_frame, text="Not Connected",
                                         style='Subtitle.TLabel')
        self.connection_label.pack(side=tk.LEFT)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Tabs
        self.create_overview_tab()
        self.create_config_tab()
        self.create_advanced_tab()
        self.create_logs_tab()
        self.create_history_tab()

    def create_overview_tab(self):
        """Create dashboard overview tab"""
        tab = ttk.Frame(self.notebook, style='Main.TFrame', padding="15")
        self.notebook.add(tab, text="  Dashboard  ")
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)

        # Quick Stats Cards
        stats_frame = ttk.Frame(tab, style='Main.TFrame')
        stats_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        stats_frame.columnconfigure(3, weight=1)

        self.stat_cards = {}
        stats_data = [
            ("last_sync", "Last Sync", "Never", ModernTheme.ACCENT_PRIMARY),
            ("next_sync", "Next Sync", "Not Scheduled", ModernTheme.TEXT_SECONDARY),
            ("files_synced", "Files Synced", "0", ModernTheme.SUCCESS),
            ("sync_status", "Status", "Ready", ModernTheme.SUCCESS)
        ]

        for idx, (key, title, default, color) in enumerate(stats_data):
            card = self.create_stat_card(stats_frame, title, default, color)
            card["frame"].grid(row=0, column=idx, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.stat_cards[key] = card['value_label']

        # Quick Actions
        actions_frame = ttk.LabelFrame(tab, text="Quick Actions", style='Card.TLabelframe',
                                      padding="15")
        actions_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15), padx=(0, 8))

        self.sync_now_btn = tk.Button(actions_frame, text="⚡ Sync Now",
                                      command=self.sync_now, bg=ModernTheme.ACCENT_PRIMARY,
                                      fg='white', font=('Segoe UI', 10, 'bold'),
                                      relief='flat', cursor='hand2', padx=20, pady=12)
        self.sync_now_btn.pack(fill=tk.X, pady=(0, 10))

        self.auto_sync_btn = tk.Button(actions_frame, text="▶ Start Auto-Sync",
                                       command=self.toggle_auto_sync, bg='#10B981',
                                       fg='white', font=('Segoe UI', 10, 'bold'),
                                       relief='flat', cursor='hand2', padx=20, pady=12)
        self.auto_sync_btn.pack(fill=tk.X, pady=(0, 10))

        self.stop_btn = tk.Button(actions_frame, text="⏹ Stop Sync",
                                 command=self.stop_sync, bg=ModernTheme.ERROR,
                                 fg='white', font=('Segoe UI', 10, 'bold'),
                                 relief='flat', cursor='hand2', padx=20, pady=12,
                                 state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, pady=(0, 10))

        test_btn = tk.Button(actions_frame, text="🔍 Test NAS Connection",
                            command=self.test_connection, bg='#6366F1',
                            fg='white', font=('Segoe UI', 9), relief='flat',
                            cursor='hand2', padx=15, pady=8)
        test_btn.pack(fill=tk.X)

        # Progress Section
        progress_frame = ttk.LabelFrame(tab, text="Sync Progress", style='Card.TLabelframe',
                                       padding="15")
        progress_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15), padx=(8, 0))
        progress_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate',
                                           variable=self.progress_var, length=300)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        self.progress_label = ttk.Label(progress_frame, text="0% Complete",
                                       style='Card.TLabel')
        self.progress_label.pack()

        self.status_text = ttk.Label(progress_frame, text="Waiting to start...",
                                    style='Subtitle.TLabel', wraplength=300)
        self.status_text.pack(pady=(10, 0))

        # Mini log preview
        log_preview_frame = ttk.LabelFrame(tab, text="Recent Activity",
                                          style='Card.TLabelframe', padding="15")
        log_preview_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_preview_frame.columnconfigure(0, weight=1)
        log_preview_frame.rowconfigure(0, weight=1)

        self.mini_log = scrolledtext.ScrolledText(log_preview_frame, height=8,
                                                 state=tk.DISABLED, wrap=tk.WORD,
                                                 font=('Consolas', 9),
                                                 bg=ModernTheme.BG_SECONDARY,
                                                 relief='flat')
        self.mini_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def create_stat_card(self, parent, title, value, color):
        """Create a statistics card"""
        card = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        card_inner = ttk.Frame(card, style='Card.TFrame', padding="12")
        card_inner.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(card_inner, text=title, style='Subtitle.TLabel')
        title_label.pack(anchor=tk.W)

        value_label = ttk.Label(card_inner, text=value, font=('Segoe UI', 14, 'bold'),
                               foreground=color, background=ModernTheme.BG_PRIMARY)
        value_label.pack(anchor=tk.W, pady=(5, 0))

        return {'frame': card, 'value_label': value_label}

    def create_config_tab(self):
        """Create configuration tab"""
        tab = ttk.Frame(self.notebook, style='Main.TFrame', padding="15")
        self.notebook.add(tab, text="  Configuration  ")
        tab.columnconfigure(0, weight=1)

        # Paths Section
        paths_frame = ttk.LabelFrame(tab, text="Sync Paths", style='Card.TLabelframe',
                                    padding="15")
        paths_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        paths_frame.columnconfigure(1, weight=1)

        # Buffalo LinkStation quick preset
        ttk.Label(paths_frame, text="Quick Setup:", style='Card.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10))
        preset_frame = ttk.Frame(paths_frame, style='Card.TFrame')
        preset_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(preset_frame, text="Buffalo LinkStation:", style='Subtitle.TLabel').pack(
            side=tk.LEFT, padx=(0, 10))
        self.nas_drive_var = tk.StringVar()
        nas_combo = ttk.Combobox(preset_frame, textvariable=self.nas_drive_var,
                                values=self.detect_network_drives(), width=15, state='readonly')
        nas_combo.pack(side=tk.LEFT, padx=(0, 10))

        apply_preset_btn = tk.Button(preset_frame, text="Apply", command=self.apply_nas_preset,
                                     bg=ModernTheme.ACCENT_PRIMARY, fg='white',
                                     font=('Segoe UI', 8), relief='flat', cursor='hand2',
                                     padx=10, pady=4)
        apply_preset_btn.pack(side=tk.LEFT)

        # Source folder
        ttk.Label(paths_frame, text="Source Folder (PC):", style='Card.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=8)
        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(paths_frame, textvariable=self.source_var, width=50)
        source_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=8)
        browse_src_btn = tk.Button(paths_frame, text="Browse", command=self.browse_source,
                                   bg=ModernTheme.BG_ACCENT, font=('Segoe UI', 8),
                                   relief='flat', cursor='hand2', padx=12, pady=6)
        browse_src_btn.grid(row=1, column=2)

        # Destination folder
        ttk.Label(paths_frame, text="Destination (NAS):", style='Card.TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=8)
        self.dest_var = tk.StringVar()
        dest_entry = ttk.Entry(paths_frame, textvariable=self.dest_var, width=50)
        dest_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=8)
        browse_dest_btn = tk.Button(paths_frame, text="Browse", command=self.browse_dest,
                                    bg=ModernTheme.BG_ACCENT, font=('Segoe UI', 8),
                                    relief='flat', cursor='hand2', padx=12, pady=6)
        browse_dest_btn.grid(row=2, column=2)

        # Sync Options
        options_frame = ttk.LabelFrame(tab, text="Sync Options", style='Card.TLabelframe',
                                      padding="15")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        options_frame.columnconfigure(1, weight=1)

        # Interval
        ttk.Label(options_frame, text="Auto-Sync Interval:", style='Card.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=8)
        interval_frame = ttk.Frame(options_frame, style='Card.TFrame')
        interval_frame.grid(row=0, column=1, sticky=tk.W, padx=8)
        self.interval_var = tk.StringVar(value="30")
        ttk.Spinbox(interval_frame, from_=1, to=1440, textvariable=self.interval_var,
                   width=10).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(interval_frame, text="minutes", style='Subtitle.TLabel').pack(side=tk.LEFT)

        # Sync mode
        ttk.Label(options_frame, text="Sync Mode:", style='Card.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=8)
        self.sync_mode_var = tk.StringVar(value="mirror")
        mode_frame = ttk.Frame(options_frame, style='Card.TFrame')
        mode_frame.grid(row=1, column=1, sticky=tk.W, padx=8)
        ttk.Radiobutton(mode_frame, text="Mirror (exact copy)", variable=self.sync_mode_var,
                       value="mirror").pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(mode_frame, text="Copy Only (preserve extra files)",
                       variable=self.sync_mode_var, value="copy").pack(side=tk.LEFT)

        # File Filters
        filters_frame = ttk.LabelFrame(tab, text="File Filters", style='Card.TLabelframe',
                                      padding="15")
        filters_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        filters_frame.columnconfigure(1, weight=1)

        ttk.Label(filters_frame, text="Include Patterns:", style='Card.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=8)
        self.include_var = tk.StringVar(value="*")
        ttk.Entry(filters_frame, textvariable=self.include_var, width=50).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=8)
        ttk.Label(filters_frame, text="e.g., *.jpg,*.png,*.docx",
                 style='Subtitle.TLabel').grid(row=0, column=2, sticky=tk.W)

        ttk.Label(filters_frame, text="Exclude Patterns:", style='Card.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=8)
        self.exclude_var = tk.StringVar(value="*.tmp,~*,.DS_Store,Thumbs.db")
        ttk.Entry(filters_frame, textvariable=self.exclude_var, width=50).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=8)
        ttk.Label(filters_frame, text="e.g., *.tmp,~*,.git",
                 style='Subtitle.TLabel').grid(row=1, column=2, sticky=tk.W)

        # Additional Options
        extra_frame = ttk.LabelFrame(tab, text="Additional Options", style='Card.TLabelframe',
                                    padding="15")
        extra_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))

        self.verify_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(extra_frame, text="Verify files after copy (MD5 hash)",
                       variable=self.verify_var).pack(anchor=tk.W, pady=5)

        self.subfolders_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(extra_frame, text="Include subfolders (recursive)",
                       variable=self.subfolders_var).pack(anchor=tk.W, pady=5)

        self.notifications_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(extra_frame, text="Send email notifications on completion",
                       variable=self.notifications_var).pack(anchor=tk.W, pady=5)

        # Save button
        save_btn = tk.Button(tab, text="💾 Save Configuration", command=self.save_config,
                           bg=ModernTheme.SUCCESS, fg='white', font=('Segoe UI', 10, 'bold'),
                           relief='flat', cursor='hand2', padx=20, pady=10)
        save_btn.grid(row=4, column=0, pady=(15, 0))

    def create_advanced_tab(self):
        """Create advanced settings tab"""
        tab = ttk.Frame(self.notebook, style='Main.TFrame', padding="15")
        self.notebook.add(tab, text="  Advanced  ")
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)

        # Bandwidth Control
        bandwidth_frame = ttk.LabelFrame(tab, text="Bandwidth Control",
                                        style='Card.TLabelframe', padding="15")
        bandwidth_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S),
                            pady=(0, 15), padx=(0, 8))
        bandwidth_frame.columnconfigure(1, weight=1)

        self.bandwidth_limit_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bandwidth_frame, text="Enable bandwidth limiting",
                       variable=self.bandwidth_limit_var,
                       command=self.toggle_bandwidth).grid(
                           row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        ttk.Label(bandwidth_frame, text="Max Speed:", style='Card.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.bandwidth_value_var = tk.StringVar(value="10")
        self.bandwidth_spinbox = ttk.Spinbox(bandwidth_frame, from_=1, to=1000,
                                            textvariable=self.bandwidth_value_var,
                                            width=10, state=tk.DISABLED)
        self.bandwidth_spinbox.grid(row=1, column=1, sticky=tk.W, padx=8)
        ttk.Label(bandwidth_frame, text="MB/s", style='Subtitle.TLabel').grid(
            row=1, column=2, sticky=tk.W)

        # Retention Policy
        retention_frame = ttk.LabelFrame(tab, text="Backup Retention Policy",
                                        style='Card.TLabelframe', padding="15")
        retention_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S),
                           pady=(0, 15), padx=(8, 0))
        retention_frame.columnconfigure(1, weight=1)

        self.retention_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(retention_frame, text="Enable automatic cleanup",
                       variable=self.retention_enabled_var,
                       command=self.toggle_retention).grid(
                           row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        ttk.Label(retention_frame, text="Keep files for:", style='Card.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.retention_days_var = tk.StringVar(value="30")
        self.retention_spinbox = ttk.Spinbox(retention_frame, from_=1, to=365,
                                            textvariable=self.retention_days_var,
                                            width=10, state=tk.DISABLED)
        self.retention_spinbox.grid(row=1, column=1, sticky=tk.W, padx=8)
        ttk.Label(retention_frame, text="days", style='Subtitle.TLabel').grid(
            row=1, column=2, sticky=tk.W)

        # Email Notifications
        email_frame = ttk.LabelFrame(tab, text="Email Notifications",
                                    style='Card.TLabelframe', padding="15")
        email_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        email_frame.columnconfigure(1, weight=1)

        ttk.Label(email_frame, text="SMTP Server:", style='Card.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.smtp_server_var = tk.StringVar(value="smtp.gmail.com")
        ttk.Entry(email_frame, textvariable=self.smtp_server_var, width=30).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=8)

        ttk.Label(email_frame, text="SMTP Port:", style='Card.TLabel').grid(
            row=0, column=2, sticky=tk.W, pady=5, padx=(15, 0))
        self.smtp_port_var = tk.StringVar(value="587")
        ttk.Entry(email_frame, textvariable=self.smtp_port_var, width=10).grid(
            row=0, column=3, sticky=tk.W, padx=8)

        ttk.Label(email_frame, text="From Email:", style='Card.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.from_email_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.from_email_var, width=30).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=8)

        ttk.Label(email_frame, text="To Email:", style='Card.TLabel').grid(
            row=1, column=2, sticky=tk.W, pady=5, padx=(15, 0))
        self.to_email_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.to_email_var, width=30).grid(
            row=1, column=3, sticky=(tk.W, tk.E), padx=8)

        ttk.Label(email_frame, text="Password:", style='Card.TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.email_password_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.email_password_var, show="*", width=30).grid(
            row=2, column=1, sticky=(tk.W, tk.E), padx=8)

        test_email_btn = tk.Button(email_frame, text="Send Test Email",
                                   command=self.send_test_email, bg=ModernTheme.ACCENT_PRIMARY,
                                   fg='white', font=('Segoe UI', 8), relief='flat',
                                   cursor='hand2', padx=15, pady=6)
        test_email_btn.grid(row=2, column=2, columnspan=2, padx=(15, 0))

        # Scheduled Sync Times
        schedule_frame = ttk.LabelFrame(tab, text="Scheduled Sync Times (Optional)",
                                       style='Card.TLabelframe', padding="15")
        schedule_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        schedule_frame.columnconfigure(1, weight=1)

        self.scheduled_sync_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(schedule_frame, text="Sync only at specific times",
                       variable=self.scheduled_sync_var).grid(
                           row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(schedule_frame, text="Sync Times:", style='Subtitle.TLabel').grid(
            row=1, column=0, sticky=tk.W)
        ttk.Label(schedule_frame, text="(comma-separated, 24h format, e.g., 09:00,13:00,18:00)",
                 style='Subtitle.TLabel').grid(row=1, column=1, sticky=tk.W, padx=8)

        self.schedule_times_var = tk.StringVar(value="09:00,18:00")
        ttk.Entry(schedule_frame, textvariable=self.schedule_times_var, width=50).grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

    def create_logs_tab(self):
        """Create logs tab"""
        tab = ttk.Frame(self.notebook, style='Main.TFrame', padding="15")
        self.notebook.add(tab, text="  Logs  ")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

        # Log controls
        log_controls = ttk.Frame(tab, style='Main.TFrame')
        log_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(log_controls, text="Detailed Sync Logs", font=('Segoe UI', 12, 'bold'),
                 style='Card.TLabel', background=ModernTheme.BG_SECONDARY).pack(side=tk.LEFT)

        clear_btn = tk.Button(log_controls, text="Clear Logs", command=self.clear_log,
                             bg=ModernTheme.BG_ACCENT, font=('Segoe UI', 8),
                             relief='flat', cursor='hand2', padx=15, pady=6)
        clear_btn.pack(side=tk.RIGHT)

        export_btn = tk.Button(log_controls, text="Export Logs", command=self.export_logs,
                              bg=ModernTheme.BG_ACCENT, font=('Segoe UI', 8),
                              relief='flat', cursor='hand2', padx=15, pady=6)
        export_btn.pack(side=tk.RIGHT, padx=(0, 10))

        # Log text area
        log_frame = ttk.Frame(tab, style='Card.TFrame', relief='solid', borderwidth=1)
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, state=tk.DISABLED, wrap=tk.WORD,
                                                 font=('Consolas', 9),
                                                 bg=ModernTheme.BG_PRIMARY)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2, pady=2)

        # Configure log colors
        self.log_text.tag_config("ERROR", foreground=ModernTheme.ERROR)
        self.log_text.tag_config("SUCCESS", foreground=ModernTheme.SUCCESS)
        self.log_text.tag_config("WARNING", foreground=ModernTheme.WARNING)
        self.log_text.tag_config("INFO", foreground=ModernTheme.TEXT_SECONDARY)

    def create_history_tab(self):
        """Create sync history tab"""
        tab = ttk.Frame(self.notebook, style='Main.TFrame', padding="15")
        self.notebook.add(tab, text="  History  ")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

        # History stats
        stats_frame = ttk.LabelFrame(tab, text="Overall Statistics", style='Card.TLabelframe',
                                    padding="15")
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        stats_frame.columnconfigure(3, weight=1)

        self.history_stat_labels = {}
        stat_names = [
            ("total_syncs", "Total Syncs"),
            ("successful_syncs", "Successful"),
            ("failed_syncs", "Failed"),
            ("success_rate", "Success Rate")
        ]

        for idx, (key, label) in enumerate(stat_names):
            stat_frame = ttk.Frame(stats_frame, style='Card.TFrame')
            stat_frame.grid(row=0, column=idx, padx=10, pady=5)

            ttk.Label(stat_frame, text=label, style='Subtitle.TLabel').pack()
            value_label = ttk.Label(stat_frame, text="0", font=('Segoe UI', 14, 'bold'),
                                  foreground=ModernTheme.ACCENT_PRIMARY,
                                  background=ModernTheme.BG_PRIMARY)
            value_label.pack(pady=(5, 0))
            self.history_stat_labels[key] = value_label

        # History controls
        controls_frame = ttk.Frame(tab, style='Main.TFrame')
        controls_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(controls_frame, text="Sync History", font=('Segoe UI', 12, 'bold'),
                 style='Card.TLabel', background=ModernTheme.BG_SECONDARY).pack(side=tk.LEFT)

        export_hist_btn = tk.Button(controls_frame, text="Export History",
                                    command=self.export_history, bg=ModernTheme.BG_ACCENT,
                                    font=('Segoe UI', 8), relief='flat', cursor='hand2',
                                    padx=15, pady=6)
        export_hist_btn.pack(side=tk.RIGHT)

        clear_hist_btn = tk.Button(controls_frame, text="Clear History",
                                   command=self.clear_history, bg=ModernTheme.BG_ACCENT,
                                   font=('Segoe UI', 8), relief='flat', cursor='hand2',
                                   padx=15, pady=6)
        clear_hist_btn.pack(side=tk.RIGHT, padx=(0, 10))

        refresh_hist_btn = tk.Button(controls_frame, text="Refresh",
                                     command=self.refresh_history, bg=ModernTheme.BG_ACCENT,
                                     font=('Segoe UI', 8), relief='flat', cursor='hand2',
                                     padx=15, pady=6)
        refresh_hist_btn.pack(side=tk.RIGHT, padx=(0, 10))

        # History table
        history_frame = ttk.Frame(tab, style='Card.TFrame', relief='solid', borderwidth=1)
        history_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)

        columns = ("timestamp", "status", "copied", "updated", "deleted", "errors", "duration")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings',
                                        height=15)

        self.history_tree.heading("timestamp", text="Date & Time")
        self.history_tree.heading("status", text="Status")
        self.history_tree.heading("copied", text="Copied")
        self.history_tree.heading("updated", text="Updated")
        self.history_tree.heading("deleted", text="Deleted")
        self.history_tree.heading("errors", text="Errors")
        self.history_tree.heading("duration", text="Duration")

        self.history_tree.column("timestamp", width=150)
        self.history_tree.column("status", width=80)
        self.history_tree.column("copied", width=80)
        self.history_tree.column("updated", width=80)
        self.history_tree.column("deleted", width=80)
        self.history_tree.column("errors", width=80)
        self.history_tree.column("duration", width=100)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL,
                                 command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2, pady=2)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.refresh_history()

    def refresh_history(self):
        """Refresh history display"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        stats = self.history_manager.get_statistics()

        self.history_stat_labels['total_syncs'].config(text=str(stats['total_syncs']))
        self.history_stat_labels['successful_syncs'].config(text=str(stats['successful_syncs']))
        self.history_stat_labels['failed_syncs'].config(text=str(stats['failed_syncs']))
        self.history_stat_labels['success_rate'].config(
            text=f"{stats['success_rate']:.1f}%"
        )

        history = self.history_manager.get_recent_entries(100)

        for entry in history:
            try:
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            except:
                timestamp = entry['timestamp']

            status = "Success" if entry.get('success') else "Failed"
            duration = f"{entry.get('duration', 0):.1f}s"

            values = (
                timestamp,
                status,
                entry.get('copied', 0),
                entry.get('updated', 0),
                entry.get('deleted', 0),
                entry.get('errors', 0),
                duration
            )

            item_id = self.history_tree.insert("", tk.END, values=values)

            if not entry.get('success'):
                self.history_tree.item(item_id, tags=('error',))

        self.history_tree.tag_configure('error', foreground=ModernTheme.ERROR)

    def export_history(self):
        """Export history to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"sync_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            if filename:
                if self.history_manager.export_history(filename):
                    messagebox.showinfo("Success", "History exported successfully!")
                else:
                    messagebox.showerror("Error", "Failed to export history")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export history:\n{str(e)}")

    def clear_history(self):
        """Clear sync history"""
        result = messagebox.askyesno("Confirm", "Are you sure you want to clear all sync history?")
        if result:
            self.history_manager.clear_history()
            self.refresh_history()
            messagebox.showinfo("Success", "History cleared successfully!")

    def detect_network_drives(self):
        """Detect available network drives (Windows) or mounted shares"""
        drives = []
        if sys.platform == 'win32':
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        if os.path.ismount(drive) or 'NETWORK' in os.popen(f'net use {letter}:').read().upper():
                            drives.append(drive)
                    except:
                        pass
        else:
            # Linux/Mac - check common mount points
            mount_points = ['/mnt', '/media', '/Volumes']
            for mount_point in mount_points:
                if os.path.exists(mount_point):
                    try:
                        for item in os.listdir(mount_point):
                            full_path = os.path.join(mount_point, item)
                            if os.path.ismount(full_path):
                                drives.append(full_path)
                    except:
                        pass
        return drives if drives else ["No drives detected"]

    def apply_nas_preset(self):
        """Apply Buffalo LinkStation preset"""
        nas_drive = self.nas_drive_var.get()
        if nas_drive and nas_drive != "No drives detected":
            self.dest_var.set(nas_drive)
            self.log("Applied Buffalo LinkStation preset", "INFO")
            self.update_connection_status(True)

    def toggle_bandwidth(self):
        """Toggle bandwidth limiting option"""
        state = tk.NORMAL if self.bandwidth_limit_var.get() else tk.DISABLED
        self.bandwidth_spinbox.config(state=state)

    def toggle_retention(self):
        """Toggle retention policy option"""
        state = tk.NORMAL if self.retention_enabled_var.get() else tk.DISABLED
        self.retention_spinbox.config(state=state)

    def test_connection(self):
        """Test connection to NAS"""
        dest = self.dest_var.get()
        if not dest:
            messagebox.showwarning("No Destination", "Please set a destination path first.")
            return

        self.log("Testing NAS connection...", "INFO")
        try:
            if os.path.exists(dest) and os.path.isdir(dest):
                # Try to write a test file
                test_file = os.path.join(dest, '.nassync_test')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)

                self.log("Connection test successful!", "SUCCESS")
                self.update_connection_status(True)
                messagebox.showinfo("Success", "Buffalo LinkStation connection successful!")
            else:
                self.log("Connection test failed: Path not accessible", "ERROR")
                self.update_connection_status(False)
                messagebox.showerror("Error", "Cannot access NAS path. Please check:\n"
                                    "1. Buffalo LinkStation is powered on\n"
                                    "2. Network drive is mapped correctly\n"
                                    "3. You have write permissions")
        except Exception as e:
            self.log(f"Connection test failed: {str(e)}", "ERROR")
            self.update_connection_status(False)
            messagebox.showerror("Error", f"Connection failed:\n{str(e)}")

    def update_connection_status(self, connected):
        """Update connection status indicator"""
        if connected:
            self.connection_indicator.create_oval(2, 2, 10, 10, fill=ModernTheme.SUCCESS, outline='')
            self.connection_label.config(text="Connected")
        else:
            self.connection_indicator.create_oval(2, 2, 10, 10, fill=ModernTheme.ERROR, outline='')
            self.connection_label.config(text="Not Connected")

    def send_test_email(self):
        """Send a test email"""
        try:
            self.send_notification("Test Email", "This is a test notification from Buffalo LinkStation Sync Manager.")
            messagebox.showinfo("Success", "Test email sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send test email:\n{str(e)}")

    def send_notification(self, subject, message):
        """Send email notification"""
        if not self.notifications_var.get():
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email_var.get()
            msg['To'] = self.to_email_var.get()
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(self.smtp_server_var.get(), int(self.smtp_port_var.get()))
            server.starttls()
            server.login(self.from_email_var.get(), self.email_password_var.get())
            server.send_message(msg)
            server.quit()

            self.log("Email notification sent", "SUCCESS")
        except Exception as e:
            self.log(f"Failed to send email: {str(e)}", "ERROR")

    def browse_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_var.set(folder)

    def browse_dest(self):
        folder = filedialog.askdirectory(title="Select Buffalo LinkStation Destination")
        if folder:
            self.dest_var.set(folder)
            threading.Thread(target=self.test_connection, daemon=True).start()

    def log(self, message, level="INFO"):
        """Log message to both log areas"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}\n"

        # Full log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message, level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

        # Mini log (dashboard)
        self.mini_log.config(state=tk.NORMAL)
        self.mini_log.insert(tk.END, log_message)
        self.mini_log.see(tk.END)
        # Keep mini log to last 50 lines
        if int(self.mini_log.index('end-1c').split('.')[0]) > 50:
            self.mini_log.delete(1.0, 2.0)
        self.mini_log.config(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def export_logs(self):
        """Export logs to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"nassync_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", "Logs exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export logs:\n{str(e)}")

    def update_stats(self):
        """Update dashboard statistics"""
        if hasattr(self, 'stat_cards'):
            if self.last_sync_time:
                self.stat_cards['last_sync'].config(
                    text=self.last_sync_time.strftime("%H:%M:%S")
                )

            if self.next_sync_time and self.auto_sync_active:
                self.stat_cards['next_sync'].config(
                    text=self.next_sync_time.strftime("%H:%M:%S")
                )
            elif not self.auto_sync_active:
                self.stat_cards['next_sync'].config(text="Not Scheduled")

        self.root.after(1000, self.update_stats)

    def validate_paths(self):
        source = self.source_var.get()
        dest = self.dest_var.get()

        if not source or not dest:
            messagebox.showerror("Error", "Please select both source and destination folders.")
            return False

        if not os.path.exists(source):
            messagebox.showerror("Error", f"Source folder does not exist:\n{source}")
            return False

        if not os.path.isdir(source):
            messagebox.showerror("Error", "Source must be a folder.")
            return False

        return True

    def sync_now(self):
        if not self.validate_paths():
            return

        if self.is_syncing:
            messagebox.showwarning("Warning", "Sync is already in progress.")
            return

        self.sync_thread = threading.Thread(target=self.run_sync, daemon=True)
        self.sync_thread.start()

    def run_sync(self):
        self.is_syncing = True
        self.sync_start_time = time.time()
        self.sync_now_btn.config(state=tk.DISABLED)
        self.auto_sync_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_text.config(text="Syncing in progress...")
        self.stat_cards['sync_status'].config(text="Syncing...",
                                             foreground=ModernTheme.ACCENT_PRIMARY)
        self.progress_var.set(0)

        if self.tray_icon:
            self.tray_icon.update_icon("syncing")
            self.tray_icon.update_tooltip("Syncing... 0%")

        result = None

        try:
            config = self.get_current_config()
            self.sync_engine = SyncEngine(config, self.log, self.update_progress)

            self.log("Starting sync operation to Buffalo LinkStation...", "INFO")
            result = self.sync_engine.sync()

            sync_duration = time.time() - self.sync_start_time
            result['duration'] = sync_duration

            if result['success']:
                self.log(f"Sync completed successfully!", "SUCCESS")
                self.log(f"Files copied: {result['copied']}, Updated: {result['updated']}, "
                        f"Deleted: {result['deleted']}, Errors: {result['errors']}", "INFO")
                self.status_text.config(text="Sync completed successfully!")
                self.stat_cards['sync_status'].config(text="Complete",
                                                     foreground=ModernTheme.SUCCESS)
                self.stat_cards['files_synced'].config(
                    text=str(result['copied'] + result['updated'])
                )
                self.last_sync_time = datetime.now()

                if self.tray_icon:
                    self.tray_icon.update_icon("success")
                    self.tray_icon.update_tooltip("Last sync: Success")
                    self.tray_icon.show_notification(
                        "Sync Completed",
                        f"Copied: {result['copied']}, Updated: {result['updated']}"
                    )

                if self.notifications_var.get():
                    self.send_notification(
                        "Sync Completed",
                        f"Buffalo LinkStation sync completed successfully!\n\n"
                        f"Copied: {result['copied']}\n"
                        f"Updated: {result['updated']}\n"
                        f"Deleted: {result['deleted']}\n"
                        f"Errors: {result['errors']}"
                    )
            else:
                self.log(f"Sync completed with errors", "ERROR")
                self.status_text.config(text="Sync completed with errors")
                self.stat_cards['sync_status'].config(text="Errors",
                                                     foreground=ModernTheme.ERROR)

                if self.tray_icon:
                    self.tray_icon.update_icon("error")
                    self.tray_icon.update_tooltip("Last sync: Failed")
                    self.tray_icon.show_notification(
                        "Sync Failed",
                        f"Errors: {result.get('errors', 0)}"
                    )

                if self.notifications_var.get():
                    self.send_notification(
                        "Sync Failed",
                        f"Buffalo LinkStation sync completed with errors. Please check the logs."
                    )

        except Exception as e:
            self.log(f"Sync error: {str(e)}", "ERROR")
            self.status_text.config(text=f"Error: {str(e)}")
            self.stat_cards['sync_status'].config(text="Failed",
                                                 foreground=ModernTheme.ERROR)

            if self.tray_icon:
                self.tray_icon.update_icon("error")
                self.tray_icon.update_tooltip("Last sync: Error")

            if result is None:
                result = {
                    'success': False,
                    'copied': 0,
                    'updated': 0,
                    'deleted': 0,
                    'errors': 1,
                    'skipped': 0,
                    'duration': time.time() - self.sync_start_time
                }

        finally:
            self.is_syncing = False
            self.sync_now_btn.config(state=tk.NORMAL)
            self.auto_sync_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.progress_var.set(100)

            if result:
                self.history_manager.add_entry(
                    self.source_var.get(),
                    self.dest_var.get(),
                    result
                )
                self.refresh_history()

            if self.tray_icon and not result.get('success'):
                self.tray_icon.update_icon("idle")
                self.tray_icon.update_tooltip("Ready")

    def toggle_auto_sync(self):
        if not self.auto_sync_active:
            if not self.validate_paths():
                return

            self.auto_sync_active = True
            self.auto_sync_btn.config(text="⏸ Stop Auto-Sync", bg=ModernTheme.WARNING)
            self.log("Auto-sync activated", "INFO")
            self.stat_cards['sync_status'].config(text="Auto-Sync Active",
                                                 foreground=ModernTheme.ACCENT_PRIMARY)

            self.auto_sync_thread = threading.Thread(target=self.auto_sync_loop, daemon=True)
            self.auto_sync_thread.start()
        else:
            self.auto_sync_active = False
            self.auto_sync_btn.config(text="▶ Start Auto-Sync", bg='#10B981')
            self.log("Auto-sync deactivated", "INFO")
            self.stat_cards['sync_status'].config(text="Ready",
                                                 foreground=ModernTheme.SUCCESS)
            self.next_sync_time = None

    def auto_sync_loop(self):
        while self.auto_sync_active:
            try:
                interval = int(self.interval_var.get()) * 60
            except ValueError:
                interval = 1800

            self.next_sync_time = datetime.now() + timedelta(seconds=interval)

            if not self.is_syncing:
                self.sync_now()

            for _ in range(interval):
                if not self.auto_sync_active:
                    break
                time.sleep(1)

    def stop_sync(self):
        if self.sync_engine:
            self.sync_engine.stop()
            self.log("Stop requested...", "WARNING")

    def update_progress(self, value):
        self.progress_var.set(value)
        self.progress_label.config(text=f"{int(value)}% Complete")

        if self.tray_icon and self.is_syncing:
            self.tray_icon.update_tooltip(f"Syncing... {int(value)}%")

    def get_current_config(self):
        return {
            'source': self.source_var.get(),
            'destination': self.dest_var.get(),
            'interval': int(self.interval_var.get()),
            'mode': self.sync_mode_var.get(),
            'include': self.include_var.get(),
            'exclude': self.exclude_var.get(),
            'verify': self.verify_var.get(),
            'subfolders': self.subfolders_var.get(),
            'bandwidth_limit': self.bandwidth_limit_var.get(),
            'bandwidth_value': int(self.bandwidth_value_var.get()) if self.bandwidth_limit_var.get() else None,
            'retention_enabled': self.retention_enabled_var.get(),
            'retention_days': int(self.retention_days_var.get()) if self.retention_enabled_var.get() else None,
            'smtp_server': self.smtp_server_var.get(),
            'smtp_port': self.smtp_port_var.get(),
            'from_email': self.from_email_var.get(),
            'to_email': self.to_email_var.get(),
            'email_password': self.email_password_var.get(),
            'notifications': self.notifications_var.get(),
            'scheduled_sync': self.scheduled_sync_var.get(),
            'schedule_times': self.schedule_times_var.get()
        }

    def save_config(self):
        config = self.get_current_config()
        self.config_manager.save_config(config)
        self.log("Configuration saved", "SUCCESS")
        messagebox.showinfo("Success", "Configuration saved successfully!")

    def load_config(self):
        config = self.config_manager.load_config()
        if config:
            self.source_var.set(config.get('source', ''))
            self.dest_var.set(config.get('destination', ''))
            self.interval_var.set(str(config.get('interval', 30)))
            self.sync_mode_var.set(config.get('mode', 'mirror'))
            self.include_var.set(config.get('include', '*'))
            self.exclude_var.set(config.get('exclude', '*.tmp,~*,.DS_Store,Thumbs.db'))
            self.verify_var.set(config.get('verify', True))
            self.subfolders_var.set(config.get('subfolders', True))
            self.bandwidth_limit_var.set(config.get('bandwidth_limit', False))
            self.bandwidth_value_var.set(str(config.get('bandwidth_value', 10)))
            self.retention_enabled_var.set(config.get('retention_enabled', False))
            self.retention_days_var.set(str(config.get('retention_days', 30)))
            self.smtp_server_var.set(config.get('smtp_server', 'smtp.gmail.com'))
            self.smtp_port_var.set(config.get('smtp_port', '587'))
            self.from_email_var.set(config.get('from_email', ''))
            self.to_email_var.set(config.get('to_email', ''))
            self.email_password_var.set(config.get('email_password', ''))
            self.notifications_var.set(config.get('notifications', False))
            self.scheduled_sync_var.set(config.get('scheduled_sync', False))
            self.schedule_times_var.set(config.get('schedule_times', '09:00,18:00'))
            self.log("Configuration loaded", "INFO")

            self.toggle_bandwidth()
            self.toggle_retention()

    def on_closing(self):
        """Handle window close event"""
        if self.minimize_to_tray and self.tray_icon and TRAY_AVAILABLE:
            self.root.withdraw()
            if self.tray_icon:
                self.tray_icon.show_notification(
                    "Still Running",
                    "Buffalo LinkStation Sync is running in the system tray"
                )
        else:
            self.quit_app()

    def quit_app(self):
        """Quit the application"""
        if self.is_syncing:
            result = messagebox.askyesno(
                "Sync in Progress",
                "A sync is currently in progress. Are you sure you want to quit?"
            )
            if not result:
                return

        if self.tray_icon:
            self.tray_icon.stop()

        self.root.quit()
        self.root.destroy()
        sys.exit(0)

def main():

    root = tk.Tk()
    app = NASyncApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

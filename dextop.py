#!/usr/bin/env python3
import os
import sys
import json
import re
import subprocess
import shutil
import threading
import time
import string
import random
import socket
try:
    import tkinter as tk
    import customtkinter as ctk
    from tkinter import messagebox
except ImportError as e:
    import subprocess
    print(f"❌ Error loading GUI libraries: {e}")
    print("\nIt looks like 'tkinter' is missing on your system.")
    
    pkg_manager = ""
    install_cmd = []
    if shutil.which("pacman"):
        pkg_manager = "pacman (Arch Linux)"
        install_cmd = ["sudo", "pacman", "-S", "--noconfirm", "tk"]
    elif shutil.which("apt-get"):
        pkg_manager = "apt (Debian/Ubuntu)"
        install_cmd = ["sudo", "apt", "install", "-y", "python3-tk"]
    elif shutil.which("dnf"):
        pkg_manager = "dnf (Fedora)"
        install_cmd = ["sudo", "dnf", "install", "-y", "python3-tkinter"]
        
    if install_cmd and sys.stdin and sys.stdin.isatty():
        try:
            ans = input(f"\nWould you like to automatically install the missing package via {pkg_manager}? [Y/n] ")
            if ans.lower() in ["", "y", "yes"]:
                print(f"Running: {' '.join(install_cmd)}")
                subprocess.run(install_cmd)
                print("\nInstallation finished! Please restart DeXtop Mode.")
            else:
                print("Please install it manually to use DeXtop Mode.")
        except EOFError:
            print("Please install your system's tkinter package manually to use DeXtop Mode.")
    else:
        print("Please install your system's tkinter package manually to use DeXtop Mode.")
    sys.exit(1)
from PIL import Image, ImageDraw
try:
    from PIL import ImageTk
except ImportError:
    ImageTk = None

try:
    import qrcode
except ImportError:
    qrcode = None

try:
    from zeroconf import ServiceBrowser, Zeroconf, ServiceStateChange
except ImportError:
    Zeroconf = None

__version__ = "1.0.26"

# Set styling theme
if sys.platform == "darwin":
    for extra_path in ["/opt/homebrew/bin", "/usr/local/bin", "/opt/homebrew/sbin"]:
        if os.path.exists(extra_path) and extra_path not in os.environ.get("PATH", ""):
            os.environ["PATH"] = extra_path + os.pathsep + os.environ.get("PATH", "")
elif sys.platform.startswith("win"):
    for extra_path in [
        os.path.expanduser("~\\.config\\dextop\\scrcpy"),
        "C:\\scrcpy",
        "C:\\ProgramData\\chocolatey\\bin",
        "C:\\scoop\\shims",
        os.path.expanduser("~\\AppData\\Local\\Microsoft\\WinGet\\Links")
    ]:
        if os.path.exists(extra_path) and extra_path not in os.environ.get("PATH", ""):
            os.environ["PATH"] = extra_path + os.pathsep + os.environ.get("PATH", "")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_DIR = os.path.expanduser("~/.config/dextop")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
ICON_FILE = os.path.join(CONFIG_DIR, "icon.png")
SYSTEM_ICON_FILE = "/usr/share/icons/hicolor/512x512/apps/dextop.png"

def get_app_icon_path():
    if os.path.exists(ICON_FILE):
        return ICON_FILE
    if os.path.exists(SYSTEM_ICON_FILE):
        return SYSTEM_ICON_FILE
    ensure_app_icon()
    if os.path.exists(ICON_FILE):
        return ICON_FILE
    return None

def ensure_app_icon():
    """Generates a premium custom icon for DeXtop Mode if it doesn't exist."""
    if os.path.exists(ICON_FILE):
        return
        
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        # Create a 512x512 canvas
        img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        
        # 1. Background with a beautiful dark slate-to-purple diagonal gradient
        # Using pixels.load() is significantly faster than putpixel() in a loop
        pixels = img.load()
        for y in range(512):
            for x in range(512):
                ratio = (x + y) / 1024.0
                pixels[x, y] = (
                    int(15 + 73 * ratio),
                    int(23 + 5 * ratio),
                    int(42 + 93 * ratio),
                    255
                )
                
        # Apply smooth rounded corners mask
        mask = Image.new("L", (512, 512), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([20, 20, 492, 492], radius=100, fill=255)
        img.putalpha(mask)
        
        draw = ImageDraw.Draw(img)
        # 2. Draw Monitor Outline (White)
        draw.rounded_rectangle([100, 110, 412, 310], radius=20, outline=(255, 255, 255, 255), width=16)
        # Monitor stand
        draw.rectangle([236, 310, 276, 360], fill=(255, 255, 255, 255))
        draw.rounded_rectangle([180, 360, 332, 385], radius=8, fill=(255, 255, 255, 255))
        
        # 3. Draw Smartphone Outline (Cyan overlay)
        draw.rounded_rectangle([310, 180, 420, 390], radius=15, fill=(15, 23, 42, 255), outline=(0, 240, 255, 255), width=12)
        # Smartphone elements
        draw.rounded_rectangle([345, 370, 385, 375], radius=2, fill=(0, 240, 255, 255))
        draw.ellipse([358, 192, 372, 206], fill=(0, 240, 255, 255))
        
        img.save(ICON_FILE)
        print(f"Custom icon generated at: {ICON_FILE}")
    except Exception as e:
        print(f"Could not generate app icon: {e}")

def ensure_desktop_shortcut():
    """Ensures a desktop menu entry exists in ~/.local/share/applications/ for pip/pipx/whl installs on Linux."""
    if not sys.platform.startswith("linux"):
        return
        
    user_apps_dir = os.path.expanduser("~/.local/share/applications")
    shortcut_path = os.path.join(user_apps_dir, "dextop.desktop")
    system_shortcut = "/usr/share/applications/dextop.desktop"
    
    try:
        os.makedirs(user_apps_dir, exist_ok=True)
        ensure_app_icon()
        icon_path = get_app_icon_path() or ICON_FILE
        
        # Hide default scrcpy icons from the user's application menu
        for scrcpy_name in ["scrcpy.desktop", "scrcpy-console.desktop"]:
            scrcpy_shortcut = os.path.join(user_apps_dir, scrcpy_name)
            if not os.path.exists(scrcpy_shortcut):
                with open(scrcpy_shortcut, "w") as f:
                    f.write(f"[Desktop Entry]\nType=Application\nName={scrcpy_name.replace('.desktop', '')}\nNoDisplay=true\n")
                    
        if os.path.exists(shortcut_path) or os.path.exists(system_shortcut):
            return
            
        exec_cmd = "dextop"
        if not shutil.which("dextop"):
            exec_cmd = f"{sys.executable} {os.path.abspath(__file__)}"
            
        content = f"""[Desktop Entry]
Version=1.0
Name=DeXtop Mode
Comment=Launch DeXtop Mode wrapper (Samsung DeX & Native Desktop)
Exec={exec_cmd}
Icon={icon_path}
Terminal=false
Type=Application
Categories=Utility;
StartupWMClass=dextop
"""
        with open(shortcut_path, "w") as f:
            f.write(content)
            
        if shutil.which("update-desktop-database"):
            subprocess.run(["update-desktop-database", user_apps_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Could not auto-create desktop shortcut: {e}")


class PairingDialog(ctk.CTkToplevel):
    def __init__(self, parent, default_ip=""):
        super().__init__(parent)
        self.parent = parent
        self.title("Wireless Pairing")
        self.geometry("400x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center relative to parent
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        self.geometry(f"+{parent_x + 120}+{parent_y + 40}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        
        ctk.CTkLabel(
            self, 
            text="Pair a New Device", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        
        ctk.CTkLabel(self, text="IP Address:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.entry_ip = ctk.CTkEntry(self, placeholder_text="192.168.x.x")
        self.entry_ip.insert(0, default_ip)
        self.entry_ip.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(self, text="Pairing Port:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.entry_port = ctk.CTkEntry(self, placeholder_text="e.g., 39361")
        self.entry_port.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(self, text="Pairing Code:").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.entry_code = ctk.CTkEntry(self, placeholder_text="6 digits")
        self.entry_code.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        
        self.btn_pair = ctk.CTkButton(
            self,
            text="Start Pairing",
            command=self.start_pairing
        )
        self.btn_pair.grid(row=4, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="ew")
        
        self.btn_qr = ctk.CTkButton(
            self,
            text="📷 Pair with QR Code instead",
            fg_color="#1a4f7a",
            hover_color="#246a9f",
            command=self.open_qr_pairing
        )
        self.btn_qr.grid(row=5, column=0, columnspan=2, padx=20, pady=(5, 15), sticky="ew")
        
        # Instructions Box inside the Dialog
        self.help_frame = ctk.CTkFrame(self, fg_color="#2b3b4c", corner_radius=8)
        self.help_frame.grid(row=6, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        help_text = (
            "📌 Where to find this information on Android?\n\n"
            "1. Go to Settings > Developer Options.\n"
            "2. Enable and click on 'Wireless debugging'.\n"
            "3. Select 'Pair device with pairing code' (or QR Code).\n"
            "4. Follow the on-screen instructions."
        )
        self.help_lbl = ctk.CTkLabel(
            self.help_frame,
            text=help_text,
            font=ctk.CTkFont(size=11),
            justify="left",
            wraplength=340
        )
        self.help_lbl.pack(padx=15, pady=10, fill="both")
        
    def open_qr_pairing(self):
        if qrcode is None or Zeroconf is None:
            messagebox.showerror("Missing Dependencies", "The 'qrcode' or 'zeroconf' python libraries are missing.\nPlease install them to use this feature.", parent=self)
            return
        self.destroy()
        QRPairingDialog(self.parent)

    def start_pairing(self):
        ip = self.entry_ip.get().strip()
        port = self.entry_port.get().strip()
        code = self.entry_code.get().strip()
        
        if not ip or not port or not code:
            messagebox.showerror("Error", "All fields must be filled.")
            return
            
        self.btn_pair.configure(text="Pairing in progress...", state="disabled")
        
        def run_pair():
            success, message = self.parent.run_adb_pair(ip, port, code)
            
            def on_done():
                self.btn_pair.configure(text="Start Pairing", state="normal")
                if success:
                    messagebox.showinfo("Success", "The device has been successfully paired!")
                    self.destroy()
                else:
                    messagebox.showerror("Pairing Failed", f"Pairing failed:\n\n{message}")
                    
            self.parent.after(0, on_done)
            
        threading.Thread(target=run_pair, daemon=True).start()


def _offer_install(manager_cmd, install_prompt, no_manager_msg, success_msg="Dependencies installed successfully!"):
    """Generic helper: proposes 1-click install via a package manager."""
    if shutil.which(manager_cmd[0]):
        if messagebox.askyesno("Missing Dependencies", install_prompt):
            try:
                subprocess.run(manager_cmd, check=True)
                messagebox.showinfo("Success", success_msg)
                return True
            except Exception as e:
                messagebox.showerror("Installation Error", f"Failed to install dependencies: {e}")
                return False
    else:
        messagebox.showwarning("Missing Dependencies", no_manager_msg)
    return False


def check_and_install_dependencies():
    """Checks if scrcpy or adb is missing and offers 1-click auto-installation."""
    missing = []
    if not shutil.which("scrcpy") and not shutil.which("scrcpy.exe"):
        missing.append("scrcpy")
    if not shutil.which("adb") and not shutil.which("adb.exe"):
        missing.append("adb")

    if not missing:
        return True

    missing_str = ", ".join(missing)

    if sys.platform.startswith("win"):
        return _offer_install(
            ["winget", "install", "Genymobile.scrcpy",
             "--accept-source-agreements", "--accept-package-agreements"],
            f"The following required dependencies are missing: {missing_str}.\n\n"
            "Would you like DeXtop Mode to automatically install scrcpy via Winget now?",
            f"The following required dependencies are missing: {missing_str}.\n\n"
            "Please install scrcpy from https://github.com/Genymobile/scrcpy or via Chocolatey / Scoop.",
            "Dependencies installed successfully! Please restart DeXtop Mode."
        )

    if sys.platform == "darwin":
        return _offer_install(
            ["brew", "install", "scrcpy", "android-platform-tools"],
            f"The following required dependencies are missing: {missing_str}.\n\n"
            "Would you like DeXtop Mode to automatically install them via Homebrew now?",
            f"The following required dependencies are missing: {missing_str}.\n\n"
            "Please install Homebrew (https://brew.sh) or run:\nbrew install scrcpy android-platform-tools"
        )
    if sys.platform.startswith("linux"):
        cmd = None
        if shutil.which("pacman"):
            cmd = ["pkexec", "pacman", "-S", "--noconfirm", "scrcpy", "android-tools"]
        elif shutil.which("apt-get"):
            cmd = ["pkexec", "apt", "install", "-y", "scrcpy", "adb"]
        elif shutil.which("dnf"):
            cmd = ["pkexec", "dnf", "install", "-y", "scrcpy", "android-tools"]
            
        if cmd and shutil.which("pkexec"):
            return _offer_install(
                cmd,
                f"The following required dependencies are missing: {missing_str}.\n\n"
                "Would you like DeXtop Mode to automatically install them now? (Requires administrator password)",
                f"The following required dependencies are missing: {missing_str}.\n\n"
                "Please install them via your system package manager."
            )
        else:
            messagebox.showwarning("Missing Dependencies", f"The following required dependencies are missing: {missing_str}.\n\nPlease install 'scrcpy' and 'adb' via your package manager to use DeXtop Mode.")
            return False

    return False

class QRPairingDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Pair via QR Code")
        self.geometry("380x550")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center relative to parent
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        self.geometry(f"+{parent_x + 100}+{parent_y + 20}")

        # Generate Password
        self.password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        try:
            self.service_name = socket.gethostname()
        except Exception:
            self.service_name = "DeXify"

        ctk.CTkLabel(
            self, 
            text="Scan to Pair", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 10))

        # Create QR Code Image
        if qrcode is None:
            ctk.CTkLabel(self, text="qrcode library not installed.").pack(pady=20)
            return
            
        qr_data = f"WIFI:T:ADB;S:{self.service_name};P:{self.password};;"
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        self.qr_photo = ImageTk.PhotoImage(img)
        self.qr_label = ctk.CTkLabel(self, image=self.qr_photo, text="")
        self.qr_label.pack(pady=10)
        
        self.status_lbl = ctk.CTkLabel(
            self,
            text="Waiting for device to scan...",
            font=ctk.CTkFont(weight="bold"),
            text_color="orange"
        )
        self.status_lbl.pack(pady=(0, 10))
        
        self.info_lbl = ctk.CTkLabel(
            self, 
            text="1. On your phone, go to Settings > Developer Options\n2. Open 'Wireless debugging'\n3. Select 'Pair device with QR code'\n4. Scan the code above",
            justify="left"
        )
        self.info_lbl.pack(pady=10)

        # Setup Zeroconf
        self.zeroconf = None
        self.browser = None
        try:
            if Zeroconf:
                self.zeroconf = Zeroconf()
                self.browser = ServiceBrowser(self.zeroconf, "_adb-tls-pairing._tcp.local.", handlers=[self.on_service_state_change])
        except Exception as e:
            print(f"Failed to start mDNS listener: {e}")
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                addresses = info.parsed_addresses()
                if addresses:
                    ip = addresses[0]
                    port = info.port
                    print(f"Discovered ADB pairing service at {ip}:{port}")
                    self.after(0, lambda: self.status_lbl.configure(text=f"Pairing with {ip}:{port}...", text_color="cyan"))
                    
                    # Run pairing in a separate thread to avoid blocking the zeroconf handler
                    def pair_thread():
                        success, msg = self.parent.run_adb_pair(ip, port, self.password)
                        if success:
                            self.after(0, lambda: messagebox.showinfo("Success", "Device paired successfully via QR code!"))
                            self.after(0, self.on_close)
                        else:
                            self.after(0, lambda: self.status_lbl.configure(text="Pairing failed.", text_color="red"))
                            self.after(0, lambda: messagebox.showerror("Pairing Failed", f"Failed to pair:\n{msg}"))
                    
                    threading.Thread(target=pair_thread, daemon=True).start()
                        
    def on_close(self):
        try:
            if self.zeroconf:
                self.zeroconf.close()
        except Exception:
            pass
        self.destroy()

class DeXtopModeApp(ctk.CTk):
    def __init__(self):
        super().__init__(className="dextop")
        
        self.title("DeXtop Mode")
        self.geometry("660x650")
        self.resizable(False, False)
        
        # App state
        self.connected_device = None
        self.dex_process = None
        self.old_timeout = None
        self.is_connecting = False
        self.sinks_map = {}  # Initialized early to avoid AttributeError before refresh completes
        
        # Check dependencies on launch
        check_and_install_dependencies()
        
        # Load config
        self.config = self.load_config()
        
        # Auto-ensure desktop shortcut for pip/pipx/whl installs
        ensure_desktop_shortcut()
        
        # Set window and taskbar icon
        icon_path = get_app_icon_path()
        if icon_path:
            try:
                icon_img = ImageTk.PhotoImage(file=icon_path)
                self.wm_iconphoto(True, icon_img)
                self._icon_img = icon_img
            except Exception as e:
                print(f"Could not set window icon: {e}")
        
        # UI Setup
        self.setup_ui()
        
        # Start background device monitoring
        self.stop_monitor = False
        self.monitor_thread = threading.Thread(target=self.monitor_devices, daemon=True)
        self.monitor_thread.start()
        
        # Load initial audio devices
        self.refresh_audio_devices()
        
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "last_ip": "",
            "last_port": "",
            "timeout_handling": True,
            "selected_sink": "",
            "mouse_uhid": False,
            "keyboard_uhid": False,
            "fix_oneui_gestures": True,
            "display_mode": "Secondary Display (DeX)",
            "display_dpi": "160"
        }
        
    def save_config(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def setup_ui(self):
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title
        self.grid_rowconfigure(1, weight=1) # Content
        self.grid_rowconfigure(2, weight=0) # Action button
        
        # 1. Header / Title
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.title_box = ctk.CTkFrame(self.title_frame, fg_color="transparent")
        self.title_box.pack(side="left", anchor="w")

        self.title_label = ctk.CTkLabel(
            self.title_box, 
            text="DeXtop Mode", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(anchor="w")

        self.version_label = ctk.CTkLabel(
            self.title_box,
            text=f"v{__version__}",
            font=ctk.CTkFont(size=11, weight="normal"),
            text_color="#8899a6"
        )
        self.version_label.pack(anchor="w")
        
        self.status_indicator = ctk.CTkLabel(
            self.title_frame,
            text="● Disconnected",
            text_color="#ff5555",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_indicator.pack(side="right", padx=10)

        # 2. Main content tab/frame
        self.content_frame = ctk.CTkTabview(self)
        self.content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.tab_conn = self.content_frame.add("Connection")
        self.tab_audio = self.content_frame.add("Audio")
        self.tab_settings = self.content_frame.add("Settings")
        
        self.setup_connection_tab()
        self.setup_audio_tab()
        self.setup_settings_tab()
        
        # 3. Launch Button
        self.btn_launch = ctk.CTkButton(
            self,
            text="Start DeX",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            command=self.toggle_dex,
            state="disabled"
        )
        self.btn_launch.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

    def setup_connection_tab(self):
        self.tab_conn.columnconfigure(0, weight=1)
        self.tab_conn.columnconfigure(1, weight=1)
        
        # Instruction Banner / Tooltip
        self.instr_banner = ctk.CTkFrame(self.tab_conn, fg_color="#2b3b4c", corner_radius=8)
        self.instr_banner.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        instr_text = (
            "💡 Important instructions:\n"
            "1. Enable USB/Wireless debugging in your phone's Developer Options.\n"
            "2. Unlock your phone screen during the initial DeX launch."
        )
        self.instr_lbl = ctk.CTkLabel(
            self.instr_banner,
            text=instr_text,
            font=ctk.CTkFont(size=12, weight="normal"),
            justify="left",
            wraplength=520
        )
        self.instr_lbl.pack(padx=15, pady=10, fill="both")
        
        # Wi-Fi Setup Form
        self.wifi_group = ctk.CTkFrame(self.tab_conn)
        self.wifi_group.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.wifi_group.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.wifi_group, text="Phone IP:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_ip = ctk.CTkEntry(self.wifi_group, placeholder_text="192.168.x.x")
        self.entry_ip.insert(0, self.config.get("last_ip", ""))
        self.entry_ip.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(self.wifi_group, text="Port:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_port = ctk.CTkEntry(self.wifi_group, placeholder_text="5555")
        self.entry_port.insert(0, self.config.get("last_port", ""))
        self.entry_port.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Action Buttons
        self.btn_connect = ctk.CTkButton(
            self.tab_conn,
            text="Connect over Wi-Fi",
            command=self.connect_wifi
        )
        self.btn_connect.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.btn_disconnect = ctk.CTkButton(
            self.tab_conn,
            text="Disconnect",
            fg_color="#444444",
            hover_color="#555555",
            command=self.disconnect_all
        )
        self.btn_disconnect.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Wireless Pairing Button
        self.btn_pair_open = ctk.CTkButton(
            self.tab_conn,
            text="Pair a New Device",
            fg_color="#1a4f7a",
            hover_color="#246a9f",
            command=self.open_pairing_dialog
        )
        self.btn_pair_open.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")


        # Current device details
        self.lbl_device_details = ctk.CTkLabel(
            self.tab_conn,
            text="No device detected.",
            text_color="gray"
        )
        self.lbl_device_details.grid(row=5, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

    def setup_audio_tab(self):
        self.tab_audio.columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.tab_audio, 
            text="Select audio output for DeX:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.audio_dropdown = ctk.CTkOptionMenu(
            self.tab_audio,
            values=["Default"],
            command=self.on_audio_selected
        )
        self.audio_dropdown.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.btn_refresh_audio = ctk.CTkButton(
            self.tab_audio,
            text="Refresh Devices",
            command=self.refresh_audio_devices
        )
        self.btn_refresh_audio.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Audio redirection explanation
        info_txt = (
            "DeXtop Mode uses PipeWire to redirect audio.\n"
            "Changing the device here will update the default system output during the DeX session."
        )
        ctk.CTkLabel(
            self.tab_audio,
            text=info_txt,
            font=ctk.CTkFont(size=12, slant="italic"),
            justify="left"
        ).grid(row=3, column=0, padx=10, pady=20, sticky="w")

    def setup_settings_tab(self):
        self.tab_settings.columnconfigure(0, weight=1)
        
        # Display Mode Option
        ctk.CTkLabel(
            self.tab_settings,
            text="Display Mode:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")
        
        self.opt_display_mode = ctk.CTkOptionMenu(
            self.tab_settings,
            values=["Secondary Display (DeX)", "Main Display Mirroring"],
            command=lambda _: self.on_settings_changed()
        )
        saved_mode = self.config.get("display_mode", "Secondary Display (DeX)")
        self.opt_display_mode.set(saved_mode)
        self.opt_display_mode.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # DPI Option for Secondary Display
        ctk.CTkLabel(
            self.tab_settings,
            text="DeX Display Scale (DPI):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=2, column=0, padx=10, pady=(5, 2), sticky="w")

        self.opt_dpi = ctk.CTkOptionMenu(
            self.tab_settings,
            values=["160 (Desktop Standard)", "200 (Medium Scale)", "240 (Large Scale)"],
            command=lambda _: self.on_settings_changed()
        )
        saved_dpi = self.config.get("display_dpi", "160")
        matched_dpi = [v for v in ["160 (Desktop Standard)", "200 (Medium Scale)", "240 (Large Scale)"] if saved_dpi in v]
        self.opt_dpi.set(matched_dpi[0] if matched_dpi else "160 (Desktop Standard)")
        self.opt_dpi.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Screen timeout switch
        self.switch_timeout = ctk.CTkSwitch(
            self.tab_settings,
            text="Manage automatic anti-sleep (screen_off_timeout)",
            command=self.on_settings_changed
        )
        if self.config.get("timeout_handling", True):
            self.switch_timeout.select()
        else:
            self.switch_timeout.deselect()
        self.switch_timeout.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        # One UI gesture repair switch
        self.switch_fix_gestures = ctk.CTkSwitch(
            self.tab_settings,
            text="Auto-restart One UI Launcher on exit (Fixes Back gesture)",
            command=self.on_settings_changed
        )
        if self.config.get("fix_oneui_gestures", True):
            self.switch_fix_gestures.select()
        else:
            self.switch_fix_gestures.deselect()
        self.switch_fix_gestures.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        
        # Manual One UI repair button directly under the switch
        self.btn_repair_gestures = ctk.CTkButton(
            self.tab_settings,
            text="🔄 Repair One UI Gestures Now",
            command=self.manual_repair_gestures,
            fg_color="#1a4f7a",
            hover_color="#246a9f"
        )
        self.btn_repair_gestures.grid(row=6, column=0, padx=10, pady=8, sticky="ew")

        # Mouse lock (UHID) switch
        self.switch_mouse = ctk.CTkSwitch(
            self.tab_settings,
            text="Capture mouse inside DeX window (UHID Mode)",
            command=self.on_settings_changed
        )
        if self.config.get("mouse_uhid", False):
            self.switch_mouse.select()
        else:
            self.switch_mouse.deselect()
        self.switch_mouse.grid(row=7, column=0, padx=10, pady=5, sticky="w")

        # Keyboard lock (UHID) switch
        self.switch_keyboard = ctk.CTkSwitch(
            self.tab_settings,
            text="Capture keyboard inside DeX window (UHID Mode)",
            command=self.on_settings_changed
        )
        if self.config.get("keyboard_uhid", False):
            self.switch_keyboard.select()
        else:
            self.switch_keyboard.deselect()
        self.switch_keyboard.grid(row=8, column=0, padx=10, pady=5, sticky="w")

        # Info note about UHID mode release keys
        uhid_info = (
            "💡 In physical capture mode (UHID):\n"
            "• Your mouse/keyboard behave as if plugged directly into the phone.\n"
            "• Press Left Alt or Super (Windows key) to release the cursor."
        )
        uhid_lbl = ctk.CTkLabel(
            self.tab_settings,
            text=uhid_info,
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#8899a6",
            justify="left",
            wraplength=520
        )
        uhid_lbl.grid(row=9, column=0, padx=10, pady=8, sticky="w")

        # Info note about hidden scrcpy shortcut
        info_lbl = ctk.CTkLabel(
            self.tab_settings,
            text="Note: The Scrcpy application is hidden in your menus to avoid visual clutter.",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="gray",
            justify="left",
            wraplength=500
        )
        info_lbl.grid(row=10, column=0, padx=10, pady=(5, 0), sticky="w")

    # --- DEVICE MONITORING & CONNECTION ---
    def monitor_devices(self):
        while not self.stop_monitor:
            if not self.is_connecting:
                devices = self.get_adb_devices()
                if devices:
                    # Select first active device
                    self.connected_device = devices[0]
                    self.connected_device_name = self.get_device_model(self.connected_device)
                    self.update_status(True, f"Connected: {self.connected_device}")
                else:
                    self.connected_device = None
                    self.connected_device_name = None
                    self.update_status(False, "Disconnected")
            time.sleep(2.5)
            
    def get_adb_devices(self):
        try:
            output = subprocess.check_output(["adb", "devices"]).decode("utf-8")
            devices = []
            lines = output.splitlines()
            for line in lines[1:]:
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    devices.append(parts[0])
            return devices
        except Exception:
            return []

    def get_device_model(self, device_id):
        try:
            # Try getting the user-assigned device name first
            name = subprocess.check_output(
                ["adb", "-s", device_id, "shell", "settings", "get", "global", "device_name"], 
                stderr=subprocess.STDOUT,
                timeout=2
            ).decode("utf-8").strip()
            
            if name and name.lower() != "null":
                return name
                
            # Fallback to product model
            output = subprocess.check_output(
                ["adb", "-s", device_id, "shell", "getprop", "ro.product.model"], 
                stderr=subprocess.STDOUT,
                timeout=2
            ).decode("utf-8").strip()
            if output:
                return output
        except Exception:
            pass
        return device_id

    def update_status(self, connected, text):
        def gui_update():
            if connected:
                self.status_indicator.configure(text=f"● {text}", text_color="#55ff55")
                name_display = getattr(self, 'connected_device_name', self.connected_device) or self.connected_device
                self.lbl_device_details.configure(
                    text=f"Connected device: {name_display}", 
                    text_color="#55ff55"
                )
                # Auto fill IP and Port entries if connected over Wi-Fi
                if ":" in str(self.connected_device):
                    try:
                        parts = str(self.connected_device).split(":")
                        ip, port = parts[0], parts[1]
                        if not self.entry_ip.get().strip():
                            self.entry_ip.insert(0, ip)
                        if not self.entry_port.get().strip():
                            self.entry_port.insert(0, port)
                    except Exception:
                        pass

                if self.dex_process is None:
                    self.btn_launch.configure(state="normal", text="Start DeX", fg_color=["#3B8ED0", "#1F6AA5"])
            else:
                self.status_indicator.configure(text="● Disconnected", text_color="#ff5555")
                self.lbl_device_details.configure(
                    text="No device detected. Plug in USB or connect over Wi-Fi.",
                    text_color="gray"
                )
                self.btn_launch.configure(state="disabled", text="Waiting for device...")
        self.after(0, gui_update)

    def connect_wifi(self):
        ip = self.entry_ip.get().strip()
        port = self.entry_port.get().strip()
        
        if not ip or not port:
            messagebox.showerror("Input Error", "Please enter the wireless debugging IP and port.")
            return
            
        self.is_connecting = True
        self.status_indicator.configure(text="● Connecting...", text_color="orange")
        self.lbl_device_details.configure(text=f"Attempting connection to {ip}:{port}...", text_color="orange")
        
        # Save to config
        self.config["last_ip"] = ip
        self.config["last_port"] = port
        self.save_config()
        
        def run_connect():
            try:
                # Ensure ADB server is running
                subprocess.run(["adb", "start-server"], check=True)
                
                # Attempt connection
                cmd = ["adb", "connect", f"{ip}:{port}"]
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if "connected to" in result.stdout:
                    # Give some time for ADB to register the device
                    time.sleep(1)
                    devices = self.get_adb_devices()
                    target = f"{ip}:{port}"
                    matched = [d for d in devices if target in d or d.startswith(ip)]
                    if matched:
                        self.connected_device = matched[0]
                        self.connected_device_name = self.get_device_model(self.connected_device)
                        self.update_status(True, f"Connected over Wi-Fi: {self.connected_device}")
                    else:
                        self.connected_device = target
                        self.connected_device_name = self.get_device_model(self.connected_device)
                        self.update_status(True, f"Connected: {target}")
                else:
                    self.after(0, lambda: messagebox.showerror(
                        "Connection Failed", 
                        f"Unable to connect: {result.stdout.strip()}"
                    ))
                    self.connected_device = None
                    self.update_status(False, "Disconnected")
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"ADB Error: {str(e)}"))
                self.connected_device = None
                self.update_status(False, "Disconnected")
            finally:
                self.is_connecting = False
                
        threading.Thread(target=run_connect, daemon=True).start()

    def disconnect_all(self):
        def run_disconnect():
            try:
                subprocess.run(["adb", "disconnect"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.connected_device = None
                self.update_status(False, "Disconnected")
            except Exception:
                pass
        threading.Thread(target=run_disconnect, daemon=True).start()

    # --- PAIRING DIALOG TRIGGERS ---
    def open_pairing_dialog(self):
        default_ip = self.entry_ip.get().strip() or self.config.get("last_ip", "")
        PairingDialog(self, default_ip)

    def run_adb_pair(self, ip, port, code):
        try:
            # Ensure ADB server is running
            subprocess.run(["adb", "start-server"], check=True)
            
            cmd = ["adb", "pair", f"{ip}:{port}"]
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Input the pairing code on stdin
            stdout, stderr = proc.communicate(input=f"{code}\n", timeout=12)
            
            if "Successfully paired" in stdout or proc.returncode == 0:
                # Update main IP input
                self.config["last_ip"] = ip
                self.save_config()
                self.after(0, lambda: self.entry_ip.delete(0, tk.END))
                self.after(0, lambda: self.entry_ip.insert(0, ip))
                return True, stdout
            else:
                return False, stdout + "\n" + stderr
        except Exception as e:
            return False, str(e)

    # --- AUDIO MANAGEMENT ---
    def refresh_audio_devices(self):
        # wpctl / PipeWire is Linux-only; skip silently on macOS and Windows
        if not sys.platform.startswith("linux"):
            self.sinks_map = {}
            self.after(0, lambda: (
                self.audio_dropdown.configure(values=["Default (system)", "Phone Only (No Audio Forwarding)"]),
                self.audio_dropdown.set(self.config.get("selected_sink", "Default (system)") if self.config.get("selected_sink", "") in ["Default (system)", "Phone Only (No Audio Forwarding)"] else "Default (system)")
            ))
            return

        def run_refresh():
            try:
                output = subprocess.check_output(["wpctl", "status"]).decode("utf-8")
                sinks = {}
                lines = output.splitlines()
                in_sinks = False
                for line in lines:
                    if "Sinks:" in line:
                        in_sinks = True
                        continue
                    if in_sinks:
                        # End of sinks section checks
                        if "├─" in line or "└─" in line or line.strip() == "" or "Sources:" in line:
                            if not ("Sinks:" in line or "│" in line):
                                in_sinks = False
                                continue
                        # Parse Sink entry
                        match = re.search(r"(\d+)\.\s+(.*?)(?:\s+\[vol:|\s*$)", line)
                        if match:
                            sink_id = match.group(1)
                            sink_name = match.group(2).strip()
                            sinks[sink_name] = sink_id
                
                self.sinks_map = sinks
                values = ["Default", "Phone Only (No Audio Forwarding)"] + list(sinks.keys())
                
                # Update dropdown safely
                def update_dropdown():
                    self.audio_dropdown.configure(values=values)
                    # Restore previous selection if valid
                    saved_sink = self.config.get("selected_sink", "")
                    if saved_sink in values:
                        self.audio_dropdown.set(saved_sink)
                    else:
                        self.audio_dropdown.set("Default")
                self.after(0, update_dropdown)
            except Exception as e:
                print(f"Error listing audio devices: {e}")
                self.sinks_map = {}
                self.after(0, lambda: (self.audio_dropdown.configure(values=["Default", "Phone Only (No Audio Forwarding)"]), self.audio_dropdown.set("Default")))
                
        threading.Thread(target=run_refresh, daemon=True).start()

    def on_audio_selected(self, choice):
        self.config["selected_sink"] = choice
        self.save_config()
        # Apply immediately via wpctl on Linux only
        if sys.platform.startswith("linux") and choice not in ("Default", "Default (system)", "Phone Only (No Audio Forwarding)") and choice in self.sinks_map:
            sink_id = self.sinks_map[choice]
            try:
                subprocess.run(["wpctl", "set-default", str(sink_id)])
            except Exception as e:
                print(f"Failed to change default sink: {e}")

    # --- SETTINGS ---
    def on_settings_changed(self):
        self.config["timeout_handling"] = self.switch_timeout.get() == 1
        self.config["fix_oneui_gestures"] = self.switch_fix_gestures.get() == 1
        self.config["mouse_uhid"] = self.switch_mouse.get() == 1
        self.config["keyboard_uhid"] = self.switch_keyboard.get() == 1
        self.config["display_mode"] = self.opt_display_mode.get()
        raw_dpi = self.opt_dpi.get()
        self.config["display_dpi"] = raw_dpi.split()[0] if raw_dpi else "160"
        self.save_config()

    def repair_gestures_adb(self, device=None):
        target_device = device or self.connected_device
        if not target_device:
            return False, "No device connected."
        try:
            # 1. Reset force_desktop_mode setting to 0 (crucial: exits external display mode lock)
            subprocess.run(["adb", "-s", target_device, "shell", "settings", "put", "global", "force_desktop_mode_on_external_displays", "0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 2. Stop Samsung DeX desktop mode service if active
            subprocess.run(["adb", "-s", target_device, "shell", "am", "stop-service", "-a", "com.sec.android.desktopmode.action.STOP_DESKTOP_MODE"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 3. Wake screen if off
            subprocess.run(["adb", "-s", target_device, "shell", "input", "keyevent", "KEYCODE_WAKEUP"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 4. Force-stop Samsung One UI Home launcher (restarts launcher & rebinds navigation in < 1s)
            subprocess.run(["adb", "-s", target_device, "shell", "am", "force-stop", "com.sec.android.app.launcher"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return True, "One UI Launcher successfully restarted!"
        except Exception as e:
            return False, f"Failed to repair gestures: {str(e)}"

    def manual_repair_gestures(self):
        if not self.connected_device:
            messagebox.showwarning("No Device", "Please connect a device first.")
            return
            
        if not messagebox.askyesno("Warning", "⚠️ ONLY use this if your phone's gestures are currently broken (e.g. after a DeX crash).\n\nIf your gestures are working fine, using this manual repair will actually break them!\n\nAre you sure you want to proceed?"):
            return
            
        def do_repair():
            success, msg = self.repair_gestures_adb()
            if success:
                self.after(0, lambda: messagebox.showinfo("Gestures Repaired", f"Success:\n{msg}"))
            else:
                self.after(0, lambda: messagebox.showerror("Repair Failed", f"Error:\n{msg}"))
                
        threading.Thread(target=do_repair, daemon=True).start()

    # --- DEX LIFECYCLE MANAGEMENT ---
    def toggle_dex(self):
        if self.dex_process is None:
            self.start_dex()
        else:
            self.stop_dex()

    def start_dex(self):
        if not self.connected_device:
            return
            
        self.btn_launch.configure(text="Starting up...", state="disabled")
        
        # Read parameters
        device = self.connected_device
        handle_timeout = self.config.get("timeout_handling", True)
        selected_audio = self.audio_dropdown.get()
        
        # Audio redirect via wpctl (Linux / PipeWire only)
        if sys.platform.startswith("linux") and selected_audio not in ("Default", "Default (system)", "Phone Only (No Audio Forwarding)") and selected_audio in self.sinks_map:
            sink_id = self.sinks_map[selected_audio]
            try:
                subprocess.run(["wpctl", "set-default", str(sink_id)])
            except Exception as e:
                print(f"Failed to set audio sink before startup: {e}")

        def run_session():
            try:
                # 1. Anti-veille (Save and disable screen timeout)
                if handle_timeout:
                    try:
                        self.old_timeout = subprocess.check_output(
                            ["adb", "-s", device, "shell", "settings", "get", "system", "screen_off_timeout"]
                        ).decode("utf-8").strip()
                        
                        if not self.old_timeout or self.old_timeout == "null":
                            self.old_timeout = "60000"
                            
                        # Disable timeout (~24 days)
                        subprocess.run(
                            ["adb", "-s", device, "shell", "settings", "put", "system", "screen_off_timeout", "2147483647"],
                            check=True
                        )
                    except Exception as e:
                        print(f"Could not adjust screen timeout: {e}")
                        self.old_timeout = None

                # 2. Hide window for invisibility while using DeX
                self.after(0, self.withdraw)

                # 3. Launch Scrcpy
                display_mode = self.config.get("display_mode", "Secondary Display (DeX)")
                dpi = self.config.get("display_dpi", "160")

                # Build arguments based on user config
                scrcpy_cmd = [
                    "scrcpy", 
                    "-s", device, 
                    "--turn-screen-off", 
                    "--stay-awake", 
                    "--disable-screensaver"
                ]

                if selected_audio == "Phone Only (No Audio Forwarding)":
                    scrcpy_cmd.append("--no-audio")
                else:
                    scrcpy_cmd.append("--audio-codec=aac")

                if shutil.which("systemd-inhibit"):
                    cmd = ["systemd-inhibit", "--what=idle", "--who=DeXtop Mode", "--why=Using desktop mode"] + scrcpy_cmd
                else:
                    cmd = scrcpy_cmd

                if display_mode == "Secondary Display (DeX)":
                    cmd.append(f"--new-display=1920x1080/{dpi}")

                # Check mouse capture option
                if self.config.get("mouse_uhid", False):
                    cmd.append("--mouse=uhid")
                # Check keyboard capture option
                if self.config.get("keyboard_uhid", False):
                    cmd.append("--keyboard=uhid")
                
                # Execute in the background synchronously in this thread
                self.dex_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # Update button in GUI
                self.after(0, lambda: self.btn_launch.configure(
                    text="Stop DeX", 
                    state="normal", 
                    fg_color="#ff5555", 
                    hover_color="#ff3333"
                ))
                
                # Wait for scrcpy to exit
                self.dex_process.wait()
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("DeX Error", f"Error during launch: {str(e)}"))
            finally:
                # Cleanup
                self.dex_process = None
                
                # Restore phone timeout
                if handle_timeout and self.old_timeout and self.connected_device:
                    try:
                        subprocess.run(
                            ["adb", "-s", device, "shell", "settings", "put", "system", "screen_off_timeout", self.old_timeout],
                            check=True
                        )
                    except Exception as e:
                        print(f"Could not restore timeout: {e}")
                self.old_timeout = None

                # Auto-repair One UI gesture navigation on exit (only in Secondary Display DeX mode)
                if display_mode == "Secondary Display (DeX)" and self.config.get("fix_oneui_gestures", True) and device:
                    try:
                        self.repair_gestures_adb(device)
                    except Exception as e:
                        print(f"Could not repair gestures: {e}")
                
                # Restore DeXtop Mode window and reset launch button state
                self.after(0, self.deiconify)
                self.after(0, lambda: self.btn_launch.configure(
                    text="Start DeX", 
                    fg_color=["#3B8ED0", "#1F6AA5"],
                    hover_color=["#2B72A5", "#144870"]
                ))
                
        threading.Thread(target=run_session, daemon=True).start()

    def stop_dex(self):
        if self.dex_process:
            try:
                self.dex_process.terminate()
            except Exception:
                pass

    def on_closing(self):
        self.stop_monitor = True
        self.stop_dex()
        self.destroy()

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--uninstall", "-u", "uninstall"):
        print("Uninstalling DeXtop Mode user shortcuts & config...")

        # --- Linux: remove .desktop shortcut ---
        if sys.platform.startswith("linux"):
            shortcut_path = os.path.expanduser("~/.local/share/applications/dextop.desktop")
            if os.path.exists(shortcut_path):
                try:
                    os.remove(shortcut_path)
                    print(f"Removed {shortcut_path}")
                except Exception as e:
                    print(f"Could not remove {shortcut_path}: {e}")
            if shutil.which("update-desktop-database"):
                subprocess.run(
                    ["update-desktop-database", os.path.expanduser("~/.local/share/applications/")],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )

        # --- macOS: remove app bundle from /Applications if present ---
        elif sys.platform == "darwin":
            app_path = "/Applications/dextop-mode.app"
            if os.path.exists(app_path):
                try:
                    shutil.rmtree(app_path)
                    print(f"Removed {app_path}")
                except Exception as e:
                    print(f"Could not remove {app_path}: {e}\nTry: sudo rm -rf /Applications/dextop-mode.app")
            else:
                print("No system app bundle found in /Applications (was it installed via pipx/pip?).")

        # --- Windows: remove Start Menu shortcut if present ---
        elif sys.platform.startswith("win"):
            start_menu = os.path.join(
                os.environ.get("APPDATA", ""),
                "Microsoft", "Windows", "Start Menu", "Programs", "dextop-mode.lnk"
            )
            if os.path.exists(start_menu):
                try:
                    os.remove(start_menu)
                    print(f"Removed {start_menu}")
                except Exception as e:
                    print(f"Could not remove {start_menu}: {e}")
            else:
                print("No Start Menu shortcut found.")

        # --- All platforms: remove config directory ---
        config_dir = CONFIG_DIR
        if os.path.exists(config_dir):
            try:
                shutil.rmtree(config_dir)
                print(f"Removed config directory: {config_dir}")
            except Exception as e:
                print(f"Could not remove {config_dir}: {e}")

        print("DeXtop Mode cleanup completed successfully.")
        return

    app = DeXtopModeApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()


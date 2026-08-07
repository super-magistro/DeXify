#!/usr/bin/env python3
import os
import sys
import json
import re
import subprocess
import threading
import time
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageTk

# Set styling theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_DIR = os.path.expanduser("~/.config/dextop")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
ICON_FILE = os.path.join(CONFIG_DIR, "icon.png")

def ensure_app_icon():
    """Generates a premium custom icon for DeXtop Mode if it doesn't exist."""
    if os.path.exists(ICON_FILE):
        return
        
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        # Create a 512x512 canvas
        img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        
        # 1. Background with a beautiful dark slate-to-purple diagonal gradient
        for y in range(512):
            for x in range(512):
                ratio = (x + y) / 1024.0
                r = int(15 + (88 - 15) * ratio)
                g = int(23 + (28 - 23) * ratio)
                b = int(42 + (135 - 42) * ratio)
                img.putpixel((x, y), (r, g, b, 255))
                
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
        
        img.save(ICON_FILE, "PNG")
    except Exception as e:
        print(f"Could not generate app icon: {e}")


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
        self.btn_pair.grid(row=4, column=0, columnspan=2, padx=20, pady=15, sticky="ew")
        
        # Instructions Box inside the Dialog
        self.help_frame = ctk.CTkFrame(self, fg_color="#2b3b4c", corner_radius=8)
        self.help_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        help_text = (
            "📌 Where to find this information on Android?\n\n"
            "1. Go to Settings > Developer Options.\n"
            "2. Enable and click on 'Wireless debugging'.\n"
            "3. Select 'Pair device with pairing code'.\n"
            "4. Copy the Pairing Code (6 digits) and the IP address & port (e.g., 192.168.x.x:39361) into the fields above."
        )
        self.help_lbl = ctk.CTkLabel(
            self.help_frame,
            text=help_text,
            font=ctk.CTkFont(size=11),
            justify="left",
            wraplength=340
        )
        self.help_lbl.pack(padx=15, pady=10, fill="both")
        
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


class DeXtopModeApp(ctk.CTk):
    def __init__(self):
        super().__init__(className="dextop")
        
        self.title("DeXtop Mode")
        self.geometry("640x550")
        self.resizable(False, False)
        
        # App state
        self.connected_device = None
        self.dex_process = None
        self.old_timeout = None
        self.is_connecting = False
        
        # Load config
        self.config = self.load_config()
        
        # Generate icon if missing
        ensure_app_icon()
        
        # Set window and taskbar icon
        if os.path.exists(ICON_FILE):
            try:
                icon_img = ImageTk.PhotoImage(file=ICON_FILE)
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
            "fix_oneui_gestures": True
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
        
        self.title_label = ctk.CTkLabel(
            self.title_frame, 
            text="DeXtop Mode", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left")
        
        self.status_indicator = ctk.CTkLabel(
            self.title_frame,
            text="● Disconnected",
            text_color="#ff5555",
            font=ctk.CTkFont(size=14, weight="bold")
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
        self.btn_pair_open.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Current device details
        self.lbl_device_details = ctk.CTkLabel(
            self.tab_conn,
            text="No device detected.",
            text_color="gray"
        )
        self.lbl_device_details.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="w")

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
        self.switch_timeout.grid(row=0, column=0, padx=10, pady=10, sticky="w")

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
        self.switch_fix_gestures.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
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
        self.switch_mouse.grid(row=2, column=0, padx=10, pady=10, sticky="w")

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
        self.switch_keyboard.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        # Manual One UI repair button
        self.btn_repair_gestures = ctk.CTkButton(
            self.tab_settings,
            text="🔄 Repair One UI Gestures Now",
            command=self.manual_repair_gestures,
            fg_color="#1a4f7a",
            hover_color="#246a9f"
        )
        self.btn_repair_gestures.grid(row=4, column=0, padx=10, pady=15, sticky="w")

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
        uhid_lbl.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        # Info note about hidden scrcpy shortcut
        info_lbl = ctk.CTkLabel(
            self.tab_settings,
            text="Note: The Scrcpy application is hidden in your menus to avoid visual clutter.",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="gray",
            justify="left",
            wraplength=500
        )
        info_lbl.grid(row=6, column=0, padx=10, pady=(10, 0), sticky="w")

    # --- DEVICE MONITORING & CONNECTION ---
    def monitor_devices(self):
        while not self.stop_monitor:
            if not self.is_connecting:
                devices = self.get_adb_devices()
                if devices:
                    # Select first active device
                    self.connected_device = devices[0]
                    self.update_status(True, f"Connected: {self.connected_device}")
                else:
                    self.connected_device = None
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

    def update_status(self, connected, text):
        def gui_update():
            if connected:
                self.status_indicator.configure(text=f"● {text}", text_color="#55ff55")
                self.lbl_device_details.configure(
                    text=f"Connected device: {self.connected_device}", 
                    text_color="#55ff55"
                )
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
                        self.update_status(True, f"Connected over Wi-Fi: {self.connected_device}")
                    else:
                        self.connected_device = target
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
                values = ["Default"] + list(sinks.keys())
                
                # Update dropdown safely
                def update_dropdown():
                    self.audio_dropdown.configure(values=values)
                    # Restore previous selection if valid
                    saved_sink = self.config.get("selected_sink", "")
                    if saved_sink in sinks:
                        self.audio_dropdown.set(saved_sink)
                    else:
                        self.audio_dropdown.set("Default")
                self.after(0, update_dropdown)
            except Exception as e:
                print(f"Error listing audio devices: {e}")
                self.sinks_map = {}
                
        threading.Thread(target=run_refresh, daemon=True).start()

    def on_audio_selected(self, choice):
        self.config["selected_sink"] = choice if choice != "Default" else ""
        self.save_config()
        # If user changed it and DeX is running, apply immediately
        if choice != "Default" and choice in self.sinks_map:
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
        self.save_config()

    def repair_gestures_adb(self, device=None):
        target_device = device or self.connected_device
        if not target_device:
            return False, "No device connected."
        try:
            # 1. Wake screen if off
            subprocess.run(["adb", "-s", target_device, "shell", "input", "keyevent", "KEYCODE_WAKEUP"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 2. Force-stop Samsung One UI Home launcher (restarts launcher & rebinds gesture navigation in < 1s)
            subprocess.run(["adb", "-s", target_device, "shell", "am", "force-stop", "com.sec.android.app.launcher"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 3. Force-stop generic/Motorola/Pixel launchers if present
            subprocess.run(["adb", "-s", target_device, "shell", "am", "force-stop", "com.motorola.launcher3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["adb", "-s", target_device, "shell", "am", "force-stop", "com.google.android.apps.nexuslauncher"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 4. Re-enforce gesture navigation mode
            subprocess.run(["adb", "-s", target_device, "shell", "settings", "put", "secure", "navigation_mode", "2"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return True, "One UI Launcher and gesture navigation successfully restarted!"
        except Exception as e:
            return False, f"Failed to repair gestures: {str(e)}"

    def manual_repair_gestures(self):
        if not self.connected_device:
            messagebox.showwarning("No Device", "Please connect a device first.")
            return
        success, msg = self.repair_gestures_adb()
        if success:
            messagebox.showinfo("Gestures Repaired", f"Success:\n{msg}")
        else:
            messagebox.showerror("Repair Failed", f"Error:\n{msg}")

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
        
        # Audio redirect if selected
        if selected_audio != "Default" and selected_audio in self.sinks_map:
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
                # Build arguments based on user config
                cmd = [
                    "systemd-inhibit", 
                    "--what=idle", 
                    "--who=DeXtop Mode", 
                    "--why=Using desktop mode", 
                    "scrcpy", 
                    "-s", device, 
                    "--new-display=1920x1080", 
                    "--turn-screen-off", 
                    "--stay-awake", 
                    "--disable-screensaver",
                    "--audio-codec=aac"
                ]

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

                # Auto-repair One UI gesture navigation on exit
                if self.config.get("fix_oneui_gestures", True) and device:
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

if __name__ == "__main__":
    app = DeXtopModeApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

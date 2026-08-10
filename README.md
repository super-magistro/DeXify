# DeXtop Mode: Samsung DeX & Android Desktop Mode on Linux

**DeXtop Mode** is a modern and lightweight Python GUI wrapper that launches a virtual second screen displaying your Android smartphone's desktop mode (Samsung DeX, Motorola Ready For, native Android AOSP Desktop Mode, etc.) on Linux distributions (Ubuntu, Debian, Linux Mint, Zorin OS, etc.).

It utilizes the powerful and fast engine of [scrcpy](https://github.com/Genymobile/scrcpy) in the background to handle control and video streaming.

---

## 🚀 Key Features

* **Modern Control Center (GUI)**: A beautiful CustomTkinter desktop interface in dark mode. No terminal command writing required!
* **Automated Wireless Debugging (ADB Over Wi-Fi)**:
  * Integrated **Wireless Pairing (Association)** dialog with step-by-step guidance.
  * Direct one-click Wi-Fi connection with smart IP & Port auto-filling.
* **Display Modes & Custom DPI Scaling**:
  * Easily toggle between **Secondary Display (DeX Mode)** and **Main Display Mirroring**.
  * Customizable desktop display density (160 DPI standard desktop, 200 DPI, 240 DPI).
* **Smart Audio Redirection**: Select your preferred output device (e.g. Bluetooth headphones, HDMI, internal PC speakers) dynamically from a dropdown menu using WirePlumber/PipeWire.
* **Intelligent Power Management (Anti-Veille)**:
  * Temporarily disables the smartphone's screen timeout (`screen_off_timeout`) while DeXtop Mode is running, and restores it automatically when closed.
  * Keeps your computer from sleeping during usage via `systemd-inhibit`.
  * Turns off the physical smartphone screen to save battery and avoid screen burn-in.
* **Automatic & Manual One UI Gesture Repair**:
  * Automatically refreshes and restarts the One UI Home launcher (`com.sec.android.app.launcher`) upon disconnecting to prevent back gesture freezes on Samsung smartphones.
  * Prominent **"Repair Phone Gestures (One UI)"** button available on both the Connection and Settings tabs for 1-click manual repair anytime.
* **Mouse & Keyboard Lock (UHID)**:
  * Optional relative mouse capturing (UHID) for high precision control, customizable directly in the Settings tab (press `LAlt` or `Super` to release).
* **Stealth & Native Taskbar Integration**:
  * Includes `StartupWMClass` matching so the custom icon appears natively in your Linux taskbar / dock while running.
  * Hides background `scrcpy` menu icons to keep your desktop applications clutter-free.
  * Automatically hides the DeXtop Mode window during the DeX session.

---

## 🛠️ Prerequisites

1. **Compatible Smartphone**:
   * Samsung Galaxy S series (S8 to S26), Note series, or Z Fold.
   * Motorola Edge or Razr series.
   * Any smartphone running Android 11+ (for wireless) or Android 15+ (for native desktop mode).
2. **On your Phone**:
   * Enable **Developer Options** (Settings > About Phone, tap *Build Number* 7 times).
   * Turn on **USB Debugging** and **Wireless Debugging** in Developer Options.
3. **On your Computer**:
   * A Debian/Ubuntu-based distribution (Ubuntu, Mint, Debian, Pop!_OS, Zorin OS, etc.).

---

## 📥 Installation

Choose your preferred installation method:

### 📦 Option 1: Debian / Ubuntu Package (`.deb`) — Recommended

Download the latest `.deb` package from [GitHub Releases](https://github.com/super-magistro/DeXify/releases) and install it:

```bash
sudo apt install ./dexify_1.0.0_all.deb
```

---

### ⚡ Option 2: One-Line Installer (Terminal)

Run this single command in your terminal to automatically install DeXify:

```bash
curl -fsSL https://raw.githubusercontent.com/super-magistro/DeXify/main/install_dex.sh | bash
```

---

### 🐍 Option 3: PyPI / Pip

```bash
pip install dexify
# or via pipx
pipx install dexify
```

---

### 🛠️ Option 4: Build from Source

```bash
# 1. Clone this repository
git clone https://github.com/super-magistro/DeXify.git
cd DeXify

# 2. Build the .deb package
chmod +x build_deb.sh
./build_deb.sh

# 3. Install the generated package
sudo apt install ./dexify_1.0.0_all.deb
```

---

## 💡 How to Use

1. Ensure your phone and PC are on the same Wi-Fi network (or connected via USB).
2. Open your system's application menu and search for **DeXtop Mode**.
3. **If using Wi-Fi for the first time**:
   * Click **Pair a New Device**.
   * On your phone, inside *Wireless Debugging*, select *Pair device with pairing code*.
   * Enter the IP, the pairing port, and the 6-digit code shown, then click **Start Pairing**.
4. In the main window, type the connection port shown on the phone (or plug in USB).
5. Select your preferred **Audio** output in the Audio tab.
6. Click **Start DeX**.
   * *Your phone screen will turn off, the control GUI will hide itself, and your DeX window will pop up!*
   * *When you close the DeX window, the control GUI will reappear.*

---

## 🗑️ Uninstallation

To remove DeXtop Mode, shortcuts, configurations, and the Python virtual environment:

```bash
chmod +x uninstall.sh
./uninstall.sh
```

---

## 💳 Credits

* Engine: [scrcpy](https://github.com/Genymobile/scrcpy) by Genymobile.
* Wrapper & Configurator: super-magistro.

Licensed under the MIT License. See [LICENSE](LICENSE) for details.

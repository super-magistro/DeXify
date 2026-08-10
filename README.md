# DeXtop Mode: Samsung DeX & Android Desktop Mode on Linux, macOS & Windows

**DeXtop Mode** is a modern, cross-platform Python GUI wrapper that launches a virtual second screen displaying your Android smartphone's desktop mode (Samsung DeX, Motorola Ready For, native Android AOSP Desktop Mode, etc.) on **Linux** (Ubuntu, Debian, Mint, Pop!_OS, Zorin OS), **macOS** (Intel & Apple Silicon M1-M4), and **Windows** (10/11).

It utilizes the powerful engine of [scrcpy](https://github.com/Genymobile/scrcpy) in the background to handle control and high-performance video/audio streaming.

---

## 🚀 Key Features

* **Cross-Platform Support (Linux, macOS, Windows)**:
  * 🐧 **Linux**: Native Debian package (`.deb`), 1-line `curl` script, taskbar integration (`StartupWMClass=dextop`), and WirePlumber/PipeWire audio routing.
  * 🍏 **macOS**: Native Disk Image installer (`.dmg`), `dextop-mode.app` bundle, and 1-click Homebrew dependency installer.
  * 🪟 **Windows**: Standalone 64-bit executable (`.exe`) and 1-click Winget dependency installer.
  * 🐍 **PyPI / Pip / Pipx**: `pip install dextop-mode` / `pipx install dextop-mode` for all platforms.
* **Modern Control Center (GUI)**: A sleek CustomTkinter desktop interface in dark mode.
* **Automated Wireless Debugging (ADB Over Wi-Fi)**:
  * Integrated **Wireless Pairing (Association)** dialog with step-by-step guidance.
  * Direct one-click Wi-Fi connection with smart IP & Port auto-filling.
* **Display Modes & Custom DPI Scaling**:
  * Easily toggle between **Secondary Display (DeX Mode)** and **Main Display Mirroring**.
  * Customizable desktop display density (160 DPI standard desktop, 200 DPI, 240 DPI).
* **Intelligent Power Management (Anti-Veille)**:
  * Temporarily disables the smartphone's screen timeout (`screen_off_timeout`) while DeXtop Mode is running, and restores it automatically when closed.
  * Prevents system sleep during usage (`systemd-inhibit` on Linux / continuous thread state on Windows).
  * Turns off the physical smartphone screen to save battery and avoid screen burn-in.
* **Automatic & Manual One UI Gesture Repair**:
  * Automatically refreshes and restarts the One UI Home launcher (`com.sec.android.app.launcher`) upon disconnecting to prevent back gesture freezes on Samsung smartphones.
  * Prominent **"Repair Phone Gestures (One UI)"** button available on both the Connection and Settings tabs for 1-click manual repair anytime.
* **Mouse & Keyboard Lock (UHID)**:
  * Optional relative mouse capturing (UHID) for high precision control, customizable directly in the Settings tab (press `LAlt` or `Super` to release).

---

## 🛠️ Prerequisites

1. **Compatible Smartphone**:
   * Samsung Galaxy S series (S8 to S26), Note series, or Z Fold.
   * Motorola Edge or Razr series.
   * Any smartphone running Android 11+ (for wireless debugging) or Android 15+ (for native desktop mode).
2. **On your Phone**:
   * Enable **Developer Options** (Settings > About Phone, tap *Build Number* 7 times).
   * Turn on **USB Debugging** and **Wireless Debugging** in Developer Options.
3. **On your Computer**:
   * **Linux**: Any Debian/Ubuntu-based distribution (Ubuntu, Mint, Debian, Pop!_OS, Zorin OS, etc.).
   * **macOS**: macOS 11+ (Intel or Apple Silicon M1/M2/M3/M4).
   * **Windows**: Windows 10 or Windows 11 (64-bit).

---

## 📥 Installation

Choose your platform below:

### 🐧 Linux (Debian / Ubuntu / Mint / Pop!_OS / Zorin OS)

#### **Option A: Debian Package (`.deb`) — Recommended**
Download the latest `.deb` package from [GitHub Releases](https://github.com/super-magistro/DeXtop-mode/releases) and install it:
```bash
sudo apt install ./dextop-mode_1.0.12_all.deb
```

#### **Option B: One-Line Terminal Installer**
```bash
curl -fsSL https://raw.githubusercontent.com/super-magistro/DeXtop-mode/main/install_dex.sh | bash
```

---

### 🍏 macOS (Apple Silicon & Intel)

#### **Option A: macOS Disk Image (`.dmg`) — Recommended**
1. Download **`dextop-mode_macOS.dmg`** from [GitHub Releases](https://github.com/super-magistro/DeXtop-mode/releases).
2. Double-click the `.dmg` image and open **dextop-mode.app**!
3. If `scrcpy` or `adb` are missing, **DeXtop Mode** will offer a 1-click prompt to automatically install dependencies via Homebrew.

---

### 🪟 Windows (10 / 11)

#### **Option A: Standalone Executable (`.exe`) — Recommended**
1. Download **`dextop-mode_windows_x64.exe`** from [GitHub Releases](https://github.com/super-magistro/DeXtop-mode/releases).
2. Double-click **`dextop-mode_windows_x64.exe`** to launch!
3. If `scrcpy` or `adb` are missing, **DeXtop Mode** will offer a 1-click prompt to automatically install dependencies via Winget.

---

### 🐍 PyPI / Pip / Pipx (Universal for All OS)

```bash
pip install dextop-mode
# or via pipx
pipx install dextop-mode
```

---

## 💡 How to Use

1. Ensure your phone and PC are on the same Wi-Fi network (or connected via USB).
2. Open **DeXtop Mode**.
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

To remove DeXtop Mode and clean up configurations:

* **Linux (`.deb`)**:
  ```bash
  sudo apt remove dextop-mode
  ```
* **Pip / Pipx (All OS)**:
  ```bash
  dextop --uninstall
  pipx uninstall dextop-mode
  ```

---

## 💳 Credits

* Engine: [scrcpy](https://github.com/Genymobile/scrcpy) by Genymobile.
* Wrapper & Configurator: super-magistro.

Licensed under the MIT License. See [LICENSE](https://github.com/super-magistro/DeXtop-mode/blob/main/LICENSE) for details.

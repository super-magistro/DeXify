# DeXify: Samsung DeX & Desktop Mode on Linux

This script automatically installs and configures a turnkey solution to use your Android smartphone's desktop mode (Samsung DeX, Motorola Ready For, etc.) on Linux distributions (Ubuntu, Debian, Linux Mint, etc.).

It relies on the excellent [scrcpy](https://github.com/Genymobile/scrcpy) tool by forcing the creation of a virtual display.

## Features

* **Turnkey Shortcut:** Creates a "DeX Mode" entry in your application menu with a dedicated icon.
* **Intelligent Power Management:** Uses `systemd-inhibit` to keep your PC awake during sessions and automatically turns off your phone's physical display to save battery and prevent burn-in.
* **Optimized Scaling:** Pre-configured with a 160 DPI density to ensure windows and icons look native on 1080p monitors.
* **Seamless Control**: Control the Android desktop environment directly using your PC's keyboard, mouse, and scroll wheel.

## Prerequisites

1. **Compatible Hardware:**
* Samsung Galaxy S series (S8 to S26), Note series, or Z Fold.
* Motorola Edge or Razr series.
* Any smartphone running Android 15+ with "Desktop Mode" enabled.
* A high-quality USB-C 3.1 cable capable of data transfer.

2. **Software & Settings:**

* **OS:** A Debian/Ubuntu-based Linux distribution (Ubuntu, Linux Mint, Zorin OS, etc.).
* **USB Debugging:** Go to *Settings > About Phone* and tap *Build Number* 7 times to unlock Developer Options. Then, go to *Developer Options* and enable **USB debugging**.
* **Desktop Mode (Non-Samsung only):** In *Developer Options*, scroll down and enable both **Force desktop mode** and **Enable freeform windows** (a phone reboot may be required).


## Installation

Open your terminal and run the following commands:

```bash
# 1. Clone the repository
git clone https://github.com/super-magistro/DeXify.git
cd DeXify

# 2. Make the installer executable
chmod +x install_dex.sh

# 3. Run the installation
./install_dex.sh
```

*Note: The script will prompt for your administrator password once at the start to clear the sudo cache and install the necessary build tools.*

## How to use it

1. Connect your smartphone to your PC via USB.
2. Accept the "Allow USB Debugging?" prompt on your phone screen if it appears.
3. Open your Linux system's application menu and search for **DeX Mode**.
4. Click the icon. Your phone will stay awake, but its screen will turn black to save power and avoid burning screen, while the DeX interface appears on your desktop.

## Troubleshooting

* **"Device not found":** Check your cable and ensure USB Debugging is turned on in Developer Options.
* **Black screen / No DeX:** Ensure your phone is unlocked when you click the icon for the first time.
* **Apt lock error:** The script automatically waits for background updates, but you can also manually close your system's Software Updater if it is running.

## Uninstallation

To remove the shortcuts and the DeXify configuration while keeping the system clean:

```bash
chmod +x uninstall.sh
./uninstall.sh
```

## Credits

DeXify is a wrapper and configurator built upon the incredible work of the Genymobile team.

* Core Engine: [scrcpy](https://github.com/Genymobile/scrcpy)
* Automation & Configuration: super-magistro

## License

This project is licensed under the MIT License - see the [License](LICENSE) file for details.

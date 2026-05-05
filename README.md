# DeXify: Samsung DeX & Desktop Mode on Linux

This script automatically installs and configures a turnkey solution to use your Android smartphone's desktop mode (Samsung DeX, Motorola Ready For, etc.) on Linux distributions (Ubuntu, Debian, Linux Mint, etc.).

It relies on the excellent [scrcpy](https://github.com/Genymobile/scrcpy) tool by forcing the creation of a virtual display.

## Features

- **Automatic installation:** Cleans up old versions, installs dependencies, and compiles the latest version of `scrcpy` from source.
- **Desktop Shortcut:** Creates a "DeX Mode" icon directly in your application menu (no terminal required).
- **Integrated Anti-sleep:** Automatically prevents the PC screen from going to sleep as long as the DeX window is open (via `systemd-inhibit`).
- **Energy saving:** Turns off the phone's physical screen while in use on the computer.
- **Real multitasking:** Allows you to physically use the phone while the desktop interface is running on the PC.

## Prerequisites

1. **A compatible smartphone:** 
   - Samsung Galaxy S series (S20 to S26), Note, or Z Fold (for Samsung DeX).
   - Motorola Edge series (for Ready For).
   - Smartphones running Android 15/16 that support native desktop mode.
2. **USB Debugging enabled:** You must have enabled "Developer Options" and "USB Debugging" on your phone.
3. A USB-C cable capable of data transfer.
4. A Debian/Ubuntu-based Linux distribution.

## Installation

Open a terminal and run the following commands:

```bash
# 1. Clone the repository (or download the script)
git clone [https://github.com/super-magistro/DeXify.git](https://github.com/super-magistro/DeXify.git)
cd DeXify

# 2. Make the script executable
chmod +x install_dex.sh

# 3. Run the installation
./install_dex.sh
```

*(During installation, you will be prompted for your administrator password to install the necessary dependencies).*

## How to use it?

1. Connect your smartphone to your PC via the USB cable.
2. Allow USB debugging on the phone screen if a notification appears.
3. Open your Linux system's application menu (Super/Windows key) and search for **DeX Mode**.
4. Click the icon, and enjoy!

## Uninstallation

If you want to remove the DeX Mode shortcut, simply run the uninstall script:

```bash
chmod +x uninstall.sh
./uninstall.sh
```

## Credits

This script acts as a facilitator and configurator for the **Scrcpy** tool.
A huge thank you to the [Genymobile](https://github.com/Genymobile) team for developing `scrcpy`, without which none of this would be possible on Linux.

## License

This project is licensed under the MIT License - see the [License](LICENSE) file for details.

#!/bin/bash
# Automatic installation script for Desktop Mode (Samsung DeX / Motorola) via Scrcpy

echo "=========================================="
echo " Installing Scrcpy & DeX Shortcut "
echo "=========================================="

echo -e "\n[1/4] Cleaning up old versions (Snap)..."
sudo snap remove scrcpy 2>/dev/null

echo -e "\n[2/4] Installing required dependencies..."
sudo apt update && sudo apt install -y ffmpeg libsdl2-2.0-0 adb wget gcc git pkg-config meson ninja-build libsdl2-dev libavcodec-dev libavdevice-dev libavformat-dev libavutil-dev libswresample-dev libusb-1.0-0-dev

echo -e "\n[3/4] Downloading and compiling the latest version of Scrcpy..."
cd /tmp
rm -rf scrcpy-install-tmp
git clone https://github.com/Genymobile/scrcpy scrcpy-install-tmp
cd scrcpy-install-tmp
./install_release.sh

echo -e "\n[4/4] Creating the 'DeX Mode' shortcut with anti-sleep..."
mkdir -p ~/.local/share/applications/
cat <<EOF > ~/.local/share/applications/mode-dex.desktop
[Desktop Entry]
Version=1.0
Name=DeX Mode
Comment=Launch desktop mode (Samsung DeX, Ready For...)
Exec=systemd-inhibit --what=idle --who="DeX Mode" --why="Using phone screen" scrcpy --new-display=1920x1080 --turn-screen-off
Icon=smartphone
Terminal=false
Type=Application
Categories=Utility;
EOF

# Refresh the desktop database to make the icon appear
update-desktop-database ~/.local/share/applications/ 2>/dev/null

echo "=========================================="
echo " Installation completed successfully!"
echo "You can now search for 'DeX Mode' in your application menu."
echo "Plug in any compatible smartphone via USB and click on the icon."
echo "=========================================="

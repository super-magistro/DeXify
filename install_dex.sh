#!/bin/bash
# DeXify: Automatic installation script for Desktop Mode via Scrcpy

# Exit immediately if a command exits with a non-zero status
set -e

# Cleanup function for temporary build files
cleanup() {
    echo -e "\n[Cleanup] Removing temporary build files..."
    rm -rf /tmp/scrcpy-install-tmp
}
trap cleanup EXIT

echo "=========================================="
echo "      Installing DeXify & Scrcpy          "
echo "=========================================="

echo -e "\n[1/4] Cleaning up old versions..."
# Don't stop the script if snap isn't installed
sudo snap remove scrcpy 2>/dev/null || true

echo -e "\n[2/4] Installing dependencies..."
# Check for the apt lock before proceeding
while fuser /var/lib/apt/lists/lock >/dev/null 2>&1 ; do
    echo "Waiting for the package manager (apt) to be released..."
    sleep 2
done

sudo apt update
sudo apt install -y ffmpeg libsdl2-2.0-0 adb wget gcc git pkg-config meson ninja-build \
    libsdl2-dev libavcodec-dev libavdevice-dev libavformat-dev libavutil-dev \
    libswresample-dev libusb-1.0-0-dev

echo -e "\n[3/4] Downloading and compiling Scrcpy..."
cd /tmp
rm -rf scrcpy-install-tmp
git clone https://github.com/Genymobile/scrcpy scrcpy-install-tmp
cd scrcpy-install-tmp

# Build and install
./install_release.sh

echo -e "\n[4/4] Creating the 'DeX Mode' shortcut..."
mkdir -p ~/.local/share/applications/

cat <<EOF > ~/.local/share/applications/mode-dex.desktop
[Desktop Entry]
Version=1.0
Name=DeX Mode
Comment=Launch desktop mode (Samsung DeX, Ready For...)
Exec=systemd-inhibit --what=idle --who="DeXify" --why="Using desktop mode" scrcpy --new-display=1920x1080 --turn-screen-off --disable-screensaver
Icon=smartphone
Terminal=false
Type=Application
Categories=Utility;
EOF

# Refresh the desktop application database
update-desktop-database ~/.local/share/applications/ 2>/dev/null

echo "=========================================="
echo "      Installation completed successfully!"
echo "=========================================="
echo "You can now launch 'DeX Mode' from your application menu."
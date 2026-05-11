#!/bin/bash
# DeXify: Professional installation script for Desktop Mode via Scrcpy

# Exit on error
set -e

echo "=========================================="
echo "          Installing DeXify               "
echo "=========================================="

# Request sudo privileges at the very beginning, BEFORE the spinner
echo "Administrator privileges are required for installation."
# Force sudo to forget any cached password
sudo -k
# Now, it will STRICTLY require the password
sudo -v

# Keep the sudo token active in the background during the entire installation
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# --- UI SETTINGS ---
# Hide cursor for a cleaner look
tput civis

cleanup() {
    # Restore cursor on exit
    tput cnorm
    sudo rm -rf /tmp/scrcpy-install-tmp
}
trap cleanup EXIT

# Spinner function to show progress without flooding the terminal
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# --- STEP 1: CLEANUP ---
echo -n "[1/4] Removing old versions... "
(sudo snap remove scrcpy > /dev/null 2>&1 || true) & spinner $!
echo "Done!"

# --- STEP 2: DEPENDENCIES ---
echo -n "[2/4] Installing system dependencies... "
(
    # Ensure apt is not locked
    while sudo fuser /var/lib/dpkg/lock-frontend /var/lib/apt/lists/lock >/dev/null 2>&1; do
        sleep 1
    done
    sudo apt update > /dev/null 2>&1
    sudo DEBIAN_FRONTEND=noninteractive apt install -y ffmpeg libsdl2-2.0-0 adb wget gcc git pkg-config meson ninja-build \
        libsdl2-dev libavcodec-dev libavdevice-dev libavformat-dev libavutil-dev \
        libswresample-dev libusb-1.0-0-dev > /dev/null 2>&1
) & spinner $!
echo "Done!"

# --- STEP 3: BUILD ---
echo -n "[3/4] Building Scrcpy from source... "
(
    cd /tmp
    rm -rf scrcpy-install-tmp
    git clone https://github.com/Genymobile/scrcpy scrcpy-install-tmp > /dev/null 2>&1
    cd scrcpy-install-tmp
    # Explicitly use sudo for the installation
    sudo ./install_release.sh > /dev/null 2>&1
) & spinner $!
echo "Done!"

# --- STEP 4: SHORTCUT ---
echo -n "[4/4] Configuring DeX Mode shortcut... "
(
    mkdir -p ~/.local/share/applications/
    # The Exec line now forces the Samsung DeX launcher after scrcpy starts
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
    update-desktop-database ~/.local/share/applications/ > /dev/null 2>&1
) & spinner $!
echo "Done!"

echo "=========================================="
echo "      Installation successful!            "
echo "=========================================="
echo "Search for 'DeX Mode' in your app menu."
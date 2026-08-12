#!/bin/bash
# DeXtop Mode: Professional uninstallation script

# Exit on error
set -e

# Dynamically get the repository directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# --- UI SETTINGS ---
# Hide cursor for a cleaner look
tput civis

cleanup() {
    # Restore cursor on exit
    tput cnorm
}
trap cleanup EXIT

# Spinner function to show progress
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

echo "=========================================="
echo "          Uninstalling DeXtop Mode        "
echo "=========================================="

echo "Administrator privileges are required for uninstallation."
sudo -k
sudo -v

# Keep the sudo token active in the background
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

# --- STEP 1: REMOVE SHORTCUTS & DEBIAN PACKAGE ---
echo -n "[1/3] Removing Debian package, shortcuts & configs... "
(
    sudo apt remove -y dextop-mode > /dev/null 2>&1 || true
    rm -f "$HOME/.local/share/applications/dextop.desktop"
    rm -f "$HOME/.local/share/applications/mode-dex.desktop"
    rm -f "$HOME/.local/share/applications/scrcpy.desktop"
    rm -f "$HOME/.local/share/applications/scrcpy-console.desktop"
    rm -rf "$HOME/.config/dextop"
    rm -rf "$HOME/.config/dexify"
) & spinner $!
echo "Done!"

# --- STEP 2: REFRESH DATABASE ---
echo -n "[2/3] Refreshing application database... "
(
    update-desktop-database "$HOME/.local/share/applications/" > /dev/null 2>&1
) & spinner $!
echo "Done!"

# --- STEP 3: REMOVE VIRTUAL ENVIRONMENT ---
echo -n "[3/3] Removing local Python virtual environment & caches... "
(
    rm -rf "$DIR/venv"
    find "$DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
) & spinner $!
echo "Done!"

echo "=========================================="
echo "    DeXtop Mode successfully removed!     "
echo "=========================================="
echo ""
echo "Note: Scrcpy and its system dependencies remain installed."
echo "If you wish to completely remove Scrcpy from your system, you can run:"
echo "sudo apt remove --purge scrcpy"
echo "=========================================="
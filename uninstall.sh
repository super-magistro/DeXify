#!/bin/bash
# DeXify: Professional uninstallation script

# Exit on error
set -e

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
echo "          Uninstalling DeXify             "
echo "=========================================="

# --- STEP 1: REMOVE SHORTCUTS ---
echo -n "[1/2] Removing desktop shortcuts... "
(
    rm -f ~/.local/share/applications/mode-dex.desktop
    rm -f ~/.local/share/applications/samsung-dex.desktop
) & spinner $!
echo "Done!"

# --- STEP 2: REFRESH DATABASE ---
echo -n "[2/2] Refreshing application database... "
(
    update-desktop-database ~/.local/share/applications/ > /dev/null 2>&1
) & spinner $!
echo "Done!"

echo "=========================================="
echo "      DeXify successfully removed!        "
echo "=========================================="
echo ""
echo "Note: Scrcpy and its dependencies remain installed."
echo "If you wish to completely remove Scrcpy from your system, you can run:"
echo "sudo rm -rf /usr/local/bin/scrcpy /usr/local/share/scrcpy /usr/local/share/applications/scrcpy*.desktop"
echo "=========================================="
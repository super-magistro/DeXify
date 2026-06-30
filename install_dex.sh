#!/bin/bash
# DeXtop Mode: Professional installation script for Desktop Mode via Python GUI wrappers

# Exit on error
set -e

# Dynamically get the repository directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=========================================="
echo "          Installing DeXtop Mode          "
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
echo -n "[1/5] Removing old versions... "
(
    sudo snap remove scrcpy > /dev/null 2>&1 || true
    rm -f "$HOME/.local/bin/dexify-run.sh" || true
    rm -f "$HOME/.local/share/applications/mode-dex.desktop" || true
) & spinner $!
echo "Done!"

# --- STEP 2: SYSTEM DEPENDENCIES ---
echo -n "[2/5] Installing dependencies (Scrcpy, ADB, Python-TK)... "
(
    while sudo fuser /var/lib/dpkg/lock-frontend /var/lib/apt/lists/lock >/dev/null 2>&1; do sleep 1; done
    sudo apt update > /dev/null 2>&1
    sudo DEBIAN_FRONTEND=noninteractive apt install -y scrcpy ffmpeg adb wget python3-tk python3-pip python3-venv > /dev/null 2>&1
) & spinner $!
echo "Done!"

# --- STEP 3: PYTHON VIRTUAL ENVIRONMENT ---
echo -n "[3/5] Setting up Python virtual environment... "
(
    python3 -m venv "$DIR/venv" > /dev/null 2>&1
    "$DIR/venv/bin/pip" install --upgrade pip > /dev/null 2>&1
    "$DIR/venv/bin/pip" install customtkinter pillow > /dev/null 2>&1
    
    # Pre-generate the app icon
    "$DIR/venv/bin/python" -c "import sys; sys.path.append('$DIR'); import dextop; dextop.ensure_app_icon()" > /dev/null 2>&1
) & spinner $!
echo "Done!"

# --- STEP 4: HIDING ORIGINAL SCRCPY MENUS ---
echo -n "[4/5] Securing system (hiding background scrcpy shortcuts)... "
(
    mkdir -p "$HOME/.local/share/applications"
    
    # Override scrcpy launcher entries locally with NoDisplay to hide them
    cat <<EOF > "$HOME/.local/share/applications/scrcpy.desktop"
[Desktop Entry]
Type=Application
Name=scrcpy
NoDisplay=true
EOF

    cat <<EOF > "$HOME/.local/share/applications/scrcpy-console.desktop"
[Desktop Entry]
Type=Application
Name=scrcpy (console)
NoDisplay=true
EOF
) & spinner $!
echo "Done!"

# --- STEP 5: DE-CLUTTERED SHORTCUT ---
echo -n "[5/5] Configuring DeXtop Mode graphical shortcut... "
(
    mkdir -p "$HOME/.local/share/applications/"
    
    # The desktop shortcut points to the Python GUI inside the virtual environment
    cat <<EOF > "$HOME/.local/share/applications/dextop.desktop"
[Desktop Entry]
Version=1.0
Name=DeXtop Mode
Comment=Launch DeXtop Mode wrapper (Samsung DeX & Native Desktop)
Exec=$DIR/venv/bin/python $DIR/dextop.py
Icon=$HOME/.config/dextop/icon.png
Terminal=false
Type=Application
Categories=Utility;
EOF
    update-desktop-database "$HOME/.local/share/applications/" > /dev/null 2>&1
) & spinner $!
echo "Done!"

echo "=========================================="
echo "      Installation successful!            "
echo "=========================================="
echo "Search for 'DeXtop Mode' in your application menu to launch the control GUI."

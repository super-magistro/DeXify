#!/bin/bash
# Uninstallation script for DeXify

echo "=========================================="
echo " Uninstalling DeXify "
echo "=========================================="

echo "[1/2] Removing desktop shortcuts..."
rm -f ~/.local/share/applications/mode-dex.desktop
rm -f ~/.local/share/applications/samsung-dex.desktop

echo "[2/2] Refreshing application database..."
update-desktop-database ~/.local/share/applications/ 2>/dev/null

echo "=========================================="
echo " DeXify has been successfully removed."
echo ""
echo " Note: Scrcpy and its dependencies remain installed on your system."
echo " If you wish to completely remove Scrcpy, you will need to uninstall"
echo " it from its source build or package manager."
echo "=========================================="

#!/bin/bash
set -e

VERSION="1.0.0"
BUILD_DIR="build_deb"
PKG_NAME="dexify_${VERSION}_all.deb"

echo "=========================================="
echo "      Building Debian Package: ${PKG_NAME} "
echo "=========================================="

# Clean up previous build directory
rm -rf "$BUILD_DIR"
rm -f "$PKG_NAME"

# Create directory structure
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/lib/python3/dist-packages"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/512x512/apps"
mkdir -p "$BUILD_DIR/usr/share/doc/dexify"

# 1. Create DEBIAN/control
cat <<EOF > "$BUILD_DIR/DEBIAN/control"
Package: dexify
Version: ${VERSION}
Architecture: all
Maintainer: Romain Guillon <super-magistro>
Depends: scrcpy, adb, python3 (>= 3.8), python3-customtkinter, python3-pil, python3-tk, ffmpeg
Section: utils
Priority: optional
Homepage: https://github.com/super-magistro/DeXify
Description: Samsung DeX & Android Desktop Mode GUI wrapper for Linux
 DeXtop Mode (DeXify) is a modern Python GUI wrapper using scrcpy to launch
 virtual second screens displaying Android desktop mode (Samsung DeX, Motorola
 Ready For, Android 15 Desktop Mode) on Linux distributions.
EOF

# 2. Create DEBIAN/postinst
cat <<'EOF' > "$BUILD_DIR/DEBIAN/postinst"
#!/bin/sh
set -e

if [ -x "$(command -v update-desktop-database)" ]; then
    update-desktop-database -q /usr/share/applications || true
fi
if [ -x "$(command -v gtk-update-icon-cache)" ]; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi

exit 0
EOF
chmod 755 "$BUILD_DIR/DEBIAN/postinst"

# 3. Copy python code
cp dextop.py "$BUILD_DIR/usr/lib/python3/dist-packages/"
chmod 644 "$BUILD_DIR/usr/lib/python3/dist-packages/dextop.py"

# 4. Generate icon and place it in hicolor icons folder
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f "$DIR/venv/bin/python" ]; then
    "$DIR/venv/bin/python" -c "import sys; sys.path.append('$DIR'); import dextop; dextop.ensure_app_icon()" || true
fi
if [ -f "$HOME/.config/dextop/icon.png" ]; then
    cp "$HOME/.config/dextop/icon.png" "$BUILD_DIR/usr/share/icons/hicolor/512x512/apps/dextop.png"
    chmod 644 "$BUILD_DIR/usr/share/icons/hicolor/512x512/apps/dextop.png"
fi

# 5. Create launcher script in /usr/bin/dextop
cat <<'EOF' > "$BUILD_DIR/usr/bin/dextop"
#!/bin/sh
exec python3 /usr/lib/python3/dist-packages/dextop.py "$@"
EOF
chmod 755 "$BUILD_DIR/usr/bin/dextop"
ln -sf dextop "$BUILD_DIR/usr/bin/dexify"

# 6. Create Desktop Entry
cat <<EOF > "$BUILD_DIR/usr/share/applications/dextop.desktop"
[Desktop Entry]
Version=1.0
Name=DeXtop Mode
Comment=Launch DeXtop Mode wrapper (Samsung DeX & Native Desktop)
Exec=/usr/bin/dextop
Icon=dextop
Terminal=false
Type=Application
Categories=Utility;
StartupWMClass=dextop
EOF
chmod 644 "$BUILD_DIR/usr/share/applications/dextop.desktop"

# 7. Create copyright file
cp LICENSE "$BUILD_DIR/usr/share/doc/dexify/copyright"
chmod 644 "$BUILD_DIR/usr/share/doc/dexify/copyright"

# 8. Build package
dpkg-deb --root-owner-group --build "$BUILD_DIR" "$PKG_NAME"

# Cleanup build_deb folder
rm -rf "$BUILD_DIR"

echo "=========================================="
echo " Package successfully built: ${PKG_NAME}  "
echo " Install with: sudo apt install ./${PKG_NAME} "
echo "=========================================="

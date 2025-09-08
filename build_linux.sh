#!/bin/bash

# Build script for Linux

set -e

echo "Building U2Be Down for Linux..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found! Please install Python 3.8 or higher."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found. Please run this script from the project directory."
    exit 1
fi

# Install build dependencies
echo "Installing build dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller
python3 -m pip install -r requirements.txt

# Create the spec file
echo "Creating PyInstaller spec file..."
cat > u2be_down.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('config.json', '.'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'moviepy.video.io.ffmpeg_tools',
        'moviepy.audio.io.ffmpeg_audiowriter',
        'pygame',
        'mutagen',
        'librosa',
        'soundfile',
        'scipy',
        'numpy',
        'imageio_ffmpeg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='u2be_down',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Build the executable
echo "Building executable..."
pyinstaller --clean u2be_down.spec

# Create installer directory
echo "Creating installer package..."
mkdir -p installer
cp dist/u2be_down installer/
cp config.json installer/ 2>/dev/null || true
if [ -d "assets" ]; then
    cp -r assets installer/
fi

# Create installation script
cat > installer/install.sh << 'EOF'
#!/bin/bash

# U2Be Down - Linux Installer

set -e

INSTALL_DIR="/opt/u2be_down"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"
SCRIPT_DIR="$(dirname "$0")"

echo "Installing U2Be Down..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Copy files
cp "$SCRIPT_DIR/u2be_down" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/config.json" "$INSTALL_DIR/" 2>/dev/null || true
if [ -d "$SCRIPT_DIR/assets" ]; then
    cp -r "$SCRIPT_DIR/assets" "$INSTALL_DIR/"
fi

# Make executable
chmod +x "$INSTALL_DIR/u2be_down"

# Create symlink
ln -sf "$INSTALL_DIR/u2be_down" "$BIN_DIR/u2be_down"

# Create desktop entry
cat > "$DESKTOP_DIR/u2be_down.desktop" << DESKTOP_EOF
[Desktop Entry]
Name=U2Be Down
Comment=YouTube Video Downloader
Exec=$INSTALL_DIR/u2be_down
Icon=$INSTALL_DIR/assets/icon.png
Terminal=true
Type=Application
Categories=AudioVideo;Network;
DESKTOP_EOF

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo "U2Be Down installed successfully!"
echo "You can run it from terminal with: u2be_down"
echo "Or find it in your applications menu."
EOF

# Create uninstallation script
cat > installer/uninstall.sh << 'EOF'
#!/bin/bash

# U2Be Down - Linux Uninstaller

set -e

INSTALL_DIR="/opt/u2be_down"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"

echo "Uninstalling U2Be Down..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Remove files
rm -rf "$INSTALL_DIR"
rm -f "$BIN_DIR/u2be_down"
rm -f "$DESKTOP_DIR/u2be_down.desktop"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo "U2Be Down uninstalled successfully!"
EOF

# Make scripts executable
chmod +x installer/install.sh
chmod +x installer/uninstall.sh

# Create .deb package structure
echo "Creating .deb package structure..."
DEB_DIR="u2be-down_1.0.0_amd64"
mkdir -p "$DEB_DIR/DEBIAN"
mkdir -p "$DEB_DIR/opt/u2be_down"
mkdir -p "$DEB_DIR/usr/local/bin"
mkdir -p "$DEB_DIR/usr/share/applications"

# Copy files for .deb
cp dist/u2be_down "$DEB_DIR/opt/u2be_down/"
cp config.json "$DEB_DIR/opt/u2be_down/" 2>/dev/null || true
if [ -d "assets" ]; then
    cp -r assets "$DEB_DIR/opt/u2be_down/"
fi

# Create control file
cat > "$DEB_DIR/DEBIAN/control" << 'EOF'
Package: u2be-down
Version: 1.0.0
Section: multimedia
Priority: optional
Architecture: amd64
Depends: python3, ffmpeg
Maintainer: U2Be Down Team <noreply@example.com>
Description: YouTube Video Downloader
 A simple and efficient YouTube video downloader with GUI support.
 Supports downloading individual videos and playlists.
EOF

# Create postinst script
cat > "$DEB_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
ln -sf /opt/u2be_down/u2be_down /usr/local/bin/u2be_down

# Create desktop entry
cat > /usr/share/applications/u2be_down.desktop << DESKTOP_EOF
[Desktop Entry]
Name=U2Be Down
Comment=YouTube Video Downloader
Exec=/opt/u2be_down/u2be_down
Icon=/opt/u2be_down/assets/icon.png
Terminal=true
Type=Application
Categories=AudioVideo;Network;
DESKTOP_EOF

update-desktop-database /usr/share/applications 2>/dev/null || true
EOF

# Create prerm script
cat > "$DEB_DIR/DEBIAN/prerm" << 'EOF'
#!/bin/bash
rm -f /usr/local/bin/u2be_down
rm -f /usr/share/applications/u2be_down.desktop
update-desktop-database /usr/share/applications 2>/dev/null || true
EOF

# Make scripts executable
chmod +x "$DEB_DIR/DEBIAN/postinst"
chmod +x "$DEB_DIR/DEBIAN/prerm"

# Build .deb package if dpkg-deb is available
if command -v dpkg-deb &> /dev/null; then
    echo "Building .deb package..."
    dpkg-deb --build "$DEB_DIR"
    echo ".deb package created: $DEB_DIR.deb"
else
    echo "dpkg-deb not found. .deb structure created but not packaged."
fi

# Create tar.gz archive
echo "Creating tar.gz archive..."
tar -czf u2be_down_linux.tar.gz -C installer .

echo ""
echo "Build completed successfully!"
echo ""
echo "Generated files:"
echo "- dist/u2be_down (standalone executable)"
echo "- installer/ (installer directory with scripts)"
echo "- u2be_down_linux.tar.gz (portable archive)"
if [ -f "$DEB_DIR.deb" ]; then
    echo "- $DEB_DIR.deb (Debian package)"
fi
echo ""
echo "Installation instructions:"
echo "1. Extract u2be_down_linux.tar.gz"
echo "2. Run: sudo ./install.sh"
echo ""
echo "Or install the .deb package with:"
echo "sudo dpkg -i $DEB_DIR.deb"

# U2Be Down - YouTube Downloader & Music Player

🎵 A comprehensive YouTube video and audio downloader with built-in music player and modern GUI.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

## ✨ Features

- 📹 **Download YouTube videos** in various formats
- 🎵 **Convert to MP3** automatically  
- 🎶 **Built-in music player** with playlist support
- ⚡ **Parallel downloads** for faster processing
- 📊 **Progress tracking** and download history
- 🖥️ **Modern GUI** with intuitive interface
- 🔄 **Playlist support** with automatic organization
- 🎛️ **Audio controls** (pitch, speed, volume)
- 📱 **Cross-platform** support (Windows, Linux, macOS)

## 📦 Installation

### Pre-built Releases

Download the latest release for your platform:
- **Windows**: `u2be_down.exe`
- **Linux**: `.deb` package or `AppImage`
- **macOS**: `.app` or `.dmg` installer

[📥 Download Latest Release](https://github.com/fchevitarese/u2be_down/releases/latest)

### 🐧 Linux Installation

#### Via .deb Package (Ubuntu/Debian)
```bash
# Download and install
wget https://github.com/fchevitarese/u2be_down/releases/latest/download/u2be-down_*_amd64.deb
sudo dpkg -i u2be-down_*.deb
sudo apt-get install -f  # Fix dependencies if needed

# Run
u2be_down
```

#### Via AppImage (Universal Linux)
```bash
# Download and run
wget https://github.com/fchevitarese/u2be_down/releases/latest/download/U2Be_Down-x86_64.AppImage
chmod +x U2Be_Down-x86_64.AppImage
./U2Be_Down-x86_64.AppImage
```

### 🍎 macOS Installation

#### Via DMG Installer
1. Download `U2Be-Down-macOS.dmg`
2. Open the DMG file
3. Drag "U2Be Down.app" to Applications folder
4. Launch from Launchpad or Applications

#### Via .app Bundle
```bash
# Download and install
wget https://github.com/fchevitarese/u2be_down/releases/latest/download/U2Be_Down.app.zip
unzip U2Be_Down.app.zip
mv "U2Be Down.app" /Applications/
```

### 🪟 Windows Installation

1. Download `u2be_down.exe`
2. Run the executable directly
3. (Optional) Add to PATH for command-line usage

## 🛠️ Build from Source

### Prerequisites

#### All Platforms
- **Python 3.8+**
- **FFmpeg** (for video/audio processing)

#### Platform-specific Setup

<details>
<summary><strong>🐧 Linux Setup</strong></summary>

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv ffmpeg git

# Arch Linux
sudo pacman -S python python-pip ffmpeg git

# CentOS/RHEL/Fedora
sudo dnf install python3 python3-pip ffmpeg git
```
</details>

<details>
<summary><strong>🍎 macOS Setup</strong></summary>

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 ffmpeg git

# Install Xcode Command Line Tools
xcode-select --install
```
</details>

<details>
<summary><strong>🪟 Windows Setup</strong></summary>

1. **Python**: Download from [python.org](https://www.python.org/downloads/)
2. **FFmpeg**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
3. **Git**: Download from [git-scm.com](https://git-scm.com/download/win)
</details>

### Clone and Setup

```bash
# Clone repository
git clone https://github.com/fchevitarese/u2be_down.git
cd u2be_down

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller
```

### Build Commands

#### 🐧 Linux Build

```bash
# Quick build
make build-linux

# Create all Linux packages
make installers

# Individual packages
make deb        # Create .deb package
make appimage   # Create AppImage

# Manual build
python3 -m PyInstaller --onefile --windowed \
    --name=u2be_down \
    --icon=assets/icon.png \
    --add-data="assets:assets" \
    gui.py
```

#### 🍎 macOS Build

```bash
# Automated build (recommended)
chmod +x build_macos.sh
./build_macos.sh

# Or via Makefile
make build-macos

# Manual build
python3 -m PyInstaller --onefile --windowed \
    --name="U2Be Down" \
    --icon=assets/icon.icns \
    --add-data="assets:assets" \
    --osx-bundle-identifier="com.u2bedown.app" \
    gui.py
```

#### 🪟 Windows Build

```bash
# On Windows
python -m PyInstaller --onefile --windowed ^
    --name=u2be_down ^
    --icon=assets/icon.ico ^
    --add-data="assets;assets" ^
    gui.py

# Or use batch file
build_windows.bat
```

### Generate Icons

```bash
# Generate icons for all platforms
chmod +x generate_icons.sh
./generate_icons.sh

# This creates:
# - assets/icon.ico (Windows)
# - assets/icon.icns (macOS)  
# - assets/icon_128.png (Linux)
```

## 🚀 Usage

### GUI Mode (Recommended)
```bash
# Run the application
python3 gui.py

# Or use installed version
u2be_down  # Linux/macOS
u2be_down.exe  # Windows
```

### Command Line Mode
```bash
# Download video
python3 main.py "https://youtube.com/watch?v=VIDEO_ID"

# Download as MP3
python3 main.py --mp3 "https://youtube.com/watch?v=VIDEO_ID"

# Custom output directory
python3 main.py -o "/path/to/downloads" "URL"

# Keep original video when converting to MP3
python3 main.py --mp3 --keep-video "URL"
```

## 🔧 Development

### Run in Development Mode
```bash
# Start GUI in development
python3 gui.py

# Run tests
make test

# Clean build artifacts
make clean
```

### Project Structure
```
u2be_down/
├── gui.py              # Main GUI application
├── main.py             # CLI interface  
├── config.py           # Configuration management
├── music_player.py     # Built-in music player
├── audio_processor.py  # Audio processing utilities
├── assets/             # Icons and resources
├── build_*.sh         # Build scripts
├── create_*.sh        # Package creation scripts
└── requirements.txt   # Python dependencies
```

## 🎯 CI/CD

The project includes GitHub Actions workflows for automatic building:

- **🐧 Linux**: Creates `.deb` packages and `AppImage`
- **🪟 Windows**: Creates standalone `.exe`
- **🍎 macOS**: Creates `.app` bundle and `.dmg` installer

Builds are triggered on:
- Push to `main` branch
- New tags (creates releases)
- Pull requests

## 📋 Dependencies

### Core Dependencies
- `yt-dlp` - YouTube video downloading
- `PyQt5` - GUI framework
- `moviepy` - Video/audio processing
- `pygame` - Audio playback
- `mutagen` - Audio metadata

### System Dependencies
- **FFmpeg** - Required for video/audio conversion
- **Python 3.8+** - Runtime environment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📚 **Documentation**: Check the [BUILD_MACOS.md](BUILD_MACOS.md) for macOS-specific instructions
- 🐛 **Issues**: Report bugs on [GitHub Issues](https://github.com/fchevitarese/u2be_down/issues)
- 💬 **Discussions**: Join conversations on [GitHub Discussions](https://github.com/fchevitarese/u2be_down/discussions)

## 🌟 Features in Development

- [ ] Batch download from playlists
- [ ] Download quality selection
- [ ] Subtitle download support
- [ ] Cloud storage integration
- [ ] Mobile app companion

---

Made with ❤️ for the YouTube downloading community

# Makefile para U2Be Down

.PHONY: help clean install-deps build-linux build-windows build-macos build-all test installers deb appimage icons

# Detectar sistema operacional
UNAME_S := $(shell uname -s)

# Default target
help:
	@echo "U2Be Down - Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  clean        - Clean build artifacts"
	@echo "  icons        - Generate icons for all platforms"
	@echo "  install-deps - Install build dependencies"
	@echo "  build-linux  - Build for Linux"
	@echo "  build-windows- Build for Windows (run on Windows)"
	@echo "  build-macos  - Build for macOS (run on macOS)"
	@echo "  build-all    - Build for current platform"
	@echo "  installers   - Create all installers for current platform"
	@echo "  deb          - Create .deb package (Linux)"
	@echo "  appimage     - Create AppImage (Linux)"
	@echo "  dmg          - Create DMG (macOS)"
	@echo "  test         - Run tests"
	@echo ""

# Generate icons for all platforms
icons:
	@echo "Generating icons for all platforms..."
	@./generate_icons.sh

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf dist/ build/ __pycache__/
	@rm -rf installer/ u2be-down_*/ *.deb *.tar.gz *.AppImage *.dmg
	@rm -f u2be_down.spec installer.nsi
	@rm -rf U2Be_Down.AppDir appimagetool-*.AppImage
	@rm -rf temp_icons/
	@echo "Clean completed."

# Install build dependencies
install-deps:
	@echo "Installing build dependencies..."
	@python3 -m pip install --upgrade pip
	@python3 -m pip install pyinstaller
	@python3 -m pip install -r requirements.txt
	@echo "Dependencies installed."

# Build for Linux
build-linux:
	@echo "Building for Linux..."
	@python3 simple_build.py

# Build for macOS
build-macos:
	@echo "Building for macOS..."
	@./build_macos.sh

# Build for current platform
build-all:
ifeq ($(UNAME_S),Linux)
	@make build-linux
endif
ifeq ($(UNAME_S),Darwin)
	@make build-macos
endif

# Create all installers for current platform
installers:
ifeq ($(UNAME_S),Linux)
	@make deb appimage
endif
ifeq ($(UNAME_S),Darwin)
	@make dmg
endif

# Create .deb package
deb: build-linux
	@echo "Creating .deb package..."
	@./create_deb.sh

# Create AppImage
appimage: build-linux
	@echo "Creating AppImage..."
	@./create_appimage.sh

# Create DMG (macOS only)
dmg: build-macos
	@echo "DMG creation is integrated in build-macos script"

# Create all installers
all-installers:
	@echo "Creating all installers..."
	@./create_installers.sh

# Build for Windows (to be run on Windows)
build-windows:
	@echo "Building for Windows..."
	@echo "Note: This should be run on Windows"
	@./build_windows.bat

# Run tests
test:
	@echo "Running tests..."
	@python3 -m pytest tests/ -v 2>/dev/null || echo "No tests found or pytest not installed"

# Run application in development mode
run:
	@echo "Running U2Be Down in development mode..."
	@python3 gui.py

# Install application locally
install: build-all
ifeq ($(UNAME_S),Linux)
	@echo "Installing on Linux..."
	@sudo dpkg -i *.deb 2>/dev/null || echo "Please run 'make deb' first"
endif
ifeq ($(UNAME_S),Darwin)
	@echo "Installing on macOS..."
	@cp -r "dist/U2Be Down.app" /Applications/ 2>/dev/null || echo "Please run 'make build-macos' first"
endif

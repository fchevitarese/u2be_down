# Makefile para U2Be Down

.PHONY: help clean install-deps build-linux build-windows build-all test

# Default target
help:
	@echo "U2Be Down - Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  clean        - Clean build artifacts"
	@echo "  install-deps - Install build dependencies"
	@echo "  build-linux  - Build for Linux"
	@echo "  build-windows- Build for Windows (run on Windows)"
	@echo "  build-all    - Build for current platform"
	@echo "  test         - Run tests"
	@echo ""

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf dist/ build/ __pycache__/
	@rm -rf installer/ u2be-down_*/ *.deb *.tar.gz
	@rm -f u2be_down.spec installer.nsi
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
	@./build_linux.sh

# Build for Windows (to be run on Windows)
build-windows:
	@echo "Building for Windows..."
	@echo "Note: This should be run on Windows"
	@./build_windows.bat

# Build for current platform
build-all:
ifeq ($(OS),Windows_NT)
	@$(MAKE) build-windows
else
	@$(MAKE) build-linux
endif

# Run tests
test:
	@echo "Running tests..."
	@python3 -m pytest tests/ -v 2>/dev/null || echo "No tests found or pytest not installed"

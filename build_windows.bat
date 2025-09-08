@echo off
REM Build script for Windows

echo Building U2Be Down for Windows...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Install build dependencies
echo Installing build dependencies...
python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install -r requirements.txt

REM Create the spec file
echo Creating PyInstaller spec file...
python -c "
spec_content = '''# -*- mode: python ; coding: utf-8 -*-

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
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
'''

with open('u2be_down.spec', 'w') as f:
    f.write(spec_content)
"

REM Build the executable
echo Building executable...
pyinstaller --clean u2be_down.spec

REM Create installer directory
if not exist "installer" mkdir installer
copy "dist\u2be_down.exe" "installer\"
if exist "config.json" copy "config.json" "installer\"
if exist "assets" xcopy "assets" "installer\assets\" /E /I

REM Create NSIS installer script
echo Creating NSIS installer script...
(
echo !include "MUI2.nsh"
echo.
echo Name "U2Be Down"
echo OutFile "U2BeDown_Setup.exe"
echo InstallDir "$PROGRAMFILES\U2BeDown"
echo InstallDirRegKey HKCU "Software\U2BeDown" ""
echo RequestExecutionLevel admin
echo.
echo !insertmacro MUI_PAGE_WELCOME
echo !insertmacro MUI_PAGE_DIRECTORY
echo !insertmacro MUI_PAGE_INSTFILES
echo !insertmacro MUI_PAGE_FINISH
echo.
echo !insertmacro MUI_UNPAGE_WELCOME
echo !insertmacro MUI_UNPAGE_CONFIRM
echo !insertmacro MUI_UNPAGE_INSTFILES
echo !insertmacro MUI_UNPAGE_FINISH
echo.
echo !insertmacro MUI_LANGUAGE "English"
echo.
echo Section "U2Be Down" SecMain
echo     SetOutPath "$INSTDIR"
echo     File "installer\u2be_down.exe"
echo     File "installer\config.json"
echo     File /nonfatal /r "installer\assets"
echo.
echo     ; Create shortcuts
echo     CreateDirectory "$SMPROGRAMS\U2Be Down"
echo     CreateShortcut "$SMPROGRAMS\U2Be Down\U2Be Down.lnk" "$INSTDIR\u2be_down.exe"
echo     CreateShortcut "$DESKTOP\U2Be Down.lnk" "$INSTDIR\u2be_down.exe"
echo.
echo     ; Registry entries
echo     WriteRegStr HKCU "Software\U2BeDown" "" $INSTDIR
echo     WriteUninstaller "$INSTDIR\Uninstall.exe"
echo SectionEnd
echo.
echo Section "Uninstall"
echo     Delete "$INSTDIR\u2be_down.exe"
echo     Delete "$INSTDIR\config.json"
echo     RMDir /r "$INSTDIR\assets"
echo     Delete "$INSTDIR\Uninstall.exe"
echo     RMDir "$INSTDIR"
echo.
echo     Delete "$SMPROGRAMS\U2Be Down\U2Be Down.lnk"
echo     RMDir "$SMPROGRAMS\U2Be Down"
echo     Delete "$DESKTOP\U2Be Down.lnk"
echo.
echo     DeleteRegKey /ifempty HKCU "Software\U2BeDown"
echo SectionEnd
) > installer.nsi

echo.
echo Build completed successfully!
echo.
echo Generated files:
echo - dist\u2be_down.exe (standalone executable)
echo - installer\ (installer files)
echo - installer.nsi (NSIS installer script)
echo.
echo To create Windows installer:
echo 1. Install NSIS from https://nsis.sourceforge.io/
echo 2. Right-click installer.nsi and select "Compile NSIS Script"
echo.
pause

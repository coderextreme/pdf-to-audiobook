#!/bin/bash -x
# Safe execution environment for bash
set -euo pipefail
IFS=$'\n\t'
VENV=audiobook_env
PYBIN=bin
PYTHON="$VENV/$PYBIN/python3.12"
PIP="$VENV/$PYBIN/pip3.12"

# Node.js setup
unset NODE_OPTIONS
echo Removing Node.js modules...
rm -rf node_modules
echo Installing Node.js package-lock.json ...
npm install --package-lock-only
echo Auditing Node.js modules...
npm audit
npm audit fix
echo Installing Node.js modules --ignore scripts...
npm ci --ignore-scripts
echo "Running electron install script"
node node_modules/electron/install.js

sudo dnf install -y xkeyboard-config fontconfig dbus-x11
fc-cache -f

# Python setup
sudo dnf install python312

# ffmpeg setup
sudo dnf install samba-client-libs samba-common-libs libsmbclient
sudo ldconfig
sudo dnf install ffmpeg

# pyinstaller setup
sudo dnf install objdump

# FUSE setup
sudo dnf install fuse fuse-libs  # if it's a Fedora-based distrobox

# NSPR/NSS setup
sudo dnf install nss nspr atk at-spi2-atk cups-libs libdrm libxkbcommon mesa-libgbm alsa-lib

echo Removing virtual environment and recreating...
rm -rf "$VENV"
python3.12 -m venv "$VENV"
source "$VENV/$PYBIN/activate"
echo Installing needed Python packages...
$PYTHON -m pip install --upgrade pip setuptools wheel
$PYTHON -m spacy download en_core_web_sm || echo "Couldn't find spacy"

$PIP install .
$PIP install pyinstaller
$PYTHON -m spacy download en_core_web_sm
$PIP uninstall torch torchaudio -y
# $PIP install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
$PIP install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

export NLTK_DISABLE_IMPORT_SECURITY=1
$PYTHON -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
$PIP install pip-audit
echo Doing Python security audit...
pip-audit || echo "========  Audit failed!  Check results"
pyinstaller --log-level WARN --collect-all spacy --collect-all en_core_web_sm --copy-metadata en_core_web_sm --copy-metadata spacy --collect-all thinc --collect-all srsly --collect-all spacy_legacy --collect-all spacy_loggers --collect-all cymem --collect-all preshed --collect-all murmurhash --collect-all blis --collect-all catalogue --collect-all wasabi --collect-all weasel --collect-all confection --collect-all espeakng_loader --collect-all kokoro --collect-all misaki --collect-all transformers --collect-all language_tags --collect-data espeakng_loader --copy-metadata torch --copy-metadata tqdm --copy-metadata regex --copy-metadata requests --copy-metadata packaging --copy-metadata filelock --copy-metadata numpy --copy-metadata tokenizers --onedir PDF_to_Audiobook.py
echo Running graphical user interface
npm run dev

npm run build       # compile TypeScript + bundle Vite
echo Packaging TypeScript into release .exe
npm run package     # wrap with electron-builder (auto-detects platform)
#npm run package:win
#npm run package:mac
#npm run package:linux
"release/PDF to Audiobook-2.0.0.AppImage"

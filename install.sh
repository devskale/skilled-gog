#!/bin/bash
#
# Google Workspace Tools Installer
# Usage: curl -fsSL https://gworkspace.skale.dev/install.sh | bash
#
# Installs the gworkspace CLI for Google Docs, Sheets, and Gmail operations.
#

set -e

REPO_URL="https://github.com/devskale/skilled-gog.git"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.gworkspace}"
BIN_DIR="${BIN_DIR:-$HOME/.local/bin}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

check_command() {
    if ! command -v "$1" &> /dev/null; then
        return 1
    fi
    return 0
}

install_uv() {
    info "Installing uv..."
    if check_command curl; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif check_command wget; then
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
        error "Neither curl nor wget found. Please install one of them first."
    fi

    # Add uv to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"
}

main() {
    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║   Google Workspace Tools Installer         ║"
    echo "╚════════════════════════════════════════════╝"
    echo ""

    # Check for uv
    if ! check_command uv; then
        warn "uv not found."
        install_uv
    fi

    # Verify uv is available
    UV_PATH=$(command -v uv || echo "$HOME/.local/bin/uv")
    if [ ! -x "$UV_PATH" ]; then
        export PATH="$HOME/.local/bin:$PATH"
        UV_PATH="$HOME/.local/bin/uv"
    fi

    if [ ! -x "$UV_PATH" ]; then
        error "uv installation failed. Please install uv manually: https://docs.astral.sh/uv/"
    fi

    info "Using uv at: $UV_PATH"

    # Create install directory
    info "Creating install directory: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"

    # Clone or update repository
    if [ -d "$INSTALL_DIR/.git" ]; then
        info "Updating existing installation..."
        cd "$INSTALL_DIR"
        git pull --quiet
    else
        info "Cloning repository..."
        rm -rf "$INSTALL_DIR"
        git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi

    # Install dependencies
    info "Installing dependencies..."
    "$UV_PATH" sync --quiet

    # Create wrapper script
    info "Creating gworkspace CLI wrapper..."
    cat > "$BIN_DIR/gworkspace" << 'WRAPPER'
#!/bin/bash
set -e
cd "$HOME/.gworkspace"
uv run gworkspace "$@"
WRAPPER
    chmod +x "$BIN_DIR/gworkspace"

    # Create convenience wrappers
    for cmd in gdocs gsheets gmail; do
        cat > "$BIN_DIR/$cmd" << WRAPPER
#!/bin/bash
set -e
cd "$HOME/.gworkspace"
uv run gworkspace ${cmd#g} "\$@"
WRAPPER
        chmod +x "$BIN_DIR/$cmd"
    done

    # Check if BIN_DIR is in PATH
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        warn "$BIN_DIR is not in your PATH."
        echo ""
        echo "Add this to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
        echo ""
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo ""
        echo "Then restart your shell or run: source ~/.bashrc"
    fi

    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║          Installation Complete             ║"
    echo "╚════════════════════════════════════════════╝"
    echo ""
    echo "Installed commands:"
    echo "  gworkspace    - Main CLI"
    echo "  gdocs         - Google Docs"
    echo "  gsheets       - Google Sheets"
    echo "  gmail         - Gmail"
    echo ""
    echo "Install directory: $INSTALL_DIR"
    echo ""
    echo "Next steps:"
    echo "  1. Place your OAuth credentials in $INSTALL_DIR/client_secrets.json"
    echo "  2. Run: gworkspace docs recent 10"
    echo "  3. Authenticate when prompted"
    echo ""
    echo "For credentials setup, see:"
    echo "  https://console.cloud.google.com/apis/credentials?project=667256544145"
    echo ""
}

main "$@"

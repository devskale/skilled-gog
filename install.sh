#!/bin/bash
#
# Google Workspace Tools Installer
# Usage: curl -fsSL https://skale.dev/skilled-google/install.sh | bash
#
# Installs the gworkspace CLI for Google Docs, Sheets, and Gmail operations.
#

set -euo pipefail

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

check_command() { command -v "$1" >/dev/null 2>&1; }

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

resolve_uv_path() {
    if check_command uv; then
        command -v uv
        return
    fi
    if [ -x "$HOME/.local/bin/uv" ]; then
        echo "$HOME/.local/bin/uv"
        return
    fi
    return 1
}

create_wrapper() {
    local target="$1"
    local service="$2"
    local install_dir="$3"
    cat > "$target" <<WRAPPER
#!/bin/bash
set -euo pipefail
INSTALL_DIR="$install_dir"
if command -v uv >/dev/null 2>&1; then
  UV_BIN="\$(command -v uv)"
elif [ -x "\$HOME/.local/bin/uv" ]; then
  UV_BIN="\$HOME/.local/bin/uv"
else
  echo "uv not found. Install uv first: https://docs.astral.sh/uv/" >&2
  exit 1
fi
cd "\$INSTALL_DIR"
exec "\$UV_BIN" run gworkspace $service "\$@"
WRAPPER
    chmod +x "$target"
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
    UV_PATH="$(resolve_uv_path || true)"
    if [ -z "${UV_PATH:-}" ] || [ ! -x "$UV_PATH" ]; then
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
        git fetch --quiet origin
        git reset --quiet --hard origin/main
    else
        info "Cloning repository..."
        rm -rf "$INSTALL_DIR"
        git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi

    # Install dependencies
    info "Installing dependencies..."
    "$UV_PATH" sync --quiet

    # Create wrapper scripts
    info "Creating CLI wrappers..."
    create_wrapper "$BIN_DIR/gworkspace" "" "$INSTALL_DIR"
    create_wrapper "$BIN_DIR/gdocs" "docs" "$INSTALL_DIR"
    create_wrapper "$BIN_DIR/gsheets" "sheets" "$INSTALL_DIR"
    create_wrapper "$BIN_DIR/gmail" "gmail" "$INSTALL_DIR"

    # Check if BIN_DIR is in PATH
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        warn "$BIN_DIR is not in your PATH."
        echo ""
        echo "Add this to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
        echo ""
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo ""
        echo "Then restart your shell or run: source ~/.zshrc"
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

#!/bin/bash
#
# Google Workspace Skill Installer
# Usage: curl -fsSL https://skale.dev/install-gog-skill.sh | bash
#
# Installs the google-workspace skill for AI agents (pi, Claude, etc.)
#

set -euo pipefail

SKILL_DIR="${SKILL_DIR:-$HOME/.pi/agent/skills/google-workspace}"
GITHUB_REPO="https://github.com/devskale/skilled-gog"
TOOLS_DIR="${TOOLS_DIR:-$HOME/.gworkspace}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

install_skill() {
    info "Installing google-workspace skill..."

    # Create skill directory
    mkdir -p "$SKILL_DIR"

    # Download SKILL.md from GitHub
    info "Downloading skill from GitHub..."
    curl -fsSL "$GITHUB_REPO/raw/main/.agents/skills/google-workspace/SKILL.md" \
        -o "$SKILL_DIR/SKILL.md"

    # Download template files
    curl -fsSL "$GITHUB_REPO/raw/main/.agents/skills/google-workspace/.gitignore" \
        -o "$SKILL_DIR/.gitignore" 2>/dev/null || true

    curl -fsSL "$GITHUB_REPO/raw/main/.agents/skills/google-workspace/client_secrets.json.template" \
        -o "$SKILL_DIR/client_secrets.json.template" 2>/dev/null || true

    info "Skill installed to: $SKILL_DIR"
}

install_tools() {
    info "Installing Google Workspace tools..."

    # Check if already installed
    if [ -d "$TOOLS_DIR/.git" ]; then
        info "Tools already installed at $TOOLS_DIR"
        read -p "Update existing installation? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cd "$TOOLS_DIR"
            git pull
            uv sync --quiet
            info "Tools updated."
        fi
        return
    fi

    # Clone repository
    info "Cloning repository..."
    rm -rf "$TOOLS_DIR"
    git clone --depth 1 "$GITHUB_REPO.git" "$TOOLS_DIR"
    cd "$TOOLS_DIR"

    # Install dependencies
    info "Installing dependencies..."
    uv sync --quiet

    info "Tools installed to: $TOOLS_DIR"
}

link_to_project() {
    local project_dir="${1:-.}"

    if [ ! -d "$project_dir/.agents/skills" ]; then
        mkdir -p "$project_dir/.agents/skills"
    fi

    local skill_link="$project_dir/.agents/skills/google-workspace"

    if [ -L "$skill_link" ]; then
        info "Skill already linked in $project_dir"
        return
    fi

    if [ -e "$skill_link" ]; then
        warn "Removing existing skill directory..."
        rm -rf "$skill_link"
    fi

    ln -s "$SKILL_DIR" "$skill_link"
    info "Skill linked to: $skill_link"
}

main() {
    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║   Google Workspace Skill Installer         ║"
    echo "╚════════════════════════════════════════════╝"
    echo ""

    # Install skill
    install_skill

    # Ask to install tools
    echo ""
    read -p "Install Google Workspace tools (~/.gworkspace)? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        install_tools
    fi

    # Ask to link to current project
    echo ""
    read -p "Link skill to current directory? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        link_to_project "$(pwd)"
    fi

    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║          Installation Complete             ║"
    echo "╚════════════════════════════════════════════╝"
    echo ""
    echo "Skill location: $SKILL_DIR"
    echo "Tools location: $TOOLS_DIR"
    echo ""
    echo "Next steps:"
    echo "  1. Add OAuth credentials: $TOOLS_DIR/client_secrets.json"
    echo "  2. Test: cd $TOOLS_DIR && uv run gworkspace docs recent 5"
    echo ""
    echo "To install in another project:"
    echo "  ln -s $SKILL_DIR .agents/skills/google-workspace"
    echo ""
}

main "$@"

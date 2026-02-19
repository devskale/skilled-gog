#!/bin/bash
#
# Google Workspace Skill Installer
# Usage: curl -fsSL https://skale.dev/install-gog-skill.sh | bash
#
# Installs the google-workspace skill for AI agents (pi, opencode, etc.)
#

set -euo pipefail

GITHUB_REPO="https://github.com/devskale/skilled-gog"
TOOLS_DIR="$HOME/.gworkspace"

# Default: global install for pi
AGENT="${AGENT:-pi}"
SCOPE="${SCOPE:-global}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

usage() {
    echo "Usage: curl -fsSL https://skale.dev/install-gog-skill.sh | bash -s -- [options]"
    echo ""
    echo "Options:"
    echo "  --agent <pi|opencode>    AI agent (default: pi)"
    echo "  --scope <global|local>   Global (~/.pi) or local (./.agents) (default: global)"
    echo "  --tools                  Also install gworkspace tools (~/.gworkspace)"
    echo "  --update                 Update existing installation"
    echo "  -h, --help               Show this help"
    echo ""
    echo "Examples:"
    echo "  # Global install for pi"
    echo "  curl -fsSL https://skale.dev/install-gog-skill.sh | bash"
    echo ""
    echo "  # Local install for current project"
    echo "  curl -fsSL https://skale.dev/install-gog-skill.sh | bash -s -- --scope local"
    echo ""
    echo "  # Install for opencode"
    echo "  curl -fsSL https://skale.dev/install-gog-skill.sh | bash -s -- --agent opencode"
    echo ""
    echo "  # Install everything (skill + tools)"
    echo "  curl -fsSL https://skale.dev/install-gog-skill.sh | bash -s -- --tools"
    exit 0
}

get_skill_dir() {
    case "$AGENT" in
        pi)
            if [ "$SCOPE" = "global" ]; then
                echo "$HOME/.pi/agent/skills/google-workspace"
            else
                echo "$(pwd)/.agents/skills/google-workspace"
            fi
            ;;
        opencode)
            if [ "$SCOPE" = "global" ]; then
                echo "$HOME/.opencode/skills/google-workspace"
            else
                echo "$(pwd)/.opencode/skills/google-workspace"
            fi
            ;;
        *)
            error "Unknown agent: $AGENT"
            ;;
    esac
}

install_skill() {
    local skill_dir="$1"

    info "Installing google-workspace skill to: $skill_dir"

    mkdir -p "$skill_dir"

    # Download files from GitHub
    curl -fsSL "$GITHUB_REPO/raw/main/.agents/skills/google-workspace/SKILL.md" \
        -o "$skill_dir/SKILL.md"

    curl -fsSL "$GITHUB_REPO/raw/main/.agents/skills/google-workspace/.gitignore" \
        -o "$skill_dir/.gitignore" 2>/dev/null || true

    curl -fsSL "$GITHUB_REPO/raw/main/.agents/skills/google-workspace/client_secrets.json.template" \
        -o "$skill_dir/client_secrets.json.template" 2>/dev/null || true

    info "Skill installed successfully"
}

install_tools() {
    info "Installing Google Workspace tools to: $TOOLS_DIR"

    if [ -d "$TOOLS_DIR/.git" ]; then
        info "Tools already installed. Updating..."
        cd "$TOOLS_DIR"
        git pull
        uv sync --quiet
        info "Tools updated."
    else
        rm -rf "$TOOLS_DIR"
        git clone --depth 1 "$GITHUB_REPO.git" "$TOOLS_DIR"
        cd "$TOOLS_DIR"
        uv sync --quiet
        info "Tools installed."
    fi
}

update_installation() {
    local skill_dir="$1"

    info "Updating installation..."

    # Update skill
    if [ -d "$skill_dir" ]; then
        curl -fsSL "$GITHUB_REPO/raw/main/.agents/skills/google-workspace/SKILL.md" \
            -o "$skill_dir/SKILL.md"
        info "Skill updated."
    fi

    # Update tools
    if [ -d "$TOOLS_DIR/.git" ]; then
        cd "$TOOLS_DIR"
        git pull && uv sync --quiet
        info "Tools updated."
    fi
}

main() {
    local install_tools_flag=false
    local update_flag=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --agent)
                AGENT="$2"
                shift 2
                ;;
            --scope)
                SCOPE="$2"
                shift 2
                ;;
            --tools)
                install_tools_flag=true
                shift
                ;;
            --update)
                update_flag=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done

    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║   Google Workspace Skill Installer         ║"
    echo "╚════════════════════════════════════════════╝"
    echo ""
    echo "Agent: $AGENT"
    echo "Scope: $SCOPE"
    echo ""

    local skill_dir
    skill_dir=$(get_skill_dir)

    if [ "$update_flag" = true ]; then
        update_installation "$skill_dir"
        exit 0
    fi

    # Install skill
    install_skill "$skill_dir"

    # Install tools if requested
    if [ "$install_tools_flag" = true ]; then
        install_tools
    fi

    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║          Installation Complete             ║"
    echo "╚════════════════════════════════════════════╝"
    echo ""
    echo "Skill: $skill_dir"
    echo "Tools: $TOOLS_DIR"
    echo ""
    echo "Next steps:"
    echo "  1. Add OAuth credentials:"
    echo "     cp $skill_dir/client_secrets.json.template $TOOLS_DIR/client_secrets.json"
    echo "     # Edit with your Google Cloud OAuth credentials"
    echo ""
    echo "  2. Test:"
    echo "     cd $TOOLS_DIR && uv run gworkspace docs recent 5"
    echo ""
    echo "Update:"
    echo "  curl -fsSL https://skale.dev/install-gog-skill.sh | bash -s -- --update"
    echo ""
}

main "$@"

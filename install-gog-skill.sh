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

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
prompt() { echo -e -n "${BLUE}[?]:${NC} $1"; }

check_uv() {
    if command -v uv &>/dev/null; then
        return 0
    fi
    if [ -x "$HOME/.local/bin/uv" ]; then
        export PATH="$HOME/.local/bin:$PATH"
        return 0
    fi
    return 1
}

install_uv() {
    info "Installing uv..."
    if command -v curl &>/dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif command -v wget &>/dev/null; then
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
        error "Neither curl nor wget found. Please install one first."
    fi
    export PATH="$HOME/.local/bin:$PATH"
}

get_skill_dir() {
    local agent="$1"
    local scope="$2"

    case "$agent" in
        pi)
            if [ "$scope" = "global" ]; then
                echo "$HOME/.pi/agent/skills/google-workspace"
            else
                echo "$(pwd)/.agents/skills/google-workspace"
            fi
            ;;
        opencode)
            if [ "$scope" = "global" ]; then
                echo "$HOME/.opencode/skills/google-workspace"
            else
                echo "$(pwd)/.opencode/skills/google-workspace"
            fi
            ;;
        *)
            error "Unknown agent: $agent"
            ;;
    esac
}

install_skill() {
    local skill_dir="$1"

    info "Installing skill to: $skill_dir"
    mkdir -p "$skill_dir"

    curl -fsSL "$GITHUB_REPO/raw/main/.agents/skills/google-workspace/SKILL.md" \
        -o "$skill_dir/SKILL.md"

    curl -fsSL "$GITHUB_REPO/raw/main/.agents/skills/google-workspace/.gitignore" \
        -o "$skill_dir/.gitignore" 2>/dev/null || true

    curl -fsSL "$GITHUB_REPO/raw/main/.agents/skills/google-workspace/client_secrets.json.template" \
        -o "$skill_dir/client_secrets.json.template" 2>/dev/null || true

    info "Skill installed successfully"
}

install_tools() {
    info "Installing tools to: $TOOLS_DIR"

    if [ -d "$TOOLS_DIR/.git" ]; then
        info "Updating existing installation..."
        cd "$TOOLS_DIR"
        git pull
        uv sync --quiet
    else
        rm -rf "$TOOLS_DIR"
        git clone --depth 1 "$GITHUB_REPO.git" "$TOOLS_DIR"
        cd "$TOOLS_DIR"
        uv sync --quiet
    fi
    info "Tools installed successfully"
}

update_installation() {
    local skill_dir="$1"

    info "Updating..."

    # Update skill
    if [ -f "$skill_dir/SKILL.md" ]; then
        curl -fsSL "$GITHUB_REPO/raw/main/.agents/skills/google-workspace/SKILL.md" \
            -o "$skill_dir/SKILL.md"
        info "Skill updated"
    else
        warn "Skill not found at $skill_dir"
    fi

    # Update tools
    if [ -d "$TOOLS_DIR/.git" ]; then
        cd "$TOOLS_DIR"
        git pull && uv sync --quiet
        info "Tools updated"
    else
        warn "Tools not found at $TOOLS_DIR"
    fi
}

select_option() {
    local prompt_text="$1"
    shift
    local options=("$@")
    local default="${options[0]}"

    # If set via environment variable, use it
    case "$prompt_text" in
        *"Agent"*)
            if [ -n "${AGENT:-}" ]; then
                echo "$AGENT"
                return
            fi
            ;;
        *"Scope"*)
            if [ -n "${SCOPE:-}" ]; then
                echo "$SCOPE"
                return
            fi
            ;;
        *"tools"*)
            if [ -n "${TOOLS:-}" ]; then
                echo "$TOOLS"
                return
            fi
            ;;
    esac

    echo ""
    echo "$prompt_text"
    local i=1
    for opt in "${options[@]}"; do
        echo "  $i) $opt"
        ((i++))
    done
    echo ""

    prompt "Select [1-${#options[@]}] (default: $default): "
    read -r choice

    if [ -z "$choice" ]; then
        echo "$default"
        return
    fi

    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#options[@]} ]; then
        echo "${options[$((choice-1))]}"
    else
        echo "$default"
    fi
}

select_yesno() {
    local prompt_text="$1"
    local default="${2:-n}"

    prompt "$prompt_text [y/N]: "
    read -r choice

    if [ -z "$choice" ]; then
        echo "$default"
        return
    fi

    case "$choice" in
        [Yy]*) echo "y" ;;
        *) echo "n" ;;
    esac
}

main() {
    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║     Google Workspace Skill Installer       ║"
    echo "╚════════════════════════════════════════════╝"
    echo ""

    # Check for existing installation
    local existing_skill=""
    for dir in "$HOME/.pi/agent/skills/google-workspace" \
               "$HOME/.opencode/skills/google-workspace" \
               "$(pwd)/.agents/skills/google-workspace"; do
        if [ -f "$dir/SKILL.md" ]; then
            existing_skill="$dir"
            break
        fi
    done

    # Ask to update if exists
    if [ -n "$existing_skill" ] || [ -d "$TOOLS_DIR/.git" ]; then
        echo "Found existing installation:"
        [ -n "$existing_skill" ] && echo "  - Skill: $existing_skill"
        [ -d "$TOOLS_DIR/.git" ] && echo "  - Tools: $TOOLS_DIR"
        echo ""

        local update_choice
        update_choice=$(select_yesno "Update existing installation?" "y")
        if [ "$update_choice" = "y" ]; then
            if [ -z "$existing_skill" ]; then
                existing_skill=$(get_skill_dir "pi" "global")
            fi
            update_installation "$existing_skill"
            echo ""
            echo "Update complete!"
            exit 0
        fi
        echo ""
    fi

    # Interactive prompts
    local agent scope install_tools_choice

    agent=$(select_option "Which AI agent?" "pi" "opencode")
    scope=$(select_option "Install scope?" "global" "local")
    install_tools_choice=$(select_yesno "Also install gworkspace tools (~/.gworkspace)?" "y")

    local skill_dir
    skill_dir=$(get_skill_dir "$agent" "$scope")

    echo ""
    echo "Summary:"
    echo "  Agent: $agent"
    echo "  Scope: $scope"
    echo "  Skill: $skill_dir"
    [ "$install_tools_choice" = "y" ] && echo "  Tools: $TOOLS_DIR"
    echo ""

    local confirm
    confirm=$(select_yesno "Proceed with installation?" "y")
    if [ "$confirm" != "y" ]; then
        echo "Aborted."
        exit 0
    fi

    # Check/install uv if tools requested
    if [ "$install_tools_choice" = "y" ]; then
        if ! check_uv; then
            install_uv
        fi
    fi

    # Install
    install_skill "$skill_dir"

    if [ "$install_tools_choice" = "y" ]; then
        install_tools
    fi

    echo ""
    echo "╔════════════════════════════════════════════╗"
    echo "║          Installation Complete             ║"
    echo "╚════════════════════════════════════════════╝"
    echo ""
    echo "Skill: $skill_dir"
    [ "$install_tools_choice" = "y" ] && echo "Tools: $TOOLS_DIR"
    echo ""
    echo "Next steps:"
    echo "  1. Get OAuth credentials from Google Cloud Console"
    echo "  2. Save as: $TOOLS_DIR/client_secrets.json"
    echo "  3. Test: cd $TOOLS_DIR && uv run gworkspace docs recent 5"
    echo ""
    echo "To update later, run this installer again."
    echo ""
}

main "$@"

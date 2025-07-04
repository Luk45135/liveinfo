#!/usr/bin/env bash

set -euo pipefail
trap 'echo "❌ Script failed on line $LINENO"; exit 1' ERR

# Check if Nix is installed
check_nix_installed() {
    if ! command -v nix &> /dev/null; then
        echo "❌ Nix is not installed. Installing it now..."
        sh <(curl --proto '=https' --tlsv1.2 -L https://nixos.org/nix/install) --no-daemon
        echo
        echo "✅ Nix installed. Please restart your shell or source the environment:"
        # echo "   source ~/.nix-profile/etc/profile.d/nix.sh"
        exit 1
    fi
}

# Ensure nix.conf has both nix-command and flakes enabled
ensure_nix_config() {
    echo "🔍 Ensuring nix.conf has flakes support..."

    local conf_path="${XDG_CONFIG_HOME:-$HOME/.config}/nix/nix.conf"
    mkdir -p "$(dirname "$conf_path")"
    touch "$conf_path"

    echo "📄 Using nix.conf at: $conf_path"

    local experimental_line
    experimental_line=$(grep -E '^\s*experimental-features\s*=' "$conf_path" 2>/dev/null || true)

    echo "📌 Current config: '$experimental_line'"

    if [[ "$experimental_line" == *nix-command* && "$experimental_line" == *flakes* ]]; then
        echo "✅ nix-command and flakes already enabled."
        return
    fi

    echo "🔧 Patching nix.conf..."

    # Filter out the existing line (if any)
    grep -v -E '^\s*experimental-features\s*=' "$conf_path" > "${conf_path}.new" || true

    # Append correct line
    echo 'experimental-features = nix-command flakes' >> "${conf_path}.new"

    # Replace original file
    mv "${conf_path}.new" "$conf_path"

    echo "✅ Updated nix.conf"
}

main() {
    check_nix_installed
    ensure_nix_config

    echo "🚧 Building the Nix project..."
    nix build .

    echo "✅ Build completed successfully."
}

main "$@"


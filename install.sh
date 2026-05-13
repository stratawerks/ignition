#!/usr/bin/env bash
# StrataOS Ignition — Install Script
# Usage: curl -fsSL <url>/install.sh | bash

set -euo pipefail

INSTALL_DIR="/home/oliver/setup-wizard"
SERVICE_DIR="/home/oliver/.config/systemd/user"
SERVICE_NAME="ignition"
PORT=18792
RELEASE_URL="https://github.com/stratawerks/ignition/releases/latest/download/ignition.tar.gz"
FALLBACK_URL="https://raw.githubusercontent.com/stratawerks/ignition/main/ignition.tar.gz"
LOG="/tmp/ignition-install.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[ignition]${NC} $1"; }
warn() { echo -e "${YELLOW}[ignition]${NC} $1"; }
fail() { echo -e "${RED}[ignition]${NC} $1"; exit 1; }

echo ""
echo "  StrataOS Ignition — Setup Wizard Installer"
echo "  ─────────────────────────────────────────────"
echo ""

# ── 1. Download ──────────────────────────────────────────
log "Downloading Ignition..."

TMP_TAR="/tmp/ignition.tar.gz"

if curl -fsSL --connect-timeout 10 "$RELEASE_URL" -o "$TMP_TAR" 2>/dev/null; then
    log "Downloaded from release channel."
elif curl -fsSL --connect-timeout 5 "$FALLBACK_URL" -o "$TMP_TAR" 2>/dev/null; then
    warn "Used local fallback server."
else
    fail "Could not download Ignition. Check your network connection."
fi

# ── 2. Extract ───────────────────────────────────────────
log "Installing to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
tar xzf "$TMP_TAR" -C "$INSTALL_DIR"
rm -f "$TMP_TAR"

# Verify install
[[ -f "$INSTALL_DIR/app/main.py" ]] || fail "Install failed — app/main.py not found."
log "Files installed."

# ── 3. Create systemd service ────────────────────────────
log "Creating autostart service..."
mkdir -p "$SERVICE_DIR"

# Find nix-shell full path (NixOS services don't inherit user PATH)
NIX_SHELL_BIN=$(which nix-shell 2>/dev/null || \
    ls /run/current-system/sw/bin/nix-shell 2>/dev/null || \
    ls /nix/var/nix/profiles/default/bin/nix-shell 2>/dev/null || \
    find /nix -name nix-shell -type f 2>/dev/null | head -1 || \
    echo "nix-shell")

cat > "$SERVICE_DIR/${SERVICE_NAME}.service" << EOF
[Unit]
Description=StrataOS Ignition Setup Wizard
After=network-online.target openclaw-gateway.service
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${INSTALL_DIR}
ExecStart=/bin/sh -c 'export PATH="/home/oliver/.npm-global/bin:/run/current-system/sw/bin:/nix/var/nix/profiles/default/bin:\$PATH" && cd ${INSTALL_DIR} && ${NIX_SHELL_BIN} -p python3Packages.flask python3Packages.requests --run "python -m app.main"'
Restart=on-failure
RestartSec=10
StandardOutput=append:/tmp/ignition.log
StandardError=append:/tmp/ignition.log
Environment=WIZARD_PORT=${PORT}
Environment=WIZARD_HOST=0.0.0.0
Environment=HOME=/home/oliver

[Install]
WantedBy=default.target
EOF

# ── 4. Enable and start ──────────────────────────────────
log "Starting Ignition..."

# Kill any existing instance on this port
ss -tlnp 2>/dev/null | grep ":${PORT}" | awk '{print $NF}' | grep -oP 'pid=\K[0-9]+' | xargs -r kill 2>/dev/null || true

systemctl --user daemon-reload
systemctl --user enable "$SERVICE_NAME" 2>/dev/null || true
systemctl --user start "$SERVICE_NAME" 2>/dev/null || {
    # systemd not available — start directly
    warn "systemd not available, starting directly..."
    nohup "$NIX_SHELL_BIN" -p python3Packages.flask python3Packages.requests \
        --run "python -m app.main" \
        > /tmp/ignition.log 2>&1 &
    echo $! > /tmp/ignition.pid
}

# ── 5. Wait for ready ────────────────────────────────────
log "Waiting for Ignition to start..."
ATTEMPTS=0
until curl -sf "http://localhost:${PORT}/" -o /dev/null -w "" 2>/dev/null || [ $ATTEMPTS -ge 30 ]; do
    sleep 2
    ATTEMPTS=$((ATTEMPTS + 1))
done

# ── 6. Done ──────────────────────────────────────────────
echo ""
echo "  ─────────────────────────────────────────────"

# Get LAN IP
LAN_IP=$(ip route get 1 2>/dev/null | awk '{print $7; exit}' || hostname -I 2>/dev/null | awk '{print $1}')

if curl -sf "http://localhost:${PORT}/" -o /dev/null 2>/dev/null; then
    echo -e "  ${GREEN}✓ Ignition is running!${NC}"
    echo ""
    echo "  Open this URL in your browser:"
    echo ""
    echo -e "    ${GREEN}http://${LAN_IP}:${PORT}${NC}"
    echo ""
    echo "  Complete the setup wizard to configure your agent."
else
    warn "Ignition may still be starting (nix-shell takes 1-2 minutes)."
    echo ""
    echo "  Once ready, open:"
    echo ""
    echo "    http://${LAN_IP}:${PORT}"
    echo ""
    echo "  Check progress: tail -f /tmp/ignition.log"
fi

echo "  ─────────────────────────────────────────────"
echo ""

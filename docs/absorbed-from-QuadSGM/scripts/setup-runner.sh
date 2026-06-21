#!/usr/bin/env bash
# Self-Hosted Runner Setup Script for 4sgm
# Run this on your local machine to set up CI runners
# Usage: ./scripts/setup-runner.sh

set -euo pipefail

REPO="KooshaPari/4sgm"
RUNNER_DIR="${HOME}/.4sgm-runner"
GH_TOKEN="${GH_RUNNER_TOKEN:-$(gh auth token)}"

echo "=== 4sgm Self-Hosted Runner Setup ==="
echo "Repository: ${REPO}"
echo "Runner directory: ${RUNNER_DIR}"

# Create runner directory
mkdir -p "${RUNNER_DIR}"
cd "${RUNNER_DIR}"

# Download runner if not exists
if [[ ! -f "./actions-runner.tar.gz" ]]; then
    echo "Downloading GitHub Actions runner..."
    curl -L -o actions-runner.tar.gz "https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-osx-arm64-2.321.0.tar.gz"
fi

# Extract
echo "Extracting runner..."
tar xzf actions-runner.tar.gz

# Configure runner
echo "Configuring runner..."
./config.sh \
    --url "https://github.com/${REPO}" \
    --token "${GH_TOKEN}" \
    --name "4sgm-local-runner" \
    --labels "self-hosted,local" \
    --unattended

# Create launchd plist for macOS auto-start
echo "Creating launchd service..."
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/com.4sgm.runner.plist <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.4sgm.runner</string>
    <key>ProgramArguments</key>
    <array>
        <string>${RUNNER_DIR}/run.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Start the runner
echo "Starting runner..."
launchctl load ~/Library/LaunchAgents/com.4sgm.runner.plist 2>/dev/null || true
./run.sh &

echo "=== Runner setup complete ==="
echo "Runner should now be visible in: https://github.com/${REPO}/settings/actions/runners"

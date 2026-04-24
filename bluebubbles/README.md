# BlueBubbles iMessage Forwarder

Deploys a local iMessage REST API + webhook bridge on a macOS host, reachable
over Tailnet. Produced from audit #239.

Wraps: [BlueBubblesApp/bluebubbles-server](https://github.com/BlueBubblesApp/bluebubbles-server)
v1.9.9 (MIT). No fork — vanilla install, configured via its built-in UI.

## Components

| Artifact | Path | Purpose |
|----------|------|---------|
| BlueBubbles Server.app | `/Applications/BlueBubbles.app` | iMessage REST API (default `:1234`) |
| Webhook receiver | `webhook.py` | Ingests inbound events to `~/.phenotype/imessage-inbound.jsonl` |
| Tailscale ACL snippet | `tailscale-acl.json` | Gates ports `1234` and `8787` to tailnet owner |

## Install

1. **Download + copy app** (automated):

   ```bash
   curl -L -o ~/Downloads/BlueBubblesServer.dmg \
     https://github.com/BlueBubblesApp/bluebubbles-server/releases/latest/download/BlueBubbles-<ver>-arm64.dmg
   hdiutil attach ~/Downloads/BlueBubblesServer.dmg
   cp -R "/Volumes/BlueBubbles/BlueBubbles.app" /Applications/
   hdiutil detach "/Volumes/BlueBubbles"
   ```

2. **Grant macOS permissions** (manual — TCC wall, cannot be automated):
   - System Settings -> Privacy & Security -> **Full Disk Access** -> add `BlueBubbles`
   - System Settings -> Privacy & Security -> **Contacts** -> enable for `BlueBubbles`
   - System Settings -> Privacy & Security -> **Accessibility** -> enable for `BlueBubbles`
   - System Settings -> Privacy & Security -> **Automation** -> allow `BlueBubbles` to control `Messages`

3. **Configure server** (first launch):
   - Set a server password (write it down; used as API auth)
   - Bind: `0.0.0.0` (Tailscale ACL gates access)
   - Port: `1234` (default)
   - Disable ngrok/Cloudflare tunneling — Tailnet is the transport

4. **Paste ACL** (Tailscale admin console): see `tailscale-acl.json`.

5. **Start webhook receiver**:

   ```bash
   pip install aiohttp  # one-time
   python3 webhook.py
   # or: BB_WEBHOOK_HOST=0.0.0.0 python3 webhook.py
   ```

   Then in BlueBubbles Server UI -> Settings -> Webhooks, add
   `http://127.0.0.1:8787/bluebubbles`.

## Smoke Tests

Send a message:

```bash
curl -X POST http://100.112.14.98:1234/api/v1/message/text \
  -H 'Content-Type: application/json' \
  -d '{"password":"<pw>","chatGuid":"iMessage;-;+14243305106","message":"bluebubbles test"}'
```

Send a tapback (heart):

```bash
curl -X POST http://100.112.14.98:1234/api/v1/message/react \
  -H 'Content-Type: application/json' \
  -d '{"password":"<pw>","chatGuid":"iMessage;-;+14243305106","selectedMessageGuid":"<guid>","reaction":"love"}'
```

Server health:

```bash
curl http://100.112.14.98:1234/api/v1/server/info?password=<pw>
```

## Inbound Event Sink

`~/.phenotype/imessage-inbound.jsonl` — one JSON object per line:

```json
{"received_at": "2026-04-24T...", "type": "new-message", "data": {...}}
```

Agents tail this file to react to inbound iMessages, tapbacks, and stickers.

## Known TCC Wall

macOS Transparency, Consent, and Control (TCC) prompts for Full Disk /
Contacts / Accessibility / Automation **cannot** be granted programmatically
without disabling SIP. Step 2 is manual. After granting, restart BlueBubbles.

## Ports

| Port | Service | Exposure |
|------|---------|----------|
| 1234 | BlueBubbles REST API | Tailnet only (ACL) |
| 8787 | Webhook receiver | localhost (or tailnet via ACL) |

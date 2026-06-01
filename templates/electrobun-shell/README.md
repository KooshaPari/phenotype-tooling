# phenotype-desktop Electrobun shell template

Wrap any Phenotype web app as a desktop app in one command.
Uses [Electrobun](https://github.com/blackboardsh/electrobun): Bun runtime + system webview
(WebView2 on Windows, WKWebView on macOS, WebKitGTK on Linux). ~14MB distributable.

## One-command adoption

```bash
./adopt.sh \
  --app-name   "MyApp" \
  --app-id     "com.example.myapp" \
  --renderer-url  "http://localhost:3000" \
  --views-entrypoint "../web/dist/index.html" \
  --compose    "/path/to/repo/process-compose.yml" \
  --out        /path/to/output/desktop
```

Then:

```bash
cd /path/to/output/desktop
bun install   # macOS only
bun dev       # opens window → renderer URL; also boots services via process-compose
```

## What you get

| Feature | Detail |
|---|---|
| One-click service boot | On launch runs `process-compose up -d --config $SERVICES_COMPOSE_FILE` |
| Dev mode | Points webview at `RENDERER_URL` (hot-reload from your existing Vite/Next dev server) |
| Production | Bundles `views/app/index.html` from `--views-entrypoint` |
| Window | 1400x900, `hiddenInset` title bar (override via `WINDOW_WIDTH`/`WINDOW_HEIGHT`) |
| Menu | Standard Edit/View + app name menu; wire app-specific actions via `win.webview.executeJavaScript` |
| IPC | Dispatch to renderer via `win.webview.executeJavaScript("window.__app.handler()")` |

## Platform notes

- **Build:** Electrobun CLI (`electrobun build`) requires macOS. Use a macOS CI runner.
- **Run:** Windows 11+ (WebView2), macOS (WKWebView), Linux (WebKitGTK) — all stable.
- **Windows WebView2:** Edge WebView2 Runtime required (ships with Windows 11; auto-installed on Win10+).

## Reference: Tracera migration

`E:/Dev/Tracera/frontend/apps/desktop-electrobun` is the production reference implementation,
migrated from Electron + electron-vite to this template.

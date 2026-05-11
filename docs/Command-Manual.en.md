# YouTubeDownloader Command Manual (Beginner-Friendly)

This document only includes commands you can copy and run right now.
Current release target is Windows.

## 1. First-Time Setup (Run Once)

Run in the project root:

```bash
npm install --no-audit --no-fund
python -m pip install -r backend/requirements.txt
```

## 2. Start for Development (Recommended)

```bash
npm run dev
```

Notes:
- This command starts both the frontend dev server and Electron desktop app.
- This is the least likely way to hit a white screen during development.

## 3. Start Desktop Only (Without Frontend Dev Server)

```bash
npm run build:frontend
npm run dev:electron
```

Notes:
- Step 1 builds the frontend into `frontend/dist`.
- Step 2 starts Electron, and Electron loads the built page automatically.

## 4. Start Backend Only (For API Debugging)

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --app-dir backend
```

Notes:
- Opening `http://127.0.0.1:8000/` in a browser returns a backend running message (not the frontend page).
- Real APIs are under `/api/*`.

## 5. Build Code (Without Packaging Installer)

```bash
npm run build
```

It runs in order:
- `npm run build:frontend`
- `npm run build:electron`

## 6. Package Installer

It is recommended to regenerate icons first (to ensure `.exe` uses the latest icons):

```bash
npm run generate:icons
```

### Package for Current Platform

```bash
npm run dist
```

### Package for Windows (Recommended)

```bash
npm run dist:win
```

### Generate Unpacked Directory Only (Useful for Package Troubleshooting)

```bash
npm run pack
```

## 7. Common Issues

### 7.1 Desktop White Screen

Check in order:
1. Run `npm run build:frontend` first.
2. Then run `npm run dev:electron`.
3. Open Electron DevTools Console and check whether `ERR_FILE_NOT_FOUND` still exists.

### 7.2 Visiting Port 8000 Does Not Show Frontend Page

This is expected:
- `8000` is the backend API service, not the frontend page.
- Root path usually returns a backend running hint message.
- The desktop frontend is loaded by Electron.

### 7.3 Update yt-dlp / ffmpeg

In desktop app Settings, click:
- `Check Update`
- `Download/Update`

The app automatically puts executables under `resources/bin/windows/`.

Additional notes (current behavior):
- On app startup, missing dependencies are auto-detected and installed in background.
- While dependencies are missing/installing, `Add Task` on Download page is disabled with guidance messages.
- You can view dependency installation output in the `Logs` page.

### 7.4 Icon Not Updated (Still Showing Default Electron Icon)

Check in order:
1. Run `npm run generate:icons`.
2. Re-run `npm run dist:win`.
3. Uninstall old package and install the new one (Windows icon cache may keep old icons).

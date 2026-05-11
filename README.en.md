# YouTubeDownloader (yt-dlp GUI Desktop App)

This is a desktop application built with `Electron + Vue3 + FastAPI`.  
Its goal is to make `yt-dlp` command-line capabilities available through a GUI for beginners.
Current plan: Windows support only.

<img width="1184" height="967" alt="image" src="https://github.com/user-attachments/assets/c4cf2991-ed63-4e8d-ab42-0712bb4791fa" />
<img width="1184" height="967" alt="image" src="https://github.com/user-attachments/assets/f05e67b5-b48b-4e41-95d9-56c0ca43c883" />

## What You Get
- Create download tasks visually (URL, format, resolution, cookie)
- Download page supports `Simple / Advanced` mode switch (simple mode is beginner-friendly)
- Download queue with real-time status
- Sidebar speed card (total download speed + realtime line chart)
- Log page (unified terminal command/output view)
- History records (local SQLite)
- About page (project intro, project version, repository, author contact, upstream links)
- Auto download/update for `yt-dlp` (GitHub Release)
- Auto download/update for `ffmpeg` (GitHub Release)
- Windows packaging support (NSIS installer)

## Dependency Auto-Handling and Task Disable Rules
- On app startup, backend automatically checks whether local `yt-dlp` / `ffmpeg` exist.
- If missing, backend automatically installs them in background (you can watch logs in the `Logs` page).
- The `Add Task` button on Download page is automatically disabled when:
  - Dependencies are not installed
  - Dependencies are still being installed
- In dependency-not-ready states, the page shows guidance to open `Settings` and trigger download/update manually.

## Project Structure (Short)
- `desktop/`: Electron main process, handles windows and local system capabilities (file picker, backend startup)
- `frontend/`: Vue UI pages
- `backend/`: FastAPI service, handles task scheduling, download execution, and status management
- `resources/bin/`: Platform binaries (`yt-dlp`, `ffmpeg`)

## Before Development
> Important: run all commands in the **project root**, not in `frontend/`.

1. Install Node dependencies

```bash
npm install --no-audit --no-fund
```

2. Install Python dependencies

```bash
python -m pip install -r backend/requirements.txt
```

## Start (Recommended)
```bash
npm run dev
```

This command starts the frontend dev server and Electron desktop app in parallel, which is recommended for daily development.

## Start Desktop Only (Without Frontend Dev Server)
```bash
npm run build:frontend
npm run dev:electron
```

Notes:
- Electron tries `http://127.0.0.1:5173` first.
- If it is unavailable, Electron falls back to `frontend/dist/index.html` to avoid white screen.

## FAQ
### Why is `http://127.0.0.1:8000/` not the frontend page?
- Because `8000` is the FastAPI backend service.
- The desktop frontend page is loaded by Electron, not from this URL.

### What if I still see a white screen?
Check in order:
1. Make sure commands are run in the project root.
2. Run `npm run build:frontend` first.
3. Then run `npm run dev:electron`.
4. Open Electron DevTools and check for `ERR_FILE_NOT_FOUND`.

## Packaging Commands (Windows)
- Windows installer: `npm run dist:win`
- Current-platform installer (equivalent to Windows on Windows): `npm run dist`
- Generate unpacked directory only (for package troubleshooting): `npm run pack`
- One-click icon generation (`svg -> png/ico`): `npm run generate:icons`

> Current release target is Windows. Use `npm run dist:win` as the primary packaging command.

## Detailed Command Manual
- See `docs/命令手册.md` (Chinese)
- See `docs/Command-Manual.en.md` (English)

## API Documentation
- See `docs/接口文档.md` (Chinese)
- See `docs/API-Documentation.en.md` (English)

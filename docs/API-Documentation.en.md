# YouTubeDownloader Backend API Documentation

## 1. Basic Information
- Protocols: `HTTP` + `WebSocket`
- Default address: `http://127.0.0.1:8000`
- Data format: `application/json`
- Auth: no authentication in current version (called by local desktop app only)

## 2. General Notes
- Time fields use ISO datetime strings, for example: `2026-05-11T10:20:30.123456`
- Common error structure:

```json
{
  "detail": "Error message"
}
```

- Common status codes:
1. `200` request succeeded
2. `400` parameter or business validation failed
3. `404` resource not found
4. `422` request body validation failed (for example, invalid download concurrency range)
5. `500` internal server error
6. `503` app state not initialized

## 3. Data Models

### 3.1 CreateTaskRequest
Used to create a download task (`POST /api/tasks`).

```json
{
  "url": "https://www.youtube.com/watch?v=example",
  "output_dir": "D:/Downloads",
  "download_target": "video",
  "format_id": "bestvideo+bestaudio",
  "resolution": "1080",
  "resolution_mode": "prefer",
  "audio_format": "mp3",
  "subtitle_mode": "none",
  "subtitle_langs": "zh-Hans,en.*",
  "write_info_json": false,
  "write_description": false,
  "write_thumbnail": false,
  "embed_thumbnail": false,
  "cookie_mode": "none",
  "cookie_value": ""
}
```

Field descriptions:
1. `url`: video URL, required
2. `output_dir`: output directory, required
3. `download_target`: target type, `video | audio | thumbnail`
4. `format_id`: format ID, optional (effective for `video` only)
5. `resolution`: resolution, optional (effective for `video` only)
6. `resolution_mode`: resolution policy, `prefer | limit` (effective for `video` only)
7. `audio_format`: audio format, optional (effective for `audio` only)
8. `subtitle_mode`: subtitle mode, `none | manual | auto | all`
9. `subtitle_langs`: subtitle language expression, optional
10. `write_info_json`: whether to output `.info.json`
11. `write_description`: whether to output `.description`
12. `write_thumbnail`: whether to write thumbnail image
13. `embed_thumbnail`: whether to embed thumbnail into media file
14. `cookie_mode`: `none | file | browser`
15. `cookie_value`: cookie source value (file path or browser name), optional

### 3.2 DownloadTask
Full task structure (used by list response, create response, and WebSocket push).

```json
{
  "id": "uuid",
  "url": "https://www.youtube.com/watch?v=example",
  "output_dir": "D:/Downloads",
  "download_target": "video",
  "format_id": "bestvideo+bestaudio",
  "resolution": "1080",
  "resolution_mode": "prefer",
  "audio_format": null,
  "subtitle_mode": "none",
  "subtitle_langs": null,
  "write_info_json": false,
  "write_description": false,
  "write_thumbnail": false,
  "embed_thumbnail": false,
  "cookie_mode": "none",
  "cookie_value": null,
  "status": "pending",
  "progress": 0,
  "speed": null,
  "eta": null,
  "log": "",
  "error": null,
  "result_path": null,
  "created_at": "2026-05-11T10:20:30.123456",
  "updated_at": "2026-05-11T10:20:30.123456"
}
```

`status` allowed values:
1. `pending`
2. `running`
3. `completed`
4. `failed`
5. `canceled`

### 3.3 TaskActionResponse
Used by action endpoints such as cancel/delete/clear.

```json
{
  "ok": true,
  "message": "Task canceled"
}
```

## 4. HTTP Endpoints

### 4.1 Health
#### GET `/`
Description: root hint endpoint to verify backend is running.

Response example:

```json
{
  "message": "yt-dlp desktop backend is running",
  "hint": "Use /api/* endpoints from desktop frontend"
}
```

---

### 4.2 Task Endpoints (`/api/tasks`)

#### GET `/api/tasks`
Description: get current in-memory task list (sorted by created time descending).

Response: `DownloadTask[]`

#### POST `/api/tasks`
Description: create a task and enqueue it.

Request body: `CreateTaskRequest`  
Response: `DownloadTask`

Failure examples (400):

```json
{
  "detail": "Dependencies are still installing"
}
```

```json
{
  "detail": "Dependencies are not installed"
}
```

#### POST `/api/tasks/{task_id}/cancel`
Description: cancel a task (only unfinished tasks are cancelable).

Path params:
1. `task_id`: task ID

Response: `TaskActionResponse`

Failure example (404):

```json
{
  "detail": "Task not found or not cancelable"
}
```

#### POST `/api/tasks/{task_id}/retry`
Description: retry a failed task only (`failed` status only). A new task ID is created and enqueued.

Path params:
1. `task_id`: task ID

Response: `DownloadTask`

Failure example (400):

```json
{
  "detail": "Only failed tasks can be retried"
}
```

#### DELETE `/api/tasks/{task_id}`
Description: delete a queued task (`running` tasks cannot be deleted directly; cancel first).

Path params:
1. `task_id`: task ID

Response: `TaskActionResponse`

Failure example (404):

```json
{
  "detail": "Task not found or running"
}
```

---

### 4.3 History Endpoints (`/api/history`)

#### GET `/api/history?limit=200`
Description: read SQLite history records.

Query params:
1. `limit`: max return count, range `1-1000`, default `200`

Response: history item array (compatible with `DownloadTask` structure)

#### DELETE `/api/history/{task_id}`
Description: delete one history record.

Path params:
1. `task_id`: task ID

Response: `TaskActionResponse`

Failure example (404):

```json
{
  "detail": "History item not found"
}
```

#### DELETE `/api/history`
Description: clear all history records.

Response: `TaskActionResponse`

Response example:

```json
{
  "ok": true,
  "message": "History cleared: 12"
}
```

---

### 4.4 Cookie Endpoints (`/api/cookies`)

#### POST `/api/cookies/import`
Description: validate whether the selected `cookies.txt` path is valid.

Request body:

```json
{
  "path": "D:/path/to/cookies.txt"
}
```

Response example:

```json
{
  "ok": "true",
  "path": "D:/path/to/cookies.txt"
}
```

Failure example (400):

```json
{
  "detail": "Cookie file does not exist or has invalid format"
}
```

---

### 4.5 System Endpoints (`/api/system`)

#### GET `/api/system/settings`
Description: read app settings (currently includes download concurrency only).

Response example:

```json
{
  "download_concurrency": 2,
  "min_download_concurrency": 1,
  "max_download_concurrency": 20,
  "default_download_concurrency": 2
}
```

#### PUT `/api/system/settings`
Description: update app settings and apply immediately to running queue workers.

Request body example:

```json
{
  "download_concurrency": 4
}
```

Response: same as `GET /api/system/settings`

Failure example (422):

```json
{
  "detail": [
    {
      "loc": ["body", "download_concurrency"],
      "msg": "Input should be less than or equal to 20",
      "type": "less_than_equal"
    }
  ]
}
```

#### GET `/api/system/dependencies`
Description: check local dependency file availability (`yt-dlp` / `ffmpeg`).

Response example:

```json
{
  "yt_dlp": {
    "path": "D:/.../yt-dlp.exe",
    "exists": true,
    "installing": false
  },
  "ffmpeg": {
    "path": "D:/.../ffmpeg.exe",
    "exists": true,
    "ffmpeg_exists": true,
    "ffprobe_exists": true,
    "ffprobe_path": "D:/.../ffprobe.exe",
    "installing": false
  }
}
```

Field note:
1. `installing`: whether this dependency is currently being downloaded/installed (`true` during auto-install or manual update)
2. `ffmpeg.exists`: combined availability (`ffmpeg` and `ffprobe` must both exist)
3. `ffmpeg.ffmpeg_exists`: whether `ffmpeg` executable exists
4. `ffmpeg.ffprobe_exists`: whether `ffprobe` executable exists

#### GET `/api/system/yt-dlp/update-status`
Description: check `yt-dlp` update status.

Response example:

```json
{
  "installed_version": "2026.05.01",
  "latest_version": "2026.05.10",
  "has_update": true,
  "binary_path": "D:/.../yt-dlp.exe"
}
```

#### POST `/api/system/yt-dlp/update`
Description: one-click download/update for `yt-dlp`.

Response example:

```json
{
  "installed_version": "2026.05.01",
  "latest_version": "2026.05.10",
  "has_update": true,
  "binary_path": "D:/.../yt-dlp.exe",
  "updated_to": "2026.05.10",
  "asset": "yt-dlp.exe",
  "path": "D:/.../yt-dlp.exe",
  "updated": true
}
```

Failure example (500):

```json
{
  "detail": "yt-dlp update failed: specific error"
}
```

#### GET `/api/system/ffmpeg/update-status`
Description: check `ffmpeg` update status.

Response example:

```json
{
  "installed_version": "ffmpeg version ...",
  "latest_release_id": 123456789,
  "latest_tag_name": "latest",
  "latest_published_at": "2026-05-10T00:00:00Z",
  "local_release_id": 123000000,
  "has_update": true,
  "binary_path": "D:/.../ffmpeg.exe",
  "ffprobe_path": "D:/.../ffprobe.exe",
  "ffprobe_exists": true
}
```

#### POST `/api/system/ffmpeg/update`
Description: one-click download/update for `ffmpeg`.

Response example:

```json
{
  "installed_version": "ffmpeg version ...",
  "latest_release_id": 123456789,
  "latest_tag_name": "latest",
  "latest_published_at": "2026-05-10T00:00:00Z",
  "local_release_id": 123000000,
  "has_update": true,
  "binary_path": "D:/.../ffmpeg.exe",
  "ffprobe_path": "D:/.../ffprobe.exe",
  "ffprobe_exists": true,
  "updated_to_release": "latest",
  "asset": "ffmpeg-master-latest-win64-gpl.zip",
  "path": "D:/.../ffmpeg.exe",
  "updated": true
}
```

Failure example (500):

```json
{
  "detail": "ffmpeg update failed: specific error"
}
```

## 5. WebSocket Endpoint

### 5.1 Task and Terminal Event Stream
#### WS `/ws/tasks`
Description: unified event stream. Frontend receives task state updates and terminal logs via one connection.

Event structure:

```json
{
  "type": "event_type",
  "data": {}
}
```

Event types:
1. `task_update`: task state update, `data` is `DownloadTask`
2. `terminal_output`: terminal output event, `data` structure below

`terminal_output` example:

```json
{
  "type": "terminal_output",
  "data": {
    "task_id": "system-yt-dlp",
    "stream": "stdout",
    "text": "latest yt-dlp release: 2026.05.10, assets=24"
  }
}
```

Common `stream` values:
1. `command`: command or request action
2. `stdout`: standard output content
3. `status`: status hint

## 6. cURL Examples

### 6.1 Create Task
```bash
curl -X POST "http://127.0.0.1:8000/api/tasks" ^
  -H "Content-Type: application/json" ^
  -d "{\"url\":\"https://www.youtube.com/watch?v=example\",\"output_dir\":\"D:/Downloads\",\"cookie_mode\":\"none\"}"
```

### 6.2 Cancel Task
```bash
curl -X POST "http://127.0.0.1:8000/api/tasks/{task_id}/cancel"
```

### 6.3 Delete Queued Task
```bash
curl -X DELETE "http://127.0.0.1:8000/api/tasks/{task_id}"
```

### 6.3.1 Retry Failed Task
```bash
curl -X POST "http://127.0.0.1:8000/api/tasks/{task_id}/retry"
```

### 6.4 Delete One History Item
```bash
curl -X DELETE "http://127.0.0.1:8000/api/history/{task_id}"
```

### 6.5 Clear History
```bash
curl -X DELETE "http://127.0.0.1:8000/api/history"
```

### 6.6 Check and Update yt-dlp
```bash
curl "http://127.0.0.1:8000/api/system/yt-dlp/update-status"
curl -X POST "http://127.0.0.1:8000/api/system/yt-dlp/update"
```

### 6.7 Check and Update ffmpeg
```bash
curl "http://127.0.0.1:8000/api/system/ffmpeg/update-status"
curl -X POST "http://127.0.0.1:8000/api/system/ffmpeg/update"
```

### 6.8 Read and Update App Settings
```bash
curl "http://127.0.0.1:8000/api/system/settings"
curl -X PUT "http://127.0.0.1:8000/api/system/settings" ^
  -H "Content-Type: application/json" ^
  -d "{\"download_concurrency\":4}"
```

### 6.9 Check Dependency Install State
```bash
curl "http://127.0.0.1:8000/api/system/dependencies"
```

## 7. Versioning and Maintenance Tips
1. Update this document whenever routes are added or changed.
2. If frontend shows `Method Not Allowed / Not Found`, first check whether an old backend process is still running.
3. You can use `GET /openapi.json` as runtime truth for API definitions.

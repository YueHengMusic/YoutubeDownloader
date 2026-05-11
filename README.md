# YoutubeDownloader（yt-dlp GUI 桌面版）

这是一个基于 `Electron + Vue3 + FastAPI` 的桌面应用，目标是把 `yt-dlp` 的命令行能力做成图形界面，方便新手使用。

## 你会得到什么
- 图形化创建下载任务（链接、格式、分辨率、Cookie）
- 下载队列与实时状态
- 历史记录（本地 SQLite）
- `yt-dlp` 自动下载/更新（GitHub Release）
- `ffmpeg` 自动下载/更新（GitHub Release）
- 跨平台打包能力（Windows/macOS/Linux）

## 技术结构（简版）
- `desktop/`：Electron 主进程，负责窗口与本地系统能力（文件选择、启动后端）
- `frontend/`：Vue 页面，负责交互界面
- `backend/`：FastAPI 服务，负责任务调度、下载执行、状态管理
- `resources/bin/`：平台二进制目录（`yt-dlp`、`ffmpeg`）

## 开发前准备
> 重要：所有命令都在**项目根目录**执行，不要在 `frontend/` 子目录执行。

1. 安装 Node 依赖

```bash
npm install --no-audit --no-fund
```

2. 安装 Python 依赖

```bash
python -m pip install -r backend/requirements.txt
```

## 启动方式（推荐）
```bash
npm run dev
```

这条命令会并行启动前端开发服务 + Electron 桌面端，适合日常开发。

## 只启动桌面端（不启前端 dev server）
```bash
npm run build:frontend
npm run dev:electron
```

说明：
- Electron 会优先尝试 `http://127.0.0.1:5173`。
- 若不可用，会自动回退加载 `frontend/dist/index.html`，避免白屏。

## 常见疑问
### 为什么访问 `http://127.0.0.1:8000/` 不是前端页面？
- 因为 `8000` 是 FastAPI 后端接口服务。
- 桌面前端页面是 Electron 加载的，不走这个 URL。

### 还是白屏怎么办？
按顺序做：
1. 确认命令在项目根目录执行
2. 先运行 `npm run build:frontend`
3. 再运行 `npm run dev:electron`
4. 打开 Electron 控制台看是否有 `ERR_FILE_NOT_FOUND`

## 打包命令
- 当前平台安装包：`npm run dist`
- 指定平台：
  - `npm run dist:win`
  - `npm run dist:mac`
  - `npm run dist:linux`
- 仅生成目录（调试打包用）：`npm run pack`

> `electron-builder` 已配置把 `resources/bin/{windows,macos,linux}` 自动映射到安装包内。

## 详细命令手册
- 见 `docs/命令手册.md`（含更多启动、构建、打包、排错命令）。

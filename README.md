# YouTubeDownloader（yt-dlp GUI 桌面版）

这是一个基于 `Electron + Vue3 + FastAPI` 的桌面应用，目标是把 `yt-dlp` 的命令行能力做成图形界面，方便新手使用。
当前版本仅计划适配 Windows 平台。

## 你会得到什么
- 图形化创建下载任务（链接、格式、分辨率、Cookie）
- 下载页支持“简单/高级”模式切换（简单模式更适合新手）
- 下载队列与实时状态
- 日志页面（统一查看终端命令与输出）
- 历史记录（本地 SQLite）
- 关于页面（项目说明、项目版本、项目仓库、作者联系方式、上游仓库链接）
- `yt-dlp` 自动下载/更新（GitHub Release）
- `ffmpeg` 自动下载/更新（GitHub Release）
- Windows 桌面打包能力（NSIS 安装包）

## 依赖自动处理与任务禁用说明
- 应用启动时会自动检测本地 `yt-dlp` / `ffmpeg` 是否存在。
- 若缺失，后端会自动后台下载安装（可在“日志”页查看输出）。
- 下载页“添加任务”按钮在以下场景会自动禁用并显示引导提示：
  - 依赖未安装
  - 依赖正在下载安装（未安装完成）
- 当依赖未就绪时，可跳转“设置”页手动点击下载/更新。

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

## 打包命令（Windows）
- Windows 安装包：`npm run dist:win`
- 当前平台安装包（在 Windows 上等同打 Windows 包）：`npm run dist`
- 仅生成目录（调试打包用）：`npm run pack`
- 图标一键生成（`svg -> png/ico`）：`npm run generate:icons`

> 当前发布目标为 Windows，建议优先使用 `npm run dist:win`。

## 详细命令手册
- 见 `docs/命令手册.md`（含更多启动、构建、打包、排错命令）。

## 接口文档
- 中文：`docs/接口文档.md`
- 英文：`docs/API-Documentation.en.md`

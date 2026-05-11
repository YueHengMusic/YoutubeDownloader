import { app, BrowserWindow, Menu, dialog, ipcMain, nativeImage, shell } from "electron";
import path from "node:path";
import { spawn, ChildProcess } from "node:child_process";
import fs from "node:fs";

let backendProcess: ChildProcess | null = null;
const DEV_FRONTEND_URL = "http://127.0.0.1:5173";
const BACKEND_HOST = "127.0.0.1";
const BACKEND_PORT = "8000";

/**
 * 获取桌面端窗口图标路径：
 * - Windows 优先使用 .ico（任务栏/窗口标题图标更稳定）；
 * - macOS/Linux 使用 .png；
 * - 开发与打包路径保持同构，便于排查资源问题。
 */
function getWindowIconPath(): string {
  const iconFileName = process.platform === "win32" ? "app_icon.ico" : "app_icon.png";
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "icons", iconFileName);
  }
  return path.resolve(__dirname, "../../resources/icons", iconFileName);
}

/**
 * 读取窗口图标：
 * - 优先使用平台推荐格式（win: ico / other: png）；
 * - 读取失败时返回 undefined，Electron 会回退默认行为，不阻断启动。
 */
function loadWindowIcon() {
  const iconPath = getWindowIconPath();
  const iconImage = nativeImage.createFromPath(iconPath);
  if (!iconImage.isEmpty()) return iconImage;
  return undefined;
}

/**
 * 获取后端目录。
 * - 开发环境：项目根目录/backend
 * - 打包环境：<resources>/backend
 */
function getBackendRootDir(): string {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "backend");
  }
  return path.resolve(__dirname, "../..", "backend");
}

/**
 * 获取前端构建产物 index.html 路径。
 * - 开发环境：项目根目录/frontend/dist/index.html
 * - 打包环境：<resources>/frontend-dist/index.html
 */
function getFrontendDistHtml(): string {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "frontend-dist", "index.html");
  }
  return path.resolve(__dirname, "../../frontend/dist/index.html");
}

/**
 * 检查 Vite 开发服务器是否可访问。
 * 这里加了短超时（1.2 秒），避免卡住窗口打开流程。
 */
async function isDevServerAvailable(url: string): Promise<boolean> {
  const abort = new AbortController();
  const timer = setTimeout(() => abort.abort(), 1200);
  try {
    const response = await fetch(url, { method: "GET", signal: abort.signal });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * 创建主窗口并加载前端页面。
 *
 * 加载策略（按优先级）：
 * 1) 如果 5173 可用，加载开发服务器（支持热更新）；
 * 2) 否则加载本地构建后的 index.html（避免白屏）；
 * 3) 如果构建产物也不存在，展示可操作的错误提示页。
 */
async function createWindow(): Promise<void> {
  const windowIcon = loadWindowIcon();
  const win = new BrowserWindow({
    // 按用户要求：默认以最小尺寸启动，避免初始窗口过大。
    width: 960,
    height: 780,
    // 最小高度需要覆盖下载页完整表单，避免底部操作区被裁切。
    minWidth: 960,
    minHeight: 780,
    icon: windowIcon,
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: false,
      contextIsolation: true
    }
  });
  // 明确移除窗口菜单栏，避免显示默认 File/Edit/View 等菜单。
  win.setMenuBarVisibility(false);
  win.removeMenu();

  const hasDevServer = await isDevServerAvailable(DEV_FRONTEND_URL);
  if (hasDevServer) {
    await win.loadURL(DEV_FRONTEND_URL);
    return;
  }

  const builtHtml = getFrontendDistHtml();
  if (fs.existsSync(builtHtml)) {
    await win.loadFile(builtHtml);
    return;
  }

  // 最终兜底：就算前端资源缺失，也给用户清晰操作指引，而不是纯白屏。
  const diagnosticHtml = `
    <html>
      <body style="font-family: Arial; padding: 20px;">
        <h2>Frontend Not Found</h2>
        <p>Vite dev server is unavailable and built frontend files are missing.</p>
        <p>Run: <code>npm run build:frontend</code> then restart Electron.</p>
      </body>
    </html>
  `;
  await win.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(diagnosticHtml)}`);
}

/**
 * 启动 FastAPI 后端子进程。
 * 后端只监听本机地址，避免被局域网其他设备直接访问。
 */
function startBackend(): void {
  const backendRoot = getBackendRootDir();
  backendProcess = spawn(
    "python",
    ["-m", "uvicorn", "app.main:app", "--host", BACKEND_HOST, "--port", BACKEND_PORT, "--app-dir", backendRoot],
    {
      cwd: backendRoot,
      stdio: "inherit"
    }
  );
}

app.whenReady().then(() => {
  // Windows 任务栏分组与图标关联标识，确保打包后图标展示稳定。
  app.setAppUserModelId("com.yueh.ytdlpgui");
  // 全局移除应用菜单（Windows/Linux 顶部菜单栏；macOS 全局菜单）。
  Menu.setApplicationMenu(null);
  startBackend();
  void createWindow();
});

app.on("window-all-closed", () => {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill();
  }
  if (process.platform !== "darwin") {
    app.quit();
  }
});

// IPC：打开目录选择器（下载输出目录）。
ipcMain.handle("dialog:pick-directory", async () => {
  const result = await dialog.showOpenDialog({
    properties: ["openDirectory"]
  });
  return result.canceled ? null : result.filePaths[0];
});

// IPC：打开文件选择器（仅用于 cookies.txt 导入）。
ipcMain.handle("dialog:pick-cookie", async () => {
  const result = await dialog.showOpenDialog({
    properties: ["openFile"],
    filters: [{ name: "Text", extensions: ["txt"] }]
  });
  return result.canceled ? null : result.filePaths[0];
});

// IPC：使用系统默认浏览器打开外部链接（而不是在 Electron 内部窗口打开）。
ipcMain.handle("shell:open-external-url", async (_event, rawUrl: string) => {
  // 最基础安全校验：仅允许 http/https，避免误传其他协议。
  if (typeof rawUrl !== "string") return false;
  const safeUrl = rawUrl.trim();
  if (!safeUrl.startsWith("http://") && !safeUrl.startsWith("https://")) {
    return false;
  }
  await shell.openExternal(safeUrl);
  return true;
});

// IPC：在系统文件管理器中打开文件并选中（若是目录则直接打开目录）。
ipcMain.handle("shell:reveal-path", async (_event, rawPath: string) => {
  if (typeof rawPath !== "string") return false;
  const safePath = rawPath.trim().replace(/^"(.*)"$/, "$1");
  if (!safePath) return false;
  const normalizedPath = path.normalize(safePath);
  if (!fs.existsSync(normalizedPath)) {
    // 文件不存在时兜底打开父目录，避免前端只能拿到“未知失败”。
    const parentDir = path.dirname(normalizedPath);
    if (!fs.existsSync(parentDir)) return false;
    await shell.openPath(parentDir);
    return true;
  }
  const stat = fs.statSync(normalizedPath);
  if (stat.isDirectory()) {
    await shell.openPath(normalizedPath);
    return true;
  }
  shell.showItemInFolder(normalizedPath);
  return true;
});

// IPC：读取应用版本号（优先来自 Electron 打包版本信息）。
ipcMain.handle("app:get-version", async () => {
  return app.getVersion();
});

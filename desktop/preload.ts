import { contextBridge, ipcRenderer } from "electron";

// 通过 preload 暴露“最小必要能力”给前端页面。
// 这样前端拿不到完整 Node.js 权限，安全性更高。
contextBridge.exposeInMainWorld("desktopAPI", {
  // 让用户选择下载目录。
  pickDirectory: async (): Promise<string | null> => {
    return ipcRenderer.invoke("dialog:pick-directory");
  },
  // 让用户选择 cookies.txt 文件。
  pickCookieFile: async (): Promise<string | null> => {
    return ipcRenderer.invoke("dialog:pick-cookie");
  },
  // 使用系统默认浏览器打开外部链接（例如插件商店地址）。
  openExternalUrl: async (url: string): Promise<boolean> => {
    return ipcRenderer.invoke("shell:open-external-url", url);
  },
  // 在系统文件管理器中定位到目标文件（或打开目标目录）。
  revealPath: async (targetPath: string): Promise<boolean> => {
    return ipcRenderer.invoke("shell:reveal-path", targetPath);
  },
  // 获取桌面应用版本号（来自主进程 app.getVersion）。
  getAppVersion: async (): Promise<string> => {
    return ipcRenderer.invoke("app:get-version");
  }
});

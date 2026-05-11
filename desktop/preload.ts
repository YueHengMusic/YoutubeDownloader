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
  }
});

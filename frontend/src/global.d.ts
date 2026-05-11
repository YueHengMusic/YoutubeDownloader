export {};

// 给浏览器全局对象 Window 扩展 desktopAPI 类型定义。
// 这样在 Vue/TS 代码里调用 window.desktopAPI 时有类型提示，不会报红。
declare global {
  interface Window {
    // desktopAPI 来自 Electron preload.ts 的安全桥接能力。
    desktopAPI?: {
      // 选择目录：用于设置下载输出位置。
      pickDirectory?: () => Promise<string | null>;
      // 选择 cookies.txt：用于登录态下载。
      pickCookieFile?: () => Promise<string | null>;
    };
  }
}

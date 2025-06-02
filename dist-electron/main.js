import { app as n, BrowserWindow as i, Menu as p } from "electron";
import { fileURLToPath as a } from "node:url";
import o from "node:path";
const s = o.dirname(a(import.meta.url));
process.env.APP_ROOT = o.join(s, "..");
const t = process.env.VITE_DEV_SERVER_URL, f = o.join(process.env.APP_ROOT, "dist-electron"), r = o.join(process.env.APP_ROOT, "dist");
process.env.VITE_PUBLIC = t ? o.join(process.env.APP_ROOT, "public") : r;
let e;
function l() {
  e = new i({
    width: 1280,
    height: 720,
    minWidth: 1e3,
    minHeight: 600,
    icon: o.join(process.env.VITE_PUBLIC, "logo.ico"),
    webPreferences: {
      preload: o.join(s, "preload.mjs")
    }
  }), p.setApplicationMenu(null), e.webContents.on("before-input-event", (d, c) => {
    c.key === "F12" && (e == null || e.webContents.toggleDevTools());
  }), e.webContents.on("did-finish-load", () => {
    e == null || e.webContents.send("main-process-message", (/* @__PURE__ */ new Date()).toLocaleString());
  }), t ? e.loadURL(t) : e.loadFile(o.join(r, "index.html"));
}
n.on("window-all-closed", () => {
  process.platform !== "darwin" && (n.quit(), e = null);
});
n.on("activate", () => {
  i.getAllWindows().length === 0 && l();
});
n.whenReady().then(l);
export {
  f as MAIN_DIST,
  r as RENDERER_DIST,
  t as VITE_DEV_SERVER_URL
};

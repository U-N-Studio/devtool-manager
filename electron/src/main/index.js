const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const envHandler = require("./env");
const packagesHandler = require("./packages");
const toolsHandler = require("./tools");

let win;

function createWindow() {
  win = new BrowserWindow({
    width: 1100,
    height: 720,
    minWidth: 800,
    minHeight: 500,
    title: "DevTool Manager",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadFile(path.join(__dirname, "..", "renderer", "index.html"));
}

app.whenReady().then(() => {
  envHandler.register(ipcMain);
  packagesHandler.register(ipcMain);
  toolsHandler.register(ipcMain);
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  app.quit();
});

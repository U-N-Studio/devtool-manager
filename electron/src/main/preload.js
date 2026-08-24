const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  env: {
    getCategorized: () => ipcRenderer.invoke("env:getCategorized"),
    set: (name, value, source) => ipcRenderer.invoke("env:set", name, value, source),
    delete: (name, source) => ipcRenderer.invoke("env:delete", name, source),
    addPath: (entry, source) => ipcRenderer.invoke("env:addPath", entry, source),
    deletePath: (entry, source) => ipcRenderer.invoke("env:deletePath", entry, source),
  },
  packages: {
    getList: (funcTag, langTag, installTag) =>
      ipcRenderer.invoke("packages:getList", funcTag, langTag, installTag),
    install: (name) => ipcRenderer.invoke("packages:install", name),
    uninstall: (name) => ipcRenderer.invoke("packages:uninstall", name),
    getFuncTags: () => ipcRenderer.invoke("packages:getFuncTags"),
    getLangTags: () => ipcRenderer.invoke("packages:getLangTags"),
  },
  tools: {
    getInfo: (category) => ipcRenderer.invoke("tools:getInfo", category),
  },
});

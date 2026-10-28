// Bridge between the director (page) and capture-main.cjs. contextIsolation is off, so this is the page's window.
const { ipcRenderer } = require('electron');

window.__cap = {
    args: ipcRenderer.sendSync('args'),
    log: (...a) => ipcRenderer.send('log', a.map(x => (typeof x === 'string' ? x : JSON.stringify(x))).join(' ')),
    begin: (id) => ipcRenderer.invoke('begin', id),
    frame: (pixels) => ipcRenderer.invoke('frame', pixels),
    end: () => ipcRenderer.invoke('end'),
    still: (name, pixels, screenshot = false) => ipcRenderer.invoke('still', name, pixels, screenshot),
    json: (name, data) => ipcRenderer.invoke('json', name, data),
    finish: (code) => ipcRenderer.invoke('finish', code),
};

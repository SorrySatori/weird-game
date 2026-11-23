const { app, BrowserWindow, Menu, ipcMain, dialog, shell } = require('electron');
const fs = require('fs');
const path = require('path');

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

let mainWindow;

// A packaged build (what Steam ships) has no reload and no DevTools: Ctrl+R would throw the player back to the
// title without saving, and the hidden menu bar must not pop up over the game on Alt. `--devtools` (a Steam launch
// option) turns DevTools back on for debugging an installed copy.
const DEV_MENU = !app.isPackaged || process.argv.includes('--devtools');

const createWindow = () => {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    // width: 800,
    // height: 600,
    backgroundColor: '#2d2d2d',
    fullscreen: true,       // launch in true fullscreen — no title bar, covers the taskbar
    autoHideMenuBar: true,  // dev: hide the File/View menu bar (its F11 / Ctrl+Q accelerators still work)
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      devTools: DEV_MENU
    }
  });

  if (DEV_MENU) {
    const template = [
      {
        label: 'File',
        submenu: [{ role: 'quit' }]
      },
      {
        label: 'View',
        submenu: [
          { role: 'reload' },
          { role: 'forceReload' },
          { role: 'toggleDevTools' },
          { type: 'separator' },
          { role: 'togglefullscreen' }
        ]
      }
    ];
    Menu.setApplicationMenu(Menu.buildFromTemplate(template));
  } else {
    // no menu at all; F11 keeps toggling fullscreen (the Settings panel re-reads the real state)
    Menu.setApplicationMenu(null);
    mainWindow.webContents.on('before-input-event', (event, input) => {
      if (input.type === 'keyDown' && input.key === 'F11' && !input.isAutoRepeat) {
        event.preventDefault();
        setFullscreen(!mainWindow.isFullScreen());
      }
    });
  }

  // Load the index.html file
  mainWindow.loadFile('index.html');

  // Handle window close event
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
};

// "Exit Game" from the in-game main menu (see preload.js → window.appControl.quit).
ipcMain.on('app:quit', () => app.quit());

// The Settings panel's fullscreen toggle. Leaving fullscreen gives a 16:9 window (the game is 1067×600, FIT-scaled).
// F11 in a packaged build goes through here too.
function setFullscreen(on) {
  if (!mainWindow || mainWindow.isFullScreen() === on) return;
  if (!on) {
    mainWindow.once('leave-full-screen', () => {
      mainWindow.setSize(1280, 720);
      mainWindow.center();
    });
  }
  mainWindow.setFullScreen(on);
}
ipcMain.on('app:setFullscreen', (_e, on) => setFullscreen(!!on));
ipcMain.handle('app:isFullscreen', () => !!mainWindow && mainWindow.isFullScreen());

// The end-of-demo card's "Wishlist on Steam": the full game's store page, in the Steam client if it's there, else the
// browser. The renderer only asks; the URL never comes from it.
const STORE_APP_ID = 4118600;
ipcMain.on('app:openStore', () => {
  const web = `https://store.steampowered.com/app/${STORE_APP_ID}/`;
  shell.openExternal(`steam://store/${STORE_APP_ID}`).catch(() => shell.openExternal(web).catch(() => {}));
});

// Save files: one JSON per slot (save1.json, quicksave.json, autosave.json) in a plain folder, so Steam Auto-Cloud can
// sync it. Steamworks → the demo app → Steam Cloud → Root Paths: root WinAppDataRoaming, subdirectory
// "weird-game/saves-demo", pattern "*.json" (Proton and the Steam Deck map %APPDATA% into their prefix).
// The demo keeps its own folder, so it never overwrites the full game's saves (that one uses "saves").
// The renderer's localStorage saves (before 2026-11) are moved here by game-api.js on the first start.
const SAVE_DIR_NAME = 'saves-demo';
const SAVE_SLOT = /^[A-Za-z0-9_-]{1,64}$/;      // the slot comes from the renderer: no path separators, no dots
const SAVE_MAX_BYTES = 5 * 1024 * 1024;
const saveDir = () => path.join(app.getPath('appData'), 'weird-game', SAVE_DIR_NAME);
const slotFile = (slot) => {
  if (typeof slot !== 'string' || !SAVE_SLOT.test(slot)) throw new Error(`invalid save slot: ${slot}`);
  return path.join(saveDir(), `${slot}.json`);
};

// The renderer's save API is synchronous (gameAPI.*), so these answer ipcRenderer.sendSync. Every path sets
// returnValue: a handler that didn't would leave the game frozen waiting for the answer.
const answerSync = (handler) => (event, ...args) => {
  try {
    event.returnValue = handler(...args);
  } catch (error) {
    console.error('save files:', error);
    event.returnValue = { success: false, error: error.message };
  }
};

ipcMain.on('saves:write', answerSync((slot, json) => {
  const file = slotFile(slot);
  if (typeof json !== 'string' || json.length > SAVE_MAX_BYTES) throw new Error('invalid save data');
  JSON.parse(json);                                  // never write a file the game couldn't load back
  fs.mkdirSync(saveDir(), { recursive: true });
  // write + fsync a temp file, then swap it in: a crash or power cut mid-save leaves the old save whole.
  // ".json.tmp" doesn't match the cloud's "*.json".
  const tmp = `${file}.tmp`;
  const fd = fs.openSync(tmp, 'w');
  try {
    fs.writeFileSync(fd, json, 'utf8');
    fs.fsyncSync(fd);
  } finally {
    fs.closeSync(fd);
  }
  try {
    fs.renameSync(tmp, file);
  } catch (error) {
    // Windows: an antivirus or the Steam client scanning the old file can refuse the swap; write it in place
    fs.writeFileSync(file, json, 'utf8');
    fs.rmSync(tmp, { force: true });
  }
  return { success: true, path: file };
}));

ipcMain.on('saves:read', answerSync((slot) => {
  const file = slotFile(slot);
  if (!fs.existsSync(file)) return { success: false, error: 'Save file not found' };
  return { success: true, text: fs.readFileSync(file, 'utf8') };
}));

// name + date for the Save / Load panels; the date is the one inside the save (the file's own time can be the
// moment Steam Cloud downloaded it)
ipcMain.on('saves:list', answerSync(() => {
  if (!fs.existsSync(saveDir())) return { success: true, files: [] };
  const files = fs.readdirSync(saveDir())
    .filter(name => name.endsWith('.json') && SAVE_SLOT.test(name.slice(0, -5)))
    .map(name => {
      const file = path.join(saveDir(), name);
      const stat = fs.statSync(file);
      const entry = { name: name.slice(0, -5), date: stat.mtime.toISOString(), size: stat.size };
      try {
        const data = JSON.parse(fs.readFileSync(file, 'utf8'));
        if (data.timestamp) entry.date = data.timestamp;
        entry.scene = data.currentScene || null;
      } catch (_) {
        entry.error = true;                          // broken file: the panels show ⚠ and loading it fails cleanly
      }
      return entry;
    });
  return { success: true, files };
}));

ipcMain.on('saves:delete', answerSync((slot) => {
  const file = slotFile(slot);
  if (!fs.existsSync(file)) return { success: false, error: 'Save file not found' };
  fs.rmSync(file);
  return { success: true };
}));

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
app.whenReady().then(createWindow);

// Quit when all windows are closed, except on macOS.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});


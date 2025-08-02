// Security: API key handling
const getApiKey = () => window.GEMINI_API_KEY || "";

// Error handling wrapper
async function safeDBOperation(operation) {
  try {
    return await operation();
  } catch (error) {
    console.error("Database error:", error);
    showIsland(`Error: ${error.message || "Operation failed"}`);
    throw error;
  }
}

// Debounce for performance
function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// Ripple effect for UI feedback
function createRipple(event) {
  const button = event.currentTarget;
  const circle = document.createElement("span");
  const diameter = Math.max(button.clientWidth, button.clientHeight);
  const radius = diameter / 2;
  
  circle.style.width = circle.style.height = `${diameter}px`;
  circle.style.left = `${event.clientX - button.getBoundingClientRect().left - radius}px`;
  circle.style.top = `${event.clientY - button.getBoundingClientRect().top - radius}px`;
  circle.classList.add("ripple");
  
  const ripple = button.querySelector(".ripple");
  if (ripple) ripple.remove();
  
  button.appendChild(circle);
}

// Session persistence
function saveSessionState() {
  const state = {
    openWindows: Array.from(activeWindows.keys()),
    darkMode: isDarkMode,
    wallpaperIndex: currentWallpaperIndex
  };
  localStorage.setItem('osSession', JSON.stringify(state));
}

function restoreSessionState() {
  const state = JSON.parse(localStorage.getItem('osSession') || '{}');
  if (state.openWindows) {
    state.openWindows.forEach(appName => launchApp(appName));
  }
  if (state.darkMode !== undefined) toggleDarkMode(state.darkMode);
  if (state.wallpaperIndex !== undefined) {
    currentWallpaperIndex = state.wallpaperIndex;
    setWallpaper(wallpapers[currentWallpaperIndex]);
  }
}

// Core OS functionality
(function() {
  const desktop = document.getElementById('desktop');
  const island = document.getElementById('island');
  const dock = document.getElementById('dock');
  const appWindowTemplate = document.getElementById('appWindowTemplate');
  const contextMenu = document.getElementById('contextMenu');
  const fileInput = document.getElementById('fileInput');
  const folderInput = document.getElementById('folderInput');

  let currentZIndex = 100;
  let isDarkMode = true;
  let activeWindows = new Map();

  // Updated wallpaper paths
  const wallpapers = [
    'wallpapers/wallpaper1.jpg',
    'wallpapers/wallpaper2.jpg',
    'wallpapers/wallpaper3.jpg',
    'wallpapers/wallpaper4.jpg'
  ];
  let currentWallpaperIndex = 0;

  // Updated app icons with local paths and added JS-OS apps
  const apps = [
    { name: 'Terminal', icon: 'icons/terminal.svg' },
    { name: 'Finder', icon: 'icons/finder.svg' },
    { name: 'Notes', icon: 'icons/notes.svg' },
    { name: 'Calculator', icon: 'icons/calculator.svg' },
    { name: 'Mail', icon: 'icons/mail.svg' },
    { name: 'Settings', icon: 'icons/settings.svg' },
    { name: 'Admin Dashboard', icon: 'icons/admin.svg' },
    { name: 'About', icon: 'icons/about.svg' },
    // Added JS-OS apps
    { name: 'Text Editor', icon: 'icons/text-editor.svg' },
    { name: 'Paint', icon: 'icons/paint.svg' },
    { name: 'Browser', icon: 'icons/browser.svg' },
    { name: 'Start Menu', icon: 'icons/start-menu.svg' }
  ];

  function vibrateDevice(pattern = [50]) {
    if ("vibrate" in navigator) {
      navigator.vibrate(pattern);
    }
  }

  function showIsland(message) {
    island.textContent = message;
    island.style.opacity = '1';
    island.style.transform = 'translateX(-50%) scale(1.05)';
    vibrateDevice([10]);
    setTimeout(() => {
      island.style.opacity = '0';
      island.style.transform = 'translateX(-50%) scale(1)';
    }, 2000);
  }

  function createDockIcons() {
    apps.forEach(app => {
      const icon = document.createElement('div');
      icon.className = 'dock-icon';
      icon.setAttribute('title', app.name);
      icon.setAttribute('aria-label', `Launch ${app.name}`);
      icon.setAttribute('role', 'button');
      icon.setAttribute('tabindex', '0');
      
      icon.addEventListener('click', () => {
        launchApp(app.name);
        vibrateDevice([10]);
      });
      
      icon.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          launchApp(app.name);
        }
      });

      const img = document.createElement('img');
      img.src = app.icon;
      img.alt = app.name;

      icon.appendChild(img);
      dock.appendChild(icon);
    });
  }

  // Gemini API Call
  const geminiApiUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent";

  async function getAIResponse(prompt) {
      const apiKey = getApiKey();
      if (!apiKey) return "API key not configured";
      
      const payload = {
          contents: [{ role: "user", parts: [{ text: prompt }] }]
      };

      const options = {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
      };

      let retries = 0;
      const maxRetries = 5;
      let delay = 1000;

      while (retries < maxRetries) {
          try {
              const response = await fetch(`${geminiApiUrl}?key=${apiKey}`, options);
              if (!response.ok) {
                  throw new Error(`HTTP error! Status: ${response.status}`);
              }
              const result = await response.json();

              if (result.candidates && result.candidates.length > 0 &&
                  result.candidates[0].content && result.candidates[0].content.parts &&
                  result.candidates[0].content.parts.length > 0) {
                  return result.candidates[0].content.parts[0].text;
              } else {
                  return 'I am sorry, I could not generate a response.';
              }
          } catch (error) {
              console.error('API call failed:', error);
              retries++;
              if (retries < maxRetries) {
                  await new Promise(resolve => setTimeout(resolve, delay));
                  delay *= 2;
              }
          }
      }
      return 'I am unable to connect to the AI service right now. Please try again later.';
  }

  // IndexedDB File System
  const dbName = 'DarkCloudOSDB';
  const fileStoreName = 'files';
  let db;

  async function openDB() {
      return new Promise((resolve, reject) => {
          const request = indexedDB.open(dbName, 1);

          request.onupgradeneeded = (event) => {
              const database = event.target.result;
              if (!database.objectStoreNames.contains(fileStoreName)) {
                  const objectStore = database.createObjectStore(fileStoreName, { keyPath: 'path' });
                  objectStore.createIndex('path', 'path', { unique: true });
              }
          };

          request.onsuccess = (event) => {
              db = event.target.result;
              console.log('IndexedDB opened successfully');
              resolve(db);
          };

          request.onerror = (event) => {
              console.error('IndexedDB error:', event.target.error);
              reject(event.target.error);
          };
      });
  }

  async function saveFileToDB(file, path) {
    return safeDBOperation(async () => {
      if (!db) await openDB();
      return new Promise((resolve, reject) => {
          const transaction = db.transaction([fileStoreName], 'readwrite');
          const store = transaction.objectStore(fileStoreName);
          const fileRecord = {
              path: path,
              name: file.name,
              type: file.type,
              lastModified: file.lastModified,
              size: file.size,
              fileData: file
          };
          const request = store.put(fileRecord);
          request.onsuccess = () => resolve();
          request.onerror = (e) => reject(e.target.error);
      });
    });
  }

  async function getFileFromDB(path) {
    return safeDBOperation(async () => {
      if (!db) await openDB();
      return new Promise((resolve, reject) => {
          const transaction = db.transaction([fileStoreName], 'readonly');
          const store = transaction.objectStore(fileStoreName);
          const request = store.get(path);
          request.onsuccess = (e) => resolve(e.target.result);
          request.onerror = (e) => reject(e.target.error);
      });
    });
  }

  async function deleteFileFromDB(path) {
    return safeDBOperation(async () => {
      if (!db) await openDB();
      return new Promise((resolve, reject) => {
          const transaction = db.transaction([fileStoreName], 'readwrite');
          const store = transaction.objectStore(fileStoreName);
          const request = store.delete(path);
          request.onsuccess = () => resolve();
          request.onerror = (e) => reject(e.target.error);
      });
    });
  }

  async function getAllFilesFromDB() {
    return safeDBOperation(async () => {
      if (!db) await openDB();
      return new Promise((resolve, reject) => {
          const transaction = db.transaction([fileStoreName], 'readonly');
          const store = transaction.objectStore(fileStoreName);
          const request = store.getAll();
          request.onsuccess = (e) => resolve(e.target.result);
          request.onerror = (e) => reject(e.target.error);
      });
    });
  }

  // App Content Generation
  function getAppContent(appName) {
      let content = '';
      switch (appName) {
          case 'Terminal':
              content = `
                  <div class="terminal-content" id="terminalOutput">
                      <p>> Welcome to DarkCloud Terminal v5.0</p>
                      <p>> Type 'help' for commands.</p>
                      <div class="terminal-input-line">
                          <span>></span>
                          <input type="text" class="terminal-input" id="terminalInput" autofocus />
                      </div>
                  </div>
              `;
              break;
          case 'Finder':
              content = `
                  <div class="finder-container">
                      <div class="finder-content-main">
                          <div class="finder-toolbar">
                            <div class="left-controls">
                              <button id="uploadFileBtn">Upload File</button>
                              <button id="uploadFolderBtn">Upload Folder</button>
                              <button id="finderAiBtn">AI</button>
                            </div>
                            <div class="search-container">
                               <input type="search" id="finderSearch" placeholder="Search..." />
                            </div>
                          </div>
                          <div class="app-content-inner">
                            <div class="finder-header">
                                <div class="breadcrumb" id="finderBreadcrumb">
                                    <span>Home</span>
                                </div>
                            </div>
                            <div class="finder-content">
                                <ul class="finder-list" id="finderList"></ul>
                            </div>
                          </div>
                          <div class="finder-context-menu" id="finderContextMenu">
                            <div class="context-menu-item" data-action="new-folder">New Folder</div>
                            <div class="context-menu-item" data-action="new-file">New File</div>
                            <div class="context-menu-item" data-action="rename">Rename</div>
                            <div class="context-menu-item" data-action="delete">Delete</div>
                            <div class="context-menu-item" data-action="download" id="downloadContextBtn" style="display:none;">Download</div>
                          </div>
                      </div>
                      <div class="ai-assistant-panel" id="finderAiPanel">
                          <div class="ai-header">
                            <h3 style="margin:0;">AI Assistant</h3>
                            <button class="ai-close-btn" data-panel-id="finderAiPanel">&times;</button>
                          </div>
                          <div class="ai-chat-history" id="finderAiChatHistory"></div>
                          <form class="ai-input-form">
                              <input type="text" class="ai-input" id="finderAiInput" placeholder="Ask about your files..." />
                              <button type="submit" class="ai-send-btn">
                                <img src="icons/send.svg" />
                              </button>
                          </form>
                      </div>
                  </div>
              `;
              break;
          case 'Notes':
              content = `
                  <div class="notes-container">
                      <div class="notes-content-main">
                          <div class="notes-toolbar">
                              <button data-command="bold"><b>B</b></button>
                              <button data-command="italic"><i>I</i></button>
                              <button data-command="insertUnorderedList">List</button>
                              <button id="notesSaveBtn">Save</button>
                              <button id="notesAiBtn">AI</button>
                          </div>
                          <div class="notes-editor" id="notesEditor" contenteditable="true" spellcheck="false"></div>
                      </div>
                      <div class="ai-assistant-panel" id="notesAiPanel">
                          <div class="ai-header">
                            <h3 style="margin:0;">AI Assistant</h3>
                            <button class="ai-close-btn" data-panel-id="notesAiPanel">&times;</button>
                          </div>
                          <div class="ai-chat-history" id="notesAiChatHistory"></div>
                          <form class="ai-input-form">
                              <input type="text" class="ai-input" id="notesAiInput" placeholder="Ask about your note..." />
                              <button type="submit" class="ai-send-btn">
                                <img src="icons/send.svg" />
                              </button>
                          </form>
                      </div>
                  </div>
              `;
              break;
          case 'Mail':
              content = `
                  <div style="padding: 1rem;">
                      <h2>Inbox</h2>
                      <p><strong>Admin Notification</strong> - System Update Available</p>
                      <p><strong>Support Team</strong> - Your ticket #12345 has been resolved</p>
                      <p><strong>Marketing</strong> - BlackCloud OS New Features!</p>
                  </div>
              `;
              break;
          case 'Settings':
              content = `
                  <div class="settings-content">
                      <h2>System Settings</h2>
                      <div class="settings-item">
                          <span>Display Mode</span>
                          <label class="settings-toggle">
                              <input type="checkbox" id="darkModeToggle" ${isDarkMode ? 'checked' : ''}>
                          </label>
                      </div>
                      <div class="settings-item">
                          <span>Audio Output</span>
                          <select style="padding: 5px; border-radius: 5px; border: 1px solid var(--border-color); background: var(--highlight); color: var(--text-color);">
                              <option>Speakers (Default)</option>
                              <option>Headphones</option>
                          </select>
                      </div>
                      <div class="settings-item">
                          <span>Network Status</span>
                          <span>Connected (Ethernet)</span>
                      </div>
                      <div class="settings-item">
                          <span>Wallpaper</span>
                          <button id="changeWallpaperBtn" style="padding: 5px 10px; border-radius: 5px; background: var(--highlight); border: 1px solid var(--border-color); color: var(--text-color); cursor: pointer;">Change</button>
                      </div>
                  </div>
              `;
              break;
          case 'Admin Dashboard':
              content = `
                  <div class="dashboard-content" style="padding: 1rem;">
                      <h2 id="dashboardTitle">Admin Overview</h2>
                      <div class="dashboard-grid" id="dashboardGrid">
                          <div class="dashboard-card">
                              <h3>Active Users</h3>
                              <p id="activeUsers">...</p>
                          </div>
                          <div class="dashboard-card">
                              <h3>System Load</h3>
                              <p id="systemLoad">...</p>
                          </div>
                          <div class="dashboard-card">
                              <h3>Disk Usage</h3>
                              <p id="diskUsage">...</p>
                          </div>
                          <div class="dashboard-card">
                              <h3>Network Traffic</h3>
                              <p id="networkTraffic">...</p>
                          </div>
                      </div>
                      <h3 style="margin-top: 20px;">Recent Logs</h3>
                      <ul id="dashboardLogs" style="list-style: none; padding: 0; font-size: 0.9em; opacity: 0.9;"></ul>
                  </div>
              `;
              break;
          case 'Calculator':
              content = `
                  <div class="calculator-content">
                      <div class="calculator-display" id="calcDisplay">0</div>
                      <div class="calculator-keypad">
                          <button class="calculator-button operator" data-value="clear">AC</button>
                          <button class="calculator-button operator" data-value="backspace">⌫</button>
                          <button class="calculator-button operator" data-value="/">÷</button>
                          <button class="calculator-button operator" data-value="*">×</button>
                          <button class="calculator-button" data-value="7">7</button>
                          <button class="calculator-button" data-value="8">8</button>
                          <button class="calculator-button" data-value="9">9</button>
                          <button class="calculator-button operator" data-value="-">-</button>
                          <button class="calculator-button" data-value="4">4</button>
                          <button class="calculator-button" data-value="5">5</button>
                          <button class="calculator-button" data-value="6">6</button>
                          <button class="calculator-button operator" data-value="+">+</button>
                          <button class="calculator-button" data-value="1">1</button>
                          <button class="calculator-button" data-value="2">2</button>
                          <button class="calculator-button" data-value="3">3</button>
                          <button class="calculator-button equals" data-value="=">=</button>
                          <button class="calculator-button" data-value="0">0</button>
                          <button class="calculator-button" data-value=".">.</button>
                      </div>
                  </div>
              `;
              break;
          case 'About':
              content = `
                  <div style="padding: 1rem; text-align: center;">
                      <h2>About DarkCloud OS v5.0</h2>
                      <p>Built with pure HTML, CSS, and JavaScript.</p>
                      <p>This is a simulated operating system environment for demonstration purposes, now with full mobile and desktop support, enhanced applications, and persistent file storage via IndexedDB.</p>
                      <h3>Features</h3>
                      <ul style="list-style: none; padding: 0; text-align: left; max-width: 300px; margin: 0 auto;">
                        <li>✓ Responsive design for all screen sizes</li>
                        <li>✓ Functional Finder app with persistent file system</li>
                        <li>✓ Rich text Notes app with persistent storage</li>
                        <li>✓ File upload and download functionality</li>
                        <li>✓ Touch-based gestures (swipe down to minimize)</li>
                        <li>✓ Resizable windows and drag-and-drop on desktop</li>
                        <li>✓ Keyboard shortcuts for faster access</li>
                        <li>✓ Customizable themes and wallpapers</li>
                      </ul>
                      <p style="margin-top: 20px;">&copy; 2025 DarkCloud Inc.</p>
                  </div>
              `;
              break;
          // Start Menu
          case 'Start Menu':
              content = `
                  <div class="start-menu-content">
                    <div class="start-menu-search">
                      <input type="text" placeholder="Search apps..." id="startMenuSearch" />
                    </div>
                    <div class="start-menu-grid" id="startMenuGrid"></div>
                  </div>
              `;
              break;
          // Text Editor
          case 'Text Editor':
              content = `
                  <div class="text-editor-container">
                    <textarea id="textEditorArea" spellcheck="false"></textarea>
                  </div>
              `;
              break;
          // Paint
          case 'Paint':
              content = `
                  <div class="paint-container">
                    <canvas id="paintCanvas"></canvas>
                    <div class="paint-toolbar">
                      <button data-tool="pencil" class="active">Pencil</button>
                      <button data-tool="eraser">Eraser</button>
                      <input type="color" id="paintColor" value="#000000" />
                      <input type="range" id="brushSize" min="1" max="20" value="5" />
                    </div>
                  </div>
              `;
              break;
          // Browser
          case 'Browser':
              content = `
                  <div class="browser-container">
                    <div class="browser-toolbar">
                      <button id="browserBack">←</button>
                      <button id="browserForward">→</button>
                      <input type="text" id="browserUrl" placeholder="Enter URL..." />
                      <button id="browserGo">Go</button>
                    </div>
                    <iframe id="browserFrame"></iframe>
                  </div>
              `;
              break;
          default:
              content = `<div style="padding: 1rem;"><h2>${appName}</h2><p>This is the content for ${appName}.</p></div>`;
      }
      return content;
  }

  function createNewAppWindow(appName) {
    const appWindow = appWindowTemplate.cloneNode(true);
    appWindow.id = '';
    appWindow.style.display = 'flex';
    appWindow.querySelector('.app-title').textContent = appName;
    appWindow.querySelector('.app-content').innerHTML = getAppContent(appName);

    if (window.innerWidth <= 768) {
       appWindow.classList.add('maximized');
    } else {
      const randomX = Math.random() * (window.innerWidth * 0.8 - appWindow.offsetWidth) + window.innerWidth * 0.1;
      const randomY = Math.random() * (window.innerHeight * 0.8 - appWindow.offsetHeight) + window.innerHeight * 0.1;
      appWindow.style.top = `${randomY}px`;
      appWindow.style.left = `${randomX}px`;
    }

    desktop.appendChild(appWindow);
    bringWindowToFront(appWindow);
    setupWindowListeners(appWindow);

    activeWindows.set(appName, appWindow);
    initializeAppContent(appName, appWindow);

    return appWindow;
  }

  function initializeAppContent(appName, appWindow) {
    switch (appName) {
      case 'Terminal':
        setupTerminal(appWindow);
        break;
      case 'Finder':
        setupFinder(appWindow);
        break;
      case 'Admin Dashboard':
        generateDynamicDashboardData(appWindow);
        break;
      case 'Notes':
        setupNotes(appWindow);
        break;
      case 'Calculator':
        setupCalculator(appWindow);
        break;
      case 'Settings':
        setupSettings(appWindow);
        break;
      // JS-OS apps
      case 'Start Menu':
        setupStartMenu(appWindow);
        break;
      case 'Text Editor':
        setupTextEditor(appWindow);
        break;
      case 'Paint':
        setupPaint(appWindow);
        break;
      case 'Browser':
        setupBrowser(appWindow);
        break;
    }
  }

  function setupTerminal(appWindow) {
      const terminalOutput = appWindow.querySelector('#terminalOutput');
      const terminalInput = appWindow.querySelector('#terminalInput');
      terminalInput.focus();

      const commandHistory = [];
      let historyIndex = -1;
      const maxHistory = 20;

      terminalInput.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') {
              e.preventDefault();
              const command = terminalInput.value.trim();
              if (command) {
                  if (commandHistory.length >= maxHistory) {
                      commandHistory.shift();
                  }
                  commandHistory.push(command);
                  historyIndex = commandHistory.length;

                  const commandLine = document.createElement('p');
                  commandLine.textContent = `> ${command}`;
                  terminalOutput.insertBefore(commandLine, terminalInput.parentNode);

                  handleTerminalCommand(command, terminalOutput, terminalInput);
              }
              terminalInput.value = '';
          } else if (e.key === 'ArrowUp') {
              e.preventDefault();
              if (historyIndex > 0) {
                  historyIndex--;
                  terminalInput.value = commandHistory[historyIndex];
              }
          } else if (e.key === 'ArrowDown') {
              e.preventDefault();
              if (historyIndex < commandHistory.length - 1) {
                  historyIndex++;
                  terminalInput.value = commandHistory[historyIndex];
              } else {
                  historyIndex = commandHistory.length;
                  terminalInput.value = '';
              }
          }
      });
  }

  function handleTerminalCommand(command, outputElement, inputElement) {
      const outputLine = document.createElement('p');
      switch (command.toLowerCase()) {
          case 'help':
              outputLine.innerHTML = `
                  <p>Available Commands:</p>
                  <p> - help: Show this help message.</p>
                  <p> - clear: Clear the terminal screen.</p>
                  <p> - echo [message]: Display a message.</p>
                  <p> - whoami: Show current user.</p>
              `;
              break;
          case 'clear':
              Array.from(outputElement.children).forEach(child => {
                  if (child !== inputElement.parentNode) {
                      child.remove();
                  }
              });
              break;
          case 'whoami':
              outputLine.textContent = `> Current user: admin`;
              break;
          default:
              if (command.startsWith('echo ')) {
                  const message = command.substring(5);
                  outputLine.textContent = `> ${message}`;
              } else {
                  outputLine.textContent = `> Command not found: ${command}`;
              }
              break;
      }
      outputElement.insertBefore(outputLine, inputElement.parentNode);
      outputElement.scrollTop = outputElement.scrollHeight;
  }

  // Finder App Logic
  // Updated file system icons with local paths
  const fileSystemIcons = {
    'folder': 'icons/folder.svg',
    'file': 'icons/file.svg',
    'download': 'icons/download.svg'
  };

  let fileSystem = {
      'Documents': {
          type: 'folder',
          children: {}
      },
      'Downloads': {
          type: 'folder',
          children: {}
      },
      'System': {
          type: 'folder',
          children: {
              'settings.json': { type: 'file' },
          }
      }
  };

  let currentPath = [];

  function getPathReference(path) {
      let currentDir = fileSystem;
      for (const segment of path) {
          if (currentDir[segment] && currentDir[segment].type === 'folder') {
              currentDir = currentDir[segment].children;
          } else {
              return null;
          }
      }
      return currentDir;
  }

  async function loadFilesIntoFS() {
      try {
          const dbFiles = await getAllFilesFromDB();
          fileSystem['Documents'].children = {};
          
          dbFiles.forEach(fileRecord => {
              let pathSegments = fileRecord.path.split('/').filter(Boolean);
              let fileName = pathSegments.pop();
              let currentDir = fileSystem;

              for (const segment of pathSegments) {
                  if (!currentDir[segment] || currentDir[segment].type !== 'folder') {
                      currentDir[segment] = { type: 'folder', children: {} };
                  }
                  currentDir = currentDir[segment].children;
              }
              currentDir[fileName] = { type: 'file', dbPath: fileRecord.path, fileData: fileRecord.fileData };
          });
          const finderApp = activeWindows.get('Finder');
          if (finderApp) {
              renderFinder(finderApp);
          }
      } catch (e) {
          console.error('Failed to load files from IndexedDB:', e);
          showIsland('Error loading files');
      }
  }

  async function renderFinder(appWindow, filter = '') {
      const finderList = appWindow.querySelector('#finderList');
      const breadcrumb = appWindow.querySelector('#finderBreadcrumb');
      finderList.innerHTML = '';
      breadcrumb.innerHTML = '';

      // Breadcrumbs
      const homeSpan = document.createElement('span');
      homeSpan.textContent = 'Home';
      homeSpan.addEventListener('click', () => {
          currentPath = [];
          renderFinder(appWindow);
      });
      breadcrumb.appendChild(homeSpan);
      if (currentPath.length > 0) {
          for (const i in currentPath) {
              const segment = currentPath[i];
              const separator = document.createElement('span');
              separator.textContent = ' / ';
              breadcrumb.appendChild(separator);
              const pathSpan = document.createElement('span');
              pathSpan.textContent = segment;
              pathSpan.dataset.index = i;
              pathSpan.addEventListener('click', (e) => {
                  const newPath = currentPath.slice(0, parseInt(e.target.dataset.index) + 1);
                  currentPath = newPath;
                  renderFinder(appWindow);
              });
              breadcrumb.appendChild(pathSpan);
          }
      }

      const currentDir = getPathReference(currentPath);

      if (!currentDir) {
          finderList.innerHTML = `<li style="padding: 10px; opacity: 0.7;">Error: Directory not found.</li>`;
          return;
      }

      const items = Object.keys(currentDir).sort((a, b) => {
          const aType = currentDir[a].type;
          const bType = currentDir[b].type;
          if (aType === 'folder' && bType === 'file') return -1;
          if (aType === 'file' && bType === 'folder') return 1;
          return a.localeCompare(b);
      });

      items.filter(item => item.toLowerCase().includes(filter.toLowerCase()))
          .forEach(item => {
              const itemData = currentDir[item];
              const li = document.createElement('li');
              li.className = 'finder-item';
              li.dataset.name = item;
              li.dataset.type = itemData.type;

              let innerHTML = `
                  <div class="item-info">
                      <img src="${fileSystemIcons[itemData.type]}" alt="${itemData.type} icon" />
                      <span class="finder-item-name">${item}</span>
                  </div>
              `;
              if (itemData.type === 'file') {
                  innerHTML += `<button class="finder-download-btn" data-action="download" title="Download"><img src="${fileSystemIcons['download']}" /></button>`;
              }

              li.innerHTML = innerHTML;

              const downloadBtn = li.querySelector('.finder-download-btn');
              if (downloadBtn) {
                  downloadBtn.addEventListener('click', async (e) => {
                      e.stopPropagation();
                      await downloadFile(itemData.dbPath, itemData.fileData);
                  });
              }

              if (itemData.type === 'folder') {
                  li.addEventListener('click', () => {
                      currentPath.push(item);
                      renderFinder(appWindow);
                  });
              }
              
              // Context menu
              li.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                const finderContextMenu = appWindow.querySelector('#finderContextMenu');
                finderContextMenu.style.left = `${e.clientX}px`;
                finderContextMenu.style.top = `${e.clientY}px`;
                finderContextMenu.style.display = 'block';
                finderContextMenu.dataset.target = item;
                const downloadContextBtn = finderContextMenu.querySelector('#downloadContextBtn');
                if (itemData.type === 'file') {
                    downloadContextBtn.style.display = 'block';
                } else {
                    downloadContextBtn.style.display = 'none';
                }
              });
              li.addEventListener('touchstart', (e) => {
                const finderContextMenu = appWindow.querySelector('#finderContextMenu');
                clearTimeout(finderContextMenu.longPressTimeout);
                finderContextMenu.longPressTimeout = setTimeout(() => {
                  e.preventDefault();
                  finderContextMenu.style.left = `${e.touches[0].clientX}px`;
                  finderContextMenu.style.top = `${e.touches[0].clientY}px`;
                  finderContextMenu.style.display = 'block';
                  finderContextMenu.dataset.target = item;
                  const downloadContextBtn = finderContextMenu.querySelector('#downloadContextBtn');
                  if (itemData.type === 'file') {
                      downloadContextBtn.style.display = 'block';
                  } else {
                      downloadContextBtn.style.display = 'none';
                  }
                  vibrateDevice([50]);
                }, 500);
              });
              li.addEventListener('touchend', (e) => {
                const finderContextMenu = appWindow.querySelector('#finderContextMenu');
                clearTimeout(finderContextMenu.longPressTimeout);
              });
              li.addEventListener('touchmove', (e) => {
                const finderContextMenu = appWindow.querySelector('#finderContextMenu');
                clearTimeout(finderContextMenu.longPressTimeout);
              });

              finderList.appendChild(li);
          });

      if (finderList.children.length === 0) {
          finderList.innerHTML = `<li style="padding: 10px; opacity: 0.7;">No items found.</li>`;
      }
  }

  async function setupFinder(appWindow) {
      await loadFilesIntoFS();
      renderFinder(appWindow);

      const uploadFileBtn = appWindow.querySelector('#uploadFileBtn');
      const uploadFolderBtn = appWindow.querySelector('#uploadFolderBtn');
      const finderSearch = appWindow.querySelector('#finderSearch');
      const finderContextMenu = appWindow.querySelector('#finderContextMenu');
      const finderAiBtn = appWindow.querySelector('#finderAiBtn');
      const finderAiPanel = appWindow.querySelector('#finderAiPanel');
      const finderAiChatHistory = appWindow.querySelector('#finderAiChatHistory');
      const finderAiInput = appWindow.querySelector('#finderAiInput');
      const finderAiForm = appWindow.querySelector('#finderAiPanel .ai-input-form');
      const finderAiCloseBtn = appWindow.querySelector('#finderAiPanel .ai-close-btn');

      // Debounced search
      const debouncedRender = debounce((value) => {
        renderFinder(appWindow, value);
      }, 300);
      
      finderSearch.addEventListener('input', (e) => {
        debouncedRender(e.target.value);
      });

      // Ripple effects for buttons
      const buttons = appWindow.querySelectorAll('button');
      buttons.forEach(btn => {
        btn.addEventListener('mousedown', createRipple);
        btn.addEventListener('touchstart', createRipple);
      });

      uploadFileBtn.addEventListener('click', () => {
          fileInput.click();
      });
      fileInput.addEventListener('change', async (e) => {
          const file = e.target.files[0];
          if (file) {
              const path = [...currentPath, file.name].join('/');
              await saveFileToDB(file, path);
              await loadFilesIntoFS();
              showIsland(`File '${file.name}' uploaded.`);
          }
          fileInput.value = '';
      });

      uploadFolderBtn.addEventListener('click', () => {
          folderInput.click();
      });
      folderInput.addEventListener('change', async (e) => {
          const files = e.target.files;
          if (files.length > 0) {
              for (const file of files) {
                  const fullPath = file.webkitRelativePath.split('/').filter(Boolean).join('/');
                  const dbPath = [...currentPath, fullPath].join('/');
                  await saveFileToDB(file, dbPath);
              }
              await loadFilesIntoFS();
              showIsland(`Folder uploaded.`);
          }
          folderInput.value = '';
      });

      appWindow.addEventListener('click', (e) => {
          if (finderContextMenu) {
              finderContextMenu.style.display = 'none';
          }
      });

      // Context Menu logic
      finderContextMenu.addEventListener('click', async (e) => {
        const action = e.target.dataset.action;
        const targetName = finderContextMenu.dataset.target;
        const currentDir = getPathReference(currentPath);

        if (!currentDir) return;

        const fullPath = [...currentPath, targetName].join('/');

        switch(action) {
          case 'new-folder':
            const newFolderName = prompt('Enter new folder name:');
            if (newFolderName) {
              currentDir[newFolderName] = { type: 'folder', children: {} };
              renderFinder(appWindow);
              showIsland(`Folder '${newFolderName}' created.`);
            }
            break;
          case 'new-file':
            const newFileName = prompt('Enter new file name:');
            if (newFileName) {
              const emptyFile = new Blob([''], { type: 'text/plain' });
              const filePath = [...currentPath, newFileName].join('/');
              await saveFileToDB(emptyFile, filePath);
              await loadFilesIntoFS();
              showIsland(`File '${newFileName}' created.`);
            }
            break;
          case 'rename':
            const newName = prompt(`Rename '${targetName}' to:`);
            if (newName && newName !== targetName) {
                const oldFullPath = [...currentPath, targetName].join('/');
                const newFullPath = [...currentPath, newName].join('/');

                if (currentDir[targetName].type === 'file') {
                    const fileRecord = await getFileFromDB(oldFullPath);
                    if (fileRecord) {
                        fileRecord.path = newFullPath;
                        await saveFileToDB(fileRecord.fileData, newFullPath);
                        await deleteFileFromDB(oldFullPath);
                        showIsland(`File renamed to '${newName}'.`);
                    }
                } else if (currentDir[targetName].type === 'folder') {
                    async function renameRecursive(oldPrefix, newPrefix) {
                        const files = await getAllFilesFromDB();
                        const filesToRename = files.filter(f => f.path.startsWith(oldPrefix + '/'));

                        for (const file of filesToRename) {
                            const newPath = file.path.replace(oldPrefix, newPrefix);
                            file.path = newPath;
                            await saveFileToDB(file.fileData, newPath);
                            await deleteFileFromDB(file.path.replace(newPrefix, oldPrefix));
                        }
                    }
                    await renameRecursive(oldFullPath, newFullPath);
                    showIsland(`Folder renamed to '${newName}'.`);
                }

                await loadFilesIntoFS();
            }
            break;
          case 'delete':
            if (confirm(`Are you sure you want to delete '${targetName}'?`)) {
                if (currentDir[targetName].type === 'file') {
                    await deleteFileFromDB(fullPath);
                    showIsland(`File '${targetName}' deleted.`);
                } else if (currentDir[targetName].type === 'folder') {
                    const allFiles = await getAllFilesFromDB();
                    const filesToDelete = allFiles.filter(f => f.path.startsWith(fullPath + '/'));
                    for (const file of filesToDelete) {
                        await deleteFileFromDB(file.path);
                    }
                    showIsland(`Folder '${targetName}' deleted.`);
                }

                delete currentDir[targetName];
                await loadFilesIntoFS();
            }
            break;
          case 'download':
              const fileRecord = await getFileFromDB(fullPath);
              if (fileRecord) {
                  downloadFile(fileRecord.fileData, fileRecord.name);
                  showIsland(`Downloading '${fileRecord.name}'...`);
              }
              break;
        }
        finderContextMenu.style.display = 'none';
        vibrateDevice([10]);
      });

      // AI Assistant
      finderAiBtn.addEventListener('click', () => {
          finderAiPanel.classList.toggle('open');
          vibrateDevice([10]);
      });
      finderAiCloseBtn.addEventListener('click', () => {
          finderAiPanel.classList.remove('open');
      });

      finderAiForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          const userPrompt = finderAiInput.value.trim();
          if (!userPrompt) return;

          finderAiChatHistory.innerHTML += `<div class="ai-message user">${userPrompt}</div>`;
          finderAiChatHistory.scrollTop = finderAiChatHistory.scrollHeight;
          finderAiInput.value = '';

          const loadingMessage = document.createElement('div');
          loadingMessage.className = 'ai-message ai ai-loading';
          loadingMessage.textContent = 'Thinking...';
          finderAiChatHistory.appendChild(loadingMessage);
          finderAiChatHistory.scrollTop = finderAiChatHistory.scrollHeight;

          const allFiles = await getAllFilesFromDB();
          const fileListText = allFiles.map(f => `File: ${f.name} (Path: ${f.path})`).join('\n');
          const fullPrompt = `You are a helpful AI assistant for a file manager. Here is the list of files in the user's filesystem:\n\n${fileListText}\n\nUser request: ${userPrompt}`;

          const aiResponse = await getAIResponse(fullPrompt);

          loadingMessage.remove();
          finderAiChatHistory.innerHTML += `<div class="ai-message ai">${aiResponse}</div>`;
          finderAiChatHistory.scrollTop = finderAiChatHistory.scrollHeight;
      });
  }

  function downloadFile(fileData, fileName) {
      const url = URL.createObjectURL(fileData);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
  }

  function generateDynamicDashboardData(appWindow) {
      const activeUsers = appWindow.querySelector('#activeUsers');
      const systemLoad = appWindow.querySelector('#systemLoad');
      const diskUsage = appWindow.querySelector('#diskUsage');
      const networkTraffic = appWindow.querySelector('#networkTraffic');
      const dashboardLogs = appWindow.querySelector('#dashboardLogs');
      const dashboardTitle = appWindow.querySelector('#dashboardTitle');

      dashboardTitle.textContent = `Admin Overview - Refreshed at ${new Date().toLocaleTimeString()}`;

      activeUsers.textContent = (Math.floor(Math.random() * 5000) + 1000).toLocaleString();
      systemLoad.textContent = `${(Math.random() * 70 + 10).toFixed(1)}% CPU, ${(Math.random() * 80 + 10).toFixed(1)}% RAM`;
      diskUsage.textContent = `${(Math.random() * 50 + 50).toFixed(0)}% Full`;
      networkTraffic.textContent = `${(Math.random() * 5).toFixed(2)} TB (last 24h)`;

      const logs = [
          `User 'admin' logged in from 192.168.1.${Math.floor(Math.random() * 255)}`,
          `Service 'data_sync' started successfully`,
          `Warning: Disk space low on /dev/sda${Math.floor(Math.random() * 3) + 1}`,
          `System backup completed in ${(Math.random() * 5).toFixed(1)} minutes`,
          `Network firewall rules updated`,
      ];
      dashboardLogs.innerHTML = '';
      for (let i = 0; i < 5; i++) {
          const logEntry = document.createElement('li');
          logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${logs[Math.floor(Math.random() * logs.length)]}`;
          dashboardLogs.appendChild(logEntry);
      }
  }

  // Notes App Logic
  const notesPath = 'Documents/MyNote.html';

  async function setupNotes(appWindow) {
      const notesEditor = appWindow.querySelector('#notesEditor');
      const saveBtn = appWindow.querySelector('#notesSaveBtn');
      const toolbar = appWindow.querySelector('.notes-toolbar');
      const notesAiBtn = appWindow.querySelector('#notesAiBtn');
      const notesAiPanel = appWindow.querySelector('#notesAiPanel');
      const notesAiChatHistory = appWindow.querySelector('#notesAiChatHistory');
      const notesAiInput = appWindow.querySelector('#notesAiInput');
      const notesAiForm = appWindow.querySelector('#notesAiPanel .ai-input-form');
      const notesAiCloseBtn = appWindow.querySelector('#notesAiPanel .ai-close-btn');

      try {
          const savedNote = await getFileFromDB(notesPath);
          if (savedNote) {
              const text = await savedNote.fileData.text();
              notesEditor.innerHTML = text;
          } else {
              const emptyNote = new Blob(['<p>Start typing your note here...</p>'], { type: 'text/html' });
              await saveFileToDB(emptyNote, notesPath);
              notesEditor.innerHTML = await emptyNote.text();
              await loadFilesIntoFS();
          }
      } catch (error) {
          console.error('Failed to load note:', error);
          notesEditor.innerHTML = `<p style="color: red;">Error loading note. Please try again.</p>`;
      }

      saveBtn.addEventListener('click', async () => {
          const noteContent = new Blob([notesEditor.innerHTML], { type: 'text/html' });
          await saveFileToDB(noteContent, notesPath);
          showIsland('Notes saved to IndexedDB.');
      });

      let autosaveInterval = setInterval(async () => {
          const noteContent = new Blob([notesEditor.innerHTML], { type: 'text/html' });
          await saveFileToDB(noteContent, notesPath);
      }, 5000);

      appWindow.addEventListener('close', () => clearInterval(autosaveInterval));

      toolbar.addEventListener('click', (e) => {
          const command = e.target.dataset.command;
          if (command) {
              document.execCommand(command, false, null);
              notesEditor.focus();
              vibrateDevice([10]);
          }
      });

      // AI Assistant
      notesAiBtn.addEventListener('click', () => {
          notesAiPanel.classList.toggle('open');
          vibrateDevice([10]);
      });
      notesAiCloseBtn.addEventListener('click', () => {
          notesAiPanel.classList.remove('open');
      });

      notesAiForm.addEventListener('submit', async (e) => {
          e.preventDefault();
          const userPrompt = notesAiInput.value.trim();
          if (!userPrompt) return;

          notesAiChatHistory.innerHTML += `<div class="ai-message user">${userPrompt}</div>`;
          notesAiChatHistory.scrollTop = notesAiChatHistory.scrollHeight;
          notesAiInput.value = '';

          const loadingMessage = document.createElement('div');
          loadingMessage.className = 'ai-message ai ai-loading';
          loadingMessage.textContent = 'Thinking...';
          notesAiChatHistory.appendChild(loadingMessage);
          notesAiChatHistory.scrollTop = notesAiChatHistory.scrollHeight;

          const selection = window.getSelection();
          const selectedText = selection.toString();
          const fullContent = notesEditor.innerText;
          
          let prompt;
          if (selectedText) {
              prompt = `I am writing a note. I have selected the following text: "${selectedText}". My request is: ${userPrompt}. The full content of the note is: "${fullContent}"`;
          } else {
              prompt = `I am writing a note with the following content: "${fullContent}". My request is: ${userPrompt}`;
          }

          const aiResponse = await getAIResponse(prompt);

          loadingMessage.remove();
          notesAiChatHistory.innerHTML += `<div class="ai-message ai">${aiResponse}</div>`;
          notesAiChatHistory.scrollTop = notesAiChatHistory.scrollHeight;
      });
  }

  function setupCalculator(appWindow) {
      const display = appWindow.querySelector('#calcDisplay');
      const keypad = appWindow.querySelector('.calculator-keypad');
      let currentInput = '0';
      let operator = null;
      let firstOperand = null;
      let waitingForSecondOperand = false;

      function updateDisplay() {
          display.textContent = currentInput;
      }

      function handleNumber(number) {
          if (waitingForSecondOperand) {
              currentInput = number;
              waitingForSecondOperand = false;
          } else {
              currentInput = currentInput === '0' ? number : currentInput + number;
          }
      }

      function handleOperator(nextOperator) {
          const inputValue = parseFloat(currentInput);

          if (operator && waitingForSecondOperand) {
              operator = nextOperator;
              return;
          }

          if (firstOperand === null) {
              firstOperand = inputValue;
          } else if (operator) {
              const result = performCalculation[operator](firstOperand, inputValue);
              currentInput = `${parseFloat(result.toFixed(7))}`;
              firstOperand = result;
          }

          waitingForSecondOperand = true;
          operator = nextOperator;
      }

      const performCalculation = {
          '/': (first, second) => first / second,
          '*': (first, second) => first * second,
          '+': (first, second) => first + second,
          '-': (first, second) => first - second,
      };

      function resetCalculator() {
          currentInput = '0';
          operator = null;
          firstOperand = null;
          waitingForSecondOperand = false;
      }

      keypad.addEventListener('click', (e) => {
          const { value } = e.target.dataset;
          if (!value) return;
          vibrateDevice([10]);

          if (e.target.classList.contains('operator')) {
              if (value === 'clear') {
                  resetCalculator();
              } else if (value === 'backspace') {
                  currentInput = currentInput.slice(0, -1) || '0';
              } else if (value !== '=') {
                  handleOperator(value);
              }
          } else if (value === '=') {
              if (operator && !waitingForSecondOperand) {
                  handleOperator('=');
                  operator = null;
              }
          } else {
              handleNumber(value);
          }
          updateDisplay();
      });
  }

  function setupSettings(appWindow) {
      const darkModeToggle = appWindow.querySelector('#darkModeToggle');
      if (darkModeToggle) {
          darkModeToggle.checked = isDarkMode;
          darkModeToggle.addEventListener('change', (e) => {
              toggleDarkMode(e.target.checked);
              showIsland(`Dark mode ${e.target.checked ? 'on' : 'off'}`);
          });
      }

      const changeWallpaperBtn = appWindow.querySelector('#changeWallpaperBtn');
      if (changeWallpaperBtn) {
          changeWallpaperBtn.addEventListener('click', () => {
              changeWallpaper();
              showIsland('Wallpaper changed!');
              vibrateDevice([10]);
          });
      }
  }

  // Start Menu functionality
  function setupStartMenu(appWindow) {
    const grid = appWindow.querySelector('#startMenuGrid');
    grid.innerHTML = '';
    
    apps.forEach(app => {
      if (app.name === 'Start Menu') return;
      
      const appItem = document.createElement('div');
      appItem.className = 'start-menu-item';
      appItem.innerHTML = `
        <img src="${app.icon}" alt="${app.name}" />
        <span>${app.name}</span>
      `;
      appItem.addEventListener('click', () => {
        launchApp(app.name);
        appWindow.classList.add('minimized');
        vibrateDevice([10]);
      });
      grid.appendChild(appItem);
    });

    const searchInput = appWindow.querySelector('#startMenuSearch');
    searchInput.addEventListener('input', (e) => {
      const searchTerm = e.target.value.toLowerCase();
      const items = grid.querySelectorAll('.start-menu-item');
      
      items.forEach(item => {
        const appName = item.querySelector('span').textContent.toLowerCase();
        item.style.display = appName.includes(searchTerm) ? 'flex' : 'none';
      });
    });
  }

  // Text Editor App
  function setupTextEditor(appWindow) {
    const textArea = appWindow.querySelector('#textEditorArea');
    textArea.style.width = '100%';
    textArea.style.height = '100%';
    textArea.style.background = 'var(--highlight)';
    textArea.style.color = 'var(--text-color)';
    textArea.style.border = 'none';
    textArea.style.padding = '10px';
    textArea.style.fontFamily = 'monospace';
    textArea.focus();
  }

  // Paint App
  function setupPaint(appWindow) {
    const canvas = appWindow.querySelector('#paintCanvas');
    const ctx = canvas.getContext('2d');
    
    function resizeCanvas() {
      canvas.width = appWindow.offsetWidth;
      canvas.height = appWindow.offsetHeight - 50;
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    let tool = 'pencil';
    let color = '#000000';
    let brushSize = 5;
    
    canvas.addEventListener('mousedown', (e) => {
      isDrawing = true;
      [lastX, lastY] = [e.offsetX, e.offsetY];
    });
    
    canvas.addEventListener('mousemove', (e) => {
      if (!isDrawing) return;
      
      ctx.beginPath();
      ctx.moveTo(lastX, lastY);
      ctx.lineTo(e.offsetX, e.offsetY);
      ctx.strokeStyle = tool === 'eraser' ? 'var(--glass-bg)' : color;
      ctx.lineWidth = brushSize;
      ctx.lineCap = 'round';
      ctx.stroke();
      
      [lastX, lastY] = [e.offsetX, e.offsetY];
    });
    
    canvas.addEventListener('mouseup', () => isDrawing = false);
    canvas.addEventListener('mouseout', () => isDrawing = false);
    
    // Toolbar events
    appWindow.querySelectorAll('.paint-toolbar button').forEach(btn => {
      btn.addEventListener('click', () => {
        appWindow.querySelectorAll('.paint-toolbar button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        tool = btn.dataset.tool;
      });
    });
    
    appWindow.querySelector('#paintColor').addEventListener('change', (e) => {
      color = e.target.value;
    });
    
    appWindow.querySelector('#brushSize').addEventListener('input', (e) => {
      brushSize = e.target.value;
    });
  }

  // Browser App
  function setupBrowser(appWindow) {
    const browserFrame = appWindow.querySelector('#browserFrame');
    const urlInput = appWindow.querySelector('#browserUrl');
    const backBtn = appWindow.querySelector('#browserBack');
    const forwardBtn = appWindow.querySelector('#browserForward');
    const goBtn = appWindow.querySelector('#browserGo');
    
    browserFrame.style.width = '100%';
    browserFrame.style.height = 'calc(100% - 40px)';
    browserFrame.style.border = 'none';
    
    function navigate() {
      let url = urlInput.value;
      if (!url.startsWith('http')) {
        url = 'https://' + url;
      }
      browserFrame.src = url;
    }
    
    goBtn.addEventListener('click', navigate);
    urlInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') navigate();
    });
    
    backBtn.addEventListener('click', () => {
      try {
        browserFrame.contentWindow.history.back();
      } catch (e) {
        console.log('Cannot navigate back due to cross-origin restrictions');
      }
    });
    
    forwardBtn.addEventListener('click', () => {
      try {
        browserFrame.contentWindow.history.forward();
      } catch (e) {
        console.log('Cannot navigate forward due to cross-origin restrictions');
      }
    });
    
    browserFrame.addEventListener('load', () => {
      try {
        urlInput.value = browserFrame.contentWindow.location.href;
      } catch (e) {
        console.log('Cross-origin frame, cannot access URL');
      }
    });
    
    // Load initial page
    browserFrame.src = 'https://example.com';
  }

  function bringWindowToFront(windowElement) {
    currentZIndex++;
    windowElement.style.zIndex = currentZIndex;
    document.querySelectorAll('.app-window:not(#appWindowTemplate)').forEach(win => {
      win.style.boxShadow = '0 0.5rem 1.5rem rgba(0,0,0,0.4)';
      win.style.border = '1px solid var(--border-color)';
    });
    windowElement.style.boxShadow = 'var(--active-window-shadow)';
    windowElement.style.border = '1px solid var(--active-window-border)';
  }

  function setupWindowListeners(appWindow) {
    const appHeader = appWindow.querySelector('.app-header');
    const closeBtn = appWindow.querySelector('.close-btn');
    const minimizeBtn = appWindow.querySelector('.minimize-btn');
    const maximizeBtn = appWindow.querySelector('.maximize-btn');
    const appName = appWindow.querySelector('.app-title').textContent;
    const appContent = appWindow.querySelector('.app-content');

    closeBtn.addEventListener('click', () => {
      appWindow.classList.add('minimized');
      setTimeout(() => {
        appWindow.remove();
        activeWindows.delete(appName);
        showIsland(`${appName} closed`);
      }, 300);
    });

    minimizeBtn.addEventListener('click', () => {
      appWindow.classList.add('minimized');
      showIsland(`${appName} minimized`);
    });

    let originalSize = { width: '', height: '', top: '', left: '' };
    maximizeBtn.addEventListener('click', () => {
      if (appWindow.classList.contains('maximized')) {
        appWindow.style.width = originalSize.width;
        appWindow.style.height = originalSize.height;
        appWindow.style.top = originalSize.top;
        appWindow.style.left = originalSize.left;
        appWindow.style.transform = originalSize.transform;
        appWindow.style.borderRadius = originalSize.borderRadius;
        appWindow.classList.remove('maximized');
        showIsland(`${appName} restored`);
      } else {
        const rect = appWindow.getBoundingClientRect();
        originalSize = {
          width: `${rect.width}px`,
          height: `${rect.height}px`,
          top: `${rect.top}px`,
          left: `${rect.left}px`,
          transform: appWindow.style.transform,
          borderRadius: appWindow.style.borderRadius
        };
        appWindow.classList.add('maximized');
        showIsland(`${appName} maximized`);
      }
    });

    // Window dragging
    let isDragging = false, startX, startY, initialWindowX, initialWindowY;

    function startDrag(e) {
      if (appWindow.classList.contains('maximized') || window.innerWidth <= 768) return;
      isDragging = true;
      appHeader.classList.add('grabbing');
      bringWindowToFront(appWindow);
      const rect = appWindow.getBoundingClientRect();
      initialWindowX = rect.left;
      initialWindowY = rect.top;

      if (e.touches) {
          startX = e.touches[0].clientX;
          startY = e.touches[0].clientY;
      } else {
          startX = e.clientX;
          startY = e.clientY;
      }

      e.preventDefault();
    }

    function drag(e) {
        if (!isDragging) return;
        let currentX, currentY;
        if (e.touches) {
            currentX = e.touches[0].clientX;
            currentY = e.touches[0].clientY;
        } else {
            currentX = e.clientX;
            currentY = e.clientY;
        }

        const deltaX = currentX - startX;
        const deltaY = currentY - startY;

        let newLeft = initialWindowX + deltaX;
        let newTop = initialWindowY + deltaY;

        appWindow.style.left = `${newLeft}px`;
        appWindow.style.top = `${newTop}px`;
        appWindow.style.transform = 'none';
    }

    function endDrag() {
      isDragging = false;
      appHeader.classList.remove('grabbing');
    }

    appHeader.addEventListener('mousedown', startDrag);
    appHeader.addEventListener('touchstart', startDrag);
    document.addEventListener('mousemove', drag);
    document.addEventListener('touchmove', drag);
    document.addEventListener('mouseup', endDrag);
    document.addEventListener('touchend', endDrag);
    document.addEventListener('touchcancel', endDrag);

    appWindow.addEventListener('mousedown', () => bringWindowToFront(appWindow));
    appWindow.addEventListener('touchstart', () => bringWindowToFront(appWindow));

    // Swipe down to minimize on mobile
    let startSwipeY = 0;
    appContent.addEventListener('touchstart', (e) => {
      if (window.innerWidth > 768) return;
      startSwipeY = e.touches[0].clientY;
    });

    appContent.addEventListener('touchmove', (e) => {
      if (window.innerWidth > 768) return;
      const currentSwipeY = e.touches[0].clientY;
      if (currentSwipeY - startSwipeY > 100) {
        appWindow.classList.add('minimized');
        showIsland(`${appName} minimized`);
        vibrateDevice([50]);
        e.preventDefault();
      }
    });
  }

  function launchApp(name) {
    const existingWindow = activeWindows.get(name);
    if (existingWindow) {
      existingWindow.classList.remove('minimized');
      bringWindowToFront(existingWindow);
      showIsland(`${name} restored`);
    } else {
      createNewAppWindow(name);
      showIsland(`${name} launched`);
    }
  }

  function toggleDarkMode(forceState = null) {
    if (forceState !== null) {
      isDarkMode = forceState;
    } else {
      isDarkMode = !isDarkMode;
    }

    localStorage.setItem('isDarkMode', isDarkMode);

    if (isDarkMode) {
      desktop.classList.remove('light-mode');
      document.documentElement.style.setProperty('--glass-bg', 'rgba(0, 0, 0, 0.6)');
      document.documentElement.style.setProperty('--highlight', 'rgba(255, 255, 255, 0.1)');
      document.documentElement.style.setProperty('--border-color', '#334155');
      document.documentElement.style.setProperty('--text-color', 'white');
      document.documentElement.style.setProperty('background-color', '#0f172a');
      document.documentElement.style.setProperty('--terminal-text', '#00ff00');
    } else {
      desktop.classList.add('light-mode');
      document.documentElement.style.setProperty('--glass-bg', 'rgba(255, 255, 255, 0.85)');
      document.documentElement.style.setProperty('--highlight', 'rgba(0, 0, 0, 0.08)');
      document.documentElement.style.setProperty('--border-color', '#cbd5e1');
      document.documentElement.style.setProperty('--text-color', '#0f172a');
      document.documentElement.style.setProperty('background-color', '#f8fafc');
      document.documentElement.style.setProperty('--terminal-text', '#006400');
    }

    const settingsWindow = activeWindows.get('Settings');
    if (settingsWindow) {
      const darkModeToggle = settingsWindow.querySelector('#darkModeToggle');
      if (darkModeToggle) {
        darkModeToggle.checked = isDarkMode;
      }
    }
  }

  function changeWallpaper() {
      currentWallpaperIndex = (currentWallpaperIndex + 1) % wallpapers.length;
      setWallpaper(wallpapers[currentWallpaperIndex]);
      localStorage.setItem('wallpaperIndex', currentWallpaperIndex);
  }

  function setWallpaper(url) {
      desktop.style.backgroundImage = `url('${url}')`;
  }

  // Context menu handling
  let longPressTimeout;
  desktop.addEventListener('touchstart', (e) => {
    if (e.target.closest('.app-window, .dock') || window.innerWidth > 768) {
      return;
    }
    longPressTimeout = setTimeout(() => {
      e.preventDefault();
      contextMenu.style.left = `${e.touches[0].clientX}px`;
      contextMenu.style.top = `${e.touches[0].clientY}px`;
      contextMenu.style.display = 'block';
      vibrateDevice([50]);
    }, 500);
  });

  desktop.addEventListener('touchend', () => {
    clearTimeout(longPressTimeout);
  });
  desktop.addEventListener('touchmove', () => {
    clearTimeout(longPressTimeout);
  });
  desktop.addEventListener('touchcancel', () => {
    clearTimeout(longPressTimeout);
  });

  desktop.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    if (window.innerWidth <= 768) return;
    contextMenu.style.left = `${e.clientX}px`;
    contextMenu.style.top = `${e.clientY}px`;
    contextMenu.style.display = 'block';
  });

  document.addEventListener('click', (e) => {
    if (!contextMenu.contains(e.target)) {
      contextMenu.style.display = 'none';
    }
  });
  document.addEventListener('touchend', (e) => {
     if (!contextMenu.contains(e.target)) {
       contextMenu.style.display = 'none';
     }
  });

  contextMenu.addEventListener('click', (e) => {
      const action = e.target.dataset.action;
      if (action === 'launch-app') {
          launchApp(e.target.dataset.appName);
      } else if (action === 'toggle-dark-mode') {
          toggleDarkMode();
          showIsland(`Dark mode ${isDarkMode ? 'enabled' : 'disabled'}`);
      } else if (action === 'change-wallpaper') {
          changeWallpaper();
          showIsland('Wallpaper changed!');
      }
      contextMenu.style.display = 'none';
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
      if (e.ctrlKey && e.key === 'Escape') {
        e.preventDefault();
        launchApp('Start Menu');
      }
      if (e.ctrlKey && e.altKey && e.key === 't') {
          e.preventDefault();
          launchApp('Terminal');
      }
      if (e.ctrlKey && e.key === 'l') {
          e.preventDefault();
          toggleDarkMode();
          showIsland(`Dark mode ${isDarkMode ? 'enabled' : 'disabled'}`);
      }
  });

  window.addEventListener('resize', () => {
    document.querySelectorAll('.app-window:not(#appWindowTemplate)').forEach(appWindow => {
        if (window.innerWidth <= 768) {
            appWindow.classList.add('maximized');
        } else {
            appWindow.classList.remove('maximized');
        }
    });
  });

  document.addEventListener('DOMContentLoaded', async () => {
    await openDB();

    const savedDarkMode = localStorage.getItem('isDarkMode');
    isDarkMode = savedDarkMode ? JSON.parse(savedDarkMode) : true;
    const savedWallpaperIndex = localStorage.getItem('wallpaperIndex');
    currentWallpaperIndex = savedWallpaperIndex ? parseInt(savedWallpaperIndex) : 0;

    setWallpaper(wallpapers[currentWallpaperIndex]);
    toggleDarkMode(isDarkMode);

    // Restore session state
    restoreSessionState();
    
    // Auto-save session every 30 seconds
    setInterval(saveSessionState, 30000);

    createDockIcons();
    showIsland('Welcome to DarkCloud OS v5.0');
  });
})();

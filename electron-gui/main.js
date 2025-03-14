const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const Store = require('electron-store');
const { exec, spawn } = require('child_process');
const os = require('os');

// Cache for output results to avoid redundant processing
const processCache = new Map();

// Initialize settings store with schema validation
const store = new Store({
  schema: {
    windowBounds: {
      type: 'object',
      properties: {
        width: { type: 'number' },
        height: { type: 'number' },
        x: { type: 'number' },
        y: { type: 'number' }
      },
      default: { width: 1280, height: 800 }
    },
    lastSettings: { 
      type: 'object', 
      default: {
        outputWidth: 100,
        colorMode: 'ansi',
        dithering: false,
        edgeDetect: false,
        preset: 'classic',
        enhanceContrast: true,
        aspectRatioCorrection: 0.55,
        invert: false,
        edgeThreshold: 75,
        blur: 0,
        sharpen: 0,
        brightness: 1.0,
        saturation: 1.0,
        contrast: 1.0,
        detailLevel: 1.0,
        gamma: 1.0
      }
    },
    darkMode: { type: 'boolean', default: true },
    optimizeMemory: { type: 'boolean', default: true },
    systemPythonPath: { type: 'string' }
  },
  migrations: {
    // Add migrations for backward compatibility
    '2.0.0': (store) => {
      if (!store.has('optimizeMemory')) {
        store.set('optimizeMemory', true);
      }
    }
  }
});

// Keep a global reference of the window object to avoid garbage collection
let mainWindow;
let pythonProcess = null;

// Keep track of current processes
let activeProcesses = new Set();

function createWindow() {
  // Restore window dimensions from settings
  const { width, height, x, y } = store.get('windowBounds');
  
  // Create the browser window with modern styling
  mainWindow = new BrowserWindow({
    width: width,
    height: height,
    x: x,
    y: y,
    minWidth: 940,
    minHeight: 600,
    backgroundColor: '#1a1a1a',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
      webSecurity: false
    },
    // Use frameless window without additional title bar overlays
    frame: false,
    icon: path.join(__dirname, 'assets', 'icon.ico')
  });

  // Load the index.html of the app
  mainWindow.loadFile('src/index.html');

  // Save window position/size on close
  mainWindow.on('close', () => {
    store.set('windowBounds', mainWindow.getBounds());
  });

  // Clear the reference to the window object when closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Detect the best Python path to use
async function detectPythonPath() {
  // Check if we already have a stored path
  const storedPath = store.get('systemPythonPath');
  if (storedPath && await testPythonPath(storedPath)) {
    console.log(`Using stored Python path: ${storedPath}`);
    return storedPath;
  }
  
  // Try common Python commands
  const pythonCommands = ['python', 'python3', 'py'];
  
  for (const cmd of pythonCommands) {
    if (await testPythonPath(cmd)) {
      console.log(`Found working Python command: ${cmd}`);
      store.set('systemPythonPath', cmd);
      return cmd;
    }
  }
  
  // Try system-specific paths
  if (process.platform === 'win32') {
    // Windows common install locations
    const winPaths = [
      'C:\\Python311\\python.exe',
      'C:\\Python310\\python.exe',
      'C:\\Python39\\python.exe',
      'C:\\Python38\\python.exe',
      'C:\\Program Files\\Python311\\python.exe',
      'C:\\Program Files\\Python310\\python.exe',
      'C:\\Program Files\\Python39\\python.exe',
      'C:\\Program Files\\Python38\\python.exe'
    ];
    
    for (const pythonPath of winPaths) {
      if (fs.existsSync(pythonPath) && await testPythonPath(pythonPath)) {
        console.log(`Found working Python path: ${pythonPath}`);
        store.set('systemPythonPath', pythonPath);
        return pythonPath;
      }
    }
  } else {
    // Unix-like system paths
    const unixPaths = [
      '/usr/bin/python3',
      '/usr/local/bin/python3',
      '/opt/python3/bin/python3'
    ];
    
    for (const pythonPath of unixPaths) {
      if (fs.existsSync(pythonPath) && await testPythonPath(pythonPath)) {
        console.log(`Found working Python path: ${pythonPath}`);
        store.set('systemPythonPath', pythonPath);
        return pythonPath;
      }
    }
  }
  
  // Default fallback
  return 'python';
}

// Test if a Python path is valid
async function testPythonPath(pythonPath) {
  return new Promise((resolve) => {
    exec(`${pythonPath} --version`, (error, stdout, stderr) => {
      if (error) {
        resolve(false);
        return;
      }
      
      // Check if it's Python 3
      const output = stdout || stderr;
      if (output.includes('Python 3')) {
        resolve(true);
      } else {
        resolve(false);
      }
    });
  });
}

// Test the Python bridge script
async function testBridgeScript(pythonPath) {
  const bridgeScript = path.join(__dirname, 'python_bridge.py');
  
  return new Promise((resolve) => {
    exec(`${pythonPath} "${bridgeScript}" test`, (error, stdout, stderr) => {
      if (error) {
        console.error('Bridge script test error:', error);
        resolve(false);
        return;
      }
      
      try {
        const result = JSON.parse(stdout.trim());
        if (result && result.status === 'OK') {
          console.log('Bridge script test successful. Python version:', result.python_version);
          resolve(true);
        } else {
          console.error('Bridge script test returned unexpected result:', result);
          resolve(false);
        }
      } catch (err) {
        console.error('Bridge script test failed to parse output:', err);
        console.error('Raw output:', stdout);
        resolve(false);
      }
    });
  });
}

// Check Python environment with improved reliability
async function checkPythonEnvironment() {
  try {
    // Find the best Python path
    const pythonPath = await detectPythonPath();
    console.log(`Using Python path: ${pythonPath}`);
    
    const { projectRoot } = getPythonPath();
    
    console.log(`Checking Python environment using: ${pythonPath}`);
    
    // First check if Python works
    const result = await new Promise((resolve, reject) => {
      exec(`${pythonPath} -c "print('OK')"`, (error, stdout, stderr) => {
        if (error) {
          console.error('Python check error:', error);
          reject(error);
          return;
        }
        if (stderr) {
          console.error('Python check stderr:', stderr);
          reject(new Error(stderr));
          return;
        }
        resolve(stdout.trim());
      });
    });
    
    console.log('Python check result:', result);
    
    // For development, install in development mode if needed
    // Use the new PEP 517 compatible method if pyproject.toml exists
    if (!app.isPackaged) {
      const setupPath = path.join(projectRoot, 'setup.py');
      const pyprojectPath = path.join(projectRoot, 'pyproject.toml');
      
      if (fs.existsSync(pyprojectPath)) {
        console.log('In development mode, installing package using pyproject.toml');
        
        try {
          await new Promise((resolve, reject) => {
            const process = spawn(pythonPath, [
              '-m', 'pip', 'install', '-e', '.', 
              '--config-settings', 'editable_mode=compat'
            ], {
              cwd: projectRoot,
              shell: true
            });
            
            let stdout = '';
            let stderr = '';
            
            process.stdout.on('data', (data) => {
              stdout += data.toString();
            });
            
            process.stderr.on('data', (data) => {
              stderr += data.toString();
            });
            
            process.on('close', (code) => {
              console.log('Package install output:', stdout);
              if (stderr) {
                console.warn('Package install stderr:', stderr);
              }
              
              if (code !== 0) {
                console.warn(`Package install exited with code ${code}`);
              }
              
              resolve();
            });
            
            process.on('error', (err) => {
              console.error('Package install error:', err);
              reject(err);
            });
          });
        } catch (err) {
          console.warn('Failed to install package in development mode:', err);
          console.warn('Continuing despite package install error');
        }
      } else if (fs.existsSync(setupPath)) {
        // Fallback to legacy setup.py if pyproject.toml doesn't exist
        console.log('In development mode, installing package using setup.py');
        
        try {
          await new Promise((resolve, reject) => {
            const process = spawn(pythonPath, ['-m', 'pip', 'install', '-e', '.'], {
              cwd: projectRoot,
              shell: true
            });
            
            let stdout = '';
            let stderr = '';
            
            process.stdout.on('data', (data) => {
              stdout += data.toString();
            });
            
            process.stderr.on('data', (data) => {
              stderr += data.toString();
            });
            
            process.on('close', (code) => {
              console.log('Package install output:', stdout);
              if (stderr) {
                console.warn('Package install stderr:', stderr);
              }
              
              if (code !== 0) {
                console.warn(`Package install exited with code ${code}`);
              }
              
              resolve();
            });
            
            process.on('error', (err) => {
              console.error('Package install error:', err);
              reject(err);
            });
          });
        } catch (err) {
          console.warn('Failed to install package in development mode:', err);
          console.warn('Continuing despite package install error');
        }
      }
    }
    
    // Check if package is importable
    try {
      await new Promise((resolve, reject) => {
        exec(`${pythonPath} -c "import image2textart_generator; print('Package check OK')"`, 
          (error, stdout, stderr) => {
          if (error) {
            console.error('Package import error:', error);
            reject(error);
            return;
          }
          
          if (stderr) {
            console.warn('Package import stderr:', stderr);
          }
          
          if (stdout.includes('Package check OK')) {
            resolve(true);
          } else {
            reject(new Error('Package import check failed'));
          }
        });
      });
      
      console.log('Package import check successful');
      
      // Test the bridge script
      const bridgeOk = await testBridgeScript(pythonPath);
      if (!bridgeOk) {
        console.warn('Bridge script test failed, but continuing anyway');
      }
      
    } catch (err) {
      console.warn('Package import check failed:', err);
      console.warn('Continuing despite package import error');
    }
    
    if (result === 'OK') {
      return { success: true, pythonPath };
    } else {
      return { 
        success: false, 
        message: 'Python check failed: Unexpected response',
        pythonPath 
      };
    }
  } catch (error) {
    console.error('Python environment check failed:', error);
    return { 
      success: false, 
      message: `Python error: ${error.message}`,
      pythonPath: 'python'  // Default fallback
    };
  }
}

// Create the application window
app.whenReady().then(async () => {
  // Set app icon for taskbar
  if (process.platform === 'win32') {
    app.setAppUserModelId(process.execPath);
  }
  
  createWindow();
  
  // Check Python environment
  const pythonCheck = await checkPythonEnvironment();
  if (!pythonCheck.success) {
    dialog.showErrorBox('Python Environment Error', 
      `There was an error setting up the Python environment:\n\n${pythonCheck.message}\n\nPlease make sure Python is installed and the required files are in the correct location.`);
  }

  // On macOS, recreate window when dock icon is clicked and no windows are open
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// Quit when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
  // Kill any running Python processes
  for (const processId of activeProcesses) {
    try {
      process.kill(processId);
    } catch (e) {
      // Ignore errors - process might have already exited
    }
  }
  
  if (process.platform !== 'darwin') app.quit();
});

// Get path to the Python executable and scripts
function getPythonPath() {
  // In development mode, the script is in the parent directory
  // In production mode, the script is in the extraResources directory
  let projectRoot;
  
  if (app.isPackaged) {
    // Use path relative to executable in production
    projectRoot = process.resourcesPath;
  } else {
    // Use path relative to project root in development
    projectRoot = path.join(__dirname, '..');
  }
  
  const bridgeScript = path.join(__dirname, 'python_bridge.py');
  console.log('Bridge script path:', bridgeScript);
  console.log('Project root path:', projectRoot);
  
  return {
    pythonPath: store.get('systemPythonPath', 'python'),
    bridgeScript: bridgeScript,
    projectRoot: projectRoot
  };
}

// Generate a cache key for a specific image and settings
function getCacheKey(imagePath, settings) {
  // Create a hash of the settings
  const settingsString = JSON.stringify(settings);
  return `${imagePath}:${settingsString}`;
}

// Process image with Python using the bridge script
ipcMain.handle('process-image', async (event, imagePath, settings) => {
  return new Promise(async (resolve, reject) => {
    // Check if we have a cached result
    const cacheKey = getCacheKey(imagePath, settings);
    if (processCache.has(cacheKey)) {
      console.log('Using cached result for', imagePath);
      return resolve(processCache.get(cacheKey));
    }
    
    // Get Python paths
    const { pythonPath, bridgeScript, projectRoot } = getPythonPath();
    
    // Ensure bridge script exists
    if (!fs.existsSync(bridgeScript)) {
      return reject(new Error(`Bridge script not found: ${bridgeScript}`));
    }
    
    // Check if image exists
    if (!fs.existsSync(imagePath)) {
      return reject(new Error(`Image file not found: ${imagePath}`));
    }
    
    // Create a temporary output file
    const tmpDir = path.join(app.getPath('temp'), 'ansi-ascii-art-generator');
    if (!fs.existsSync(tmpDir)) {
      fs.mkdirSync(tmpDir, { recursive: true });
    }
    const outputFile = path.join(tmpDir, `output-${Date.now()}.txt`);
    
    // Build arguments array for the bridge script
    const args = [
      bridgeScript,
      'generate',
      imagePath,
      '--output', outputFile,
      '--width', settings.outputWidth.toString(),
      '--color', settings.colorMode,
      '--preset', settings.preset,
      '--edge-threshold', settings.edgeThreshold.toString(),
      '--aspect-ratio', settings.aspectRatioCorrection.toString(),
      '--blur', settings.blur.toString(),
      '--sharpen', settings.sharpen.toString(),
      '--brightness', settings.brightness.toString(),
      '--saturation', settings.saturation.toString(),
      '--contrast', settings.contrast.toString(),
      '--detail-level', settings.detailLevel.toString(),
      '--gamma', settings.gamma.toString()
    ];
    
    // Add memory optimization if enabled
    if (store.get('optimizeMemory', true)) {
      args.push('--optimize-for', 'memory');
      args.push('--max-image-size', '2000');
    }
    
    // Add optional boolean flags
    if (settings.dithering) args.push('--dither');
    if (settings.edgeDetect) args.push('--edges');
    if (!settings.enhanceContrast) args.push('--no-enhance');
    if (settings.invert) args.push('--invert');
    
    // Set up environment variables
    const env = Object.assign({}, process.env);
    // Set PYTHONPATH to the project root to help find the package
    env.PYTHONPATH = projectRoot;
    // Force Python to use UTF-8 for stdout/stderr
    env.PYTHONIOENCODING = 'utf-8';
    
    console.log('Running Python command:', pythonPath, args.join(' '));
    
    // Save the last used settings
    store.set('lastSettings', settings);
    
    // Use spawn for better performance and progress information
    const pythonProcess = spawn(pythonPath, args, { 
      env,
      // Increase max buffer size for large outputs
      maxBuffer: 50 * 1024 * 1024 // 50 MB
    });
    
    // Add to active processes
    activeProcesses.add(pythonProcess.pid);
    
    // Listen for progress information
    let stderrData = '';
    
    // Monitor stderr for potential errors
    pythonProcess.stderr.on('data', (data) => {
      stderrData += data.toString();
      console.error('Python stderr:', data.toString());
      
      // Send progress updates to the renderer
      if (data.toString().includes('Progress:')) {
        event.sender.send('process-progress', {
          progress: data.toString().trim()
        });
      }
    });
    
    // When the process completes
    pythonProcess.on('close', (code) => {
      // Remove from active processes
      activeProcesses.delete(pythonProcess.pid);
      
      if (code !== 0) {
        console.error(`Python process exited with code ${code}`);
        console.error('Full stderr output:', stderrData);
        reject(new Error(`Python error: ${stderrData || 'Unknown error'}`));
      } else {
        // Read the output file instead of relying on stdout
        try {
          console.log(`Reading output from file: ${outputFile}`);
          const result = fs.readFileSync(outputFile, { encoding: 'utf8' });
          
          // Cache the result for future use
          processCache.set(cacheKey, result);
          
          // Limit cache size
          if (processCache.size > 10) {
            // Remove oldest entries
            const keys = Array.from(processCache.keys());
            for (let i = 0; i < keys.length - 10; i++) {
              processCache.delete(keys[i]);
            }
          }
          
          // Cleanup the temp file
          try { fs.unlinkSync(outputFile); } catch (e) { /* ignore cleanup errors */ }
          
          resolve(result);
        } catch (err) {
          console.error('Error reading output file:', err);
          reject(new Error(`Failed to read output file: ${err.message}`));
        }
      }
    });
    
    // Handle process errors
    pythonProcess.on('error', (err) => {
      console.error('Failed to start Python process:', err);
      activeProcesses.delete(pythonProcess.pid);
      reject(new Error(`Failed to start Python process: ${err.message}`));
    });
  });
});

// IPC handlers for renderer communication
ipcMain.handle('select-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Images', extensions: ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'] }
    ]
  });
  
  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

ipcMain.handle('save-file', async (event, defaultPath, content) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: defaultPath,
    filters: [
      { name: 'Text Files', extensions: ['txt'] },
      { name: 'HTML Files', extensions: ['html'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  
  if (!result.canceled && result.filePath) {
    fs.writeFileSync(result.filePath, content);
    return result.filePath;
  }
  return null;
});

// Get settings
ipcMain.handle('get-settings', () => {
  return {
    lastSettings: store.get('lastSettings'),
    darkMode: store.get('darkMode'),
    optimizeMemory: store.get('optimizeMemory', true)
  };
});

// Save settings
ipcMain.handle('save-settings', (event, settings) => {
  store.set('lastSettings', settings);
  return true;
});

// Toggle dark mode
ipcMain.handle('toggle-dark-mode', (event, isDark) => {
  store.set('darkMode', isDark);
  return isDark;
});

// Toggle memory optimization
ipcMain.handle('toggle-memory-optimization', (event, isOptimized) => {
  store.set('optimizeMemory', isOptimized);
  return isOptimized;
});

// Window control handlers
ipcMain.handle('minimize-window', () => {
  mainWindow.minimize();
});

ipcMain.handle('maximize-window', () => {
  if (mainWindow.isMaximized()) {
    mainWindow.unmaximize();
    return false;
  } else {
    mainWindow.maximize();
    return true;
  }
});

ipcMain.handle('close-window', () => {
  mainWindow.close();
});

// Open URLs in default browser
ipcMain.handle('open-external-url', (event, url) => {
  shell.openExternal(url);
});

// Get character presets using the bridge script
ipcMain.handle('get-character-presets', async () => {
  const { pythonPath, bridgeScript, projectRoot } = getPythonPath();
  
  return new Promise((resolve, reject) => {
    // Ensure bridge script exists
    if (!fs.existsSync(bridgeScript)) {
      console.error(`Bridge script not found: ${bridgeScript}`);
      // Return empty array instead of rejecting to avoid crashing
      return resolve([]);
    }
    
    // Set up environment variables
    const env = Object.assign({}, process.env);
    // Set PYTHONPATH to the project root
    env.PYTHONPATH = projectRoot;
    // Force Python to use UTF-8 for stdout/stderr
    env.PYTHONIOENCODING = 'utf-8';
    
    console.log('Getting character presets using bridge script');
    
    // Use spawn with the bridge script
    const pythonProcess = spawn(pythonPath, [bridgeScript, 'get_presets'], { env });
    
    let stdoutData = '';
    let stderrData = '';
    
    pythonProcess.stdout.on('data', (data) => {
      stdoutData += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      stderrData += data.toString();
      console.error('Python stderr:', data.toString());
    });
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`Python process exited with code ${code}`);
        console.error('Full stderr output:', stderrData);
        // Return empty array instead of rejecting to avoid crashing
        resolve([]);
      } else {
        try {
          // Try to parse the JSON output
          const result = JSON.parse(stdoutData.trim());
          resolve(result);
        } catch (err) {
          console.error('Error parsing JSON output:', err);
          console.error('Raw output:', stdoutData);
          // Return empty array on parse error
          resolve([]);
        }
      }
    });
    
    pythonProcess.on('error', (err) => {
      console.error('Failed to start Python process:', err);
      // Return empty array instead of rejecting to avoid crashing
      resolve([]);
    });
  });
});

// Get image info
ipcMain.handle('get-image-info', async (event, imagePath) => {
  if (!fs.existsSync(imagePath)) {
    return { error: 'File not found' };
  }
  
  try {
    // Read image dimensions using the image-size module
    const sizeOf = require('image-size');
    const dimensions = sizeOf(imagePath);
    
    // Get file details
    const stats = fs.statSync(imagePath);
    const fileSizeInBytes = stats.size;
    const fileSizeInMB = fileSizeInBytes / (1024 * 1024);
    
    return {
      width: dimensions.width,
      height: dimensions.height,
      type: dimensions.type,
      size: {
        bytes: fileSizeInBytes,
        megabytes: fileSizeInMB.toFixed(2)
      },
      needsOptimization: fileSizeInMB > 5 || dimensions.width > 3000 || dimensions.height > 3000
    };
  } catch (err) {
    console.error('Error getting image info:', err);
    return { error: err.message };
  }
});

// Auto-suggest optimal settings using the bridge script
ipcMain.handle('suggest-optimal-settings', async (event, imagePath) => {
  if (!fs.existsSync(imagePath)) {
    return { success: false, error: 'File not found' };
  }
  
  const { pythonPath, bridgeScript, projectRoot } = getPythonPath();
  
  return new Promise((resolve, reject) => {
    // Set up environment variables
    const env = Object.assign({}, process.env);
    env.PYTHONPATH = projectRoot;
    env.PYTHONIOENCODING = 'utf-8';
    
    console.log('Getting optimal settings using bridge script');
    
    // Use spawn with bridge script
    const pythonProcess = spawn(pythonPath, [bridgeScript, 'suggest_settings', imagePath, '100'], { env });
    
    let stdoutData = '';
    let stderrData = '';
    
    pythonProcess.stdout.on('data', (data) => {
      stdoutData += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      stderrData += data.toString();
    });
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`Python process exited with code ${code}`);
        console.error('Full stderr output:', stderrData);
        resolve({ success: false, error: stderrData || 'Unknown error' });
        return;
      }
      
      try {
        // Try to parse the JSON output
        const result = JSON.parse(stdoutData.trim());
        resolve({ success: true, settings: result });
      } catch (err) {
        console.error('Error parsing JSON output:', err);
        console.error('Raw output:', stdoutData);
        
        // Fallback to regex parsing of output if JSON parsing fails
        const settings = {};
        const output = stdoutData + stderrData;
        
        // Extract settings from output
        const widthMatch = output.match(/Width: (\d+)/);
        if (widthMatch) settings.outputWidth = parseInt(widthMatch[1]);
        
        const colorMatch = output.match(/Color mode: (\w+)/);
        if (colorMatch) settings.colorMode = colorMatch[1];
        
        const presetMatch = output.match(/Character preset: (\w+)/);
        if (presetMatch) settings.preset = presetMatch[1];
        
        const ditheringMatch = output.match(/Dithering: (enabled|disabled)/);
        if (ditheringMatch) settings.dithering = ditheringMatch[1] === 'enabled';
        
        const edgeMatch = output.match(/Edge detection: (enabled|disabled)/);
        if (edgeMatch) settings.edgeDetect = edgeMatch[1] === 'enabled';
        
        // If we found at least some settings, consider it a success
        if (Object.keys(settings).length > 0) {
          resolve({ success: true, settings });
        } else {
          resolve({ success: false, error: 'Could not parse settings' });
        }
      }
    });
    
    pythonProcess.on('error', (err) => {
      console.error('Failed to start Python process:', err);
      resolve({ success: false, error: err.message });
    });
  });
});

// Clear cache
ipcMain.handle('clear-cache', () => {
  processCache.clear();
  return true;
});

// Get system info
ipcMain.handle('get-system-info', () => {
  return {
    platform: process.platform,
    arch: process.arch,
    version: app.getVersion(),
    electronVersion: process.versions.electron,
    chromeVersion: process.versions.chrome,
    nodeVersion: process.versions.node,
    cpus: os.cpus().length,
    memory: {
      total: Math.round(os.totalmem() / (1024 * 1024 * 1024)),  // GB
      free: Math.round(os.freemem() / (1024 * 1024 * 1024))    // GB
    }
  };
});
